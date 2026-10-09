"""
vault.py - Cryptographic Storage Engine for Secure Daily Diary

Security Specifications:
- Encryption: AES-256-GCM (Authenticated Encryption with Associated Data).
- Key Derivation: PBKDF2-HMAC-SHA256 with 600,000 iterations (OWASP recommendation).
- Salt: Cryptographically secure 32-byte random salt per vault.
- Nonce: Cryptographically secure unique 12-byte random nonce per encrypted entry.
- Privacy at Rest: Entry identifiers stored in SQLite are HMAC-SHA256 tokens derived
  from the date using the master key. Without the master password, an observer inspecting
  the database cannot determine entry dates, titles, content, moods, or tags.
- Integrity: AES-GCM authentication tags guarantee tamper detection.
"""

from __future__ import annotations

import datetime
import hashlib
import hmac
import json
import os
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class DiaryVaultError(Exception):
    """Base exception for Diary Vault operations."""
    pass


class VaultLockedError(DiaryVaultError):
    """Raised when an operation requiring an unlocked vault is attempted while locked."""
    pass


class InvalidPasswordError(DiaryVaultError):
    """Raised when an incorrect password is provided."""
    pass


class VaultAlreadyExistsError(DiaryVaultError):
    """Raised when attempting to initialize a vault that already exists."""
    pass


class VaultNotFoundError(DiaryVaultError):
    """Raised when attempting to unlock a vault that does not exist."""
    pass


AUTH_MAGIC = b"SECURE_DIARY_AUTH_OK_V1"
AUTH_AAD = b"secure_diary_auth"
ENTRY_AAD = b"secure_diary_entry"
DEFAULT_ITERATIONS = 600_000
SALT_SIZE = 32
NONCE_SIZE = 12


def get_default_vault_path() -> Path:
    """Return the default local path for the diary vault database."""
    env_path = os.environ.get("SECURE_DIARY_DB")
    if env_path:
        return Path(env_path).expanduser().resolve()
    
    # Follow XDG Base Directory specification
    data_home = os.environ.get("XDG_DATA_HOME")
    if data_home:
        base_dir = Path(data_home) / "secure_diary"
    else:
        base_dir = Path.home() / ".local" / "share" / "secure_diary"
    
    base_dir.mkdir(parents=True, exist_ok=True)
    return base_dir / "diary_vault.db"


class DiaryVault:
    """Manages the encrypted local SQLite database for daily diary entries."""

    def __init__(self, db_path: Optional[Path | str] = None):
        if db_path is None:
            self.db_path = get_default_vault_path()
        else:
            self.db_path = Path(db_path).expanduser().resolve()
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self._key: Optional[bytes] = None
        self._cached_entries: Dict[str, Dict[str, Any]] = {}
        self._salt: Optional[bytes] = None
        self._iterations: int = DEFAULT_ITERATIONS

    @property
    def is_unlocked(self) -> bool:
        """Return True if the vault is currently unlocked and key is in memory."""
        return self._key is not None

    def exists(self) -> bool:
        """Check whether the vault database exists and has been initialized."""
        if not self.db_path.exists() or self.db_path.stat().st_size == 0:
            return False
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT 1 FROM sqlite_master WHERE type='table' AND name='vault_meta'"
                )
                if not cursor.fetchone():
                    return False
                cursor.execute("SELECT COUNT(*) FROM vault_meta WHERE key='auth_verifier'")
                count = cursor.fetchone()[0]
                return count > 0
        except Exception:
            return False

    def _derive_key(self, password: str, salt: bytes, iterations: int) -> bytes:
        """Derive a 256-bit symmetric encryption key from the password."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=iterations,
        )
        return kdf.derive(password.encode("utf-8"))

    def _compute_date_token(self, date_str: str) -> str:
        """
        Compute an HMAC of the date string using the master key.
        This provides deterministic indexed lookup without leaking the plain date to disk.
        """
        if not self._key:
            raise VaultLockedError("Vault is locked")
        return hmac.new(self._key, date_str.encode("utf-8"), hashlib.sha256).hexdigest()

    def initialize_vault(self, master_password: str) -> None:
        """
        Initialize a new encrypted diary vault with the given master password.
        Raises VaultAlreadyExistsError if the vault already exists.
        """
        if not master_password:
            raise ValueError("Master password cannot be empty")
        
        if self.exists():
            raise VaultAlreadyExistsError(f"Vault already exists at {self.db_path}")

        salt = os.urandom(SALT_SIZE)
        iterations = DEFAULT_ITERATIONS
        key = self._derive_key(master_password, salt, iterations)

        # Encrypt the authentication verifier
        aesgcm = AESGCM(key)
        verifier_nonce = os.urandom(NONCE_SIZE)
        verifier_ciphertext = aesgcm.encrypt(verifier_nonce, AUTH_MAGIC, AUTH_AAD)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS vault_meta (
                    key TEXT PRIMARY KEY,
                    value BLOB NOT NULL
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS entries (
                    date_token TEXT PRIMARY KEY,
                    nonce BLOB NOT NULL,
                    ciphertext BLOB NOT NULL,
                    updated_at REAL NOT NULL
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
            """)

            cursor.execute("INSERT OR REPLACE INTO vault_meta (key, value) VALUES ('version', ?)", (b"1",))
            cursor.execute("INSERT OR REPLACE INTO vault_meta (key, value) VALUES ('salt', ?)", (salt,))
            cursor.execute("INSERT OR REPLACE INTO vault_meta (key, value) VALUES ('iterations', ?)", (str(iterations).encode("utf-8"),))
            
            verifier_blob = verifier_nonce + verifier_ciphertext
            cursor.execute("INSERT OR REPLACE INTO vault_meta (key, value) VALUES ('auth_verifier', ?)", (verifier_blob,))
            cursor.execute(
                "INSERT OR REPLACE INTO vault_meta (key, value) VALUES ('created_at', ?)",
                (datetime.datetime.now().isoformat().encode("utf-8"),)
            )
            
            # Default settings
            cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('auto_lock_minutes', '5')")
            conn.commit()

        self._key = key
        self._salt = salt
        self._iterations = iterations
        self._cached_entries.clear()

    def unlock(self, master_password: str) -> bool:
        """
        Unlock the vault using the master password.
        Returns True on success, or raises InvalidPasswordError if password is incorrect.
        """
        if not self.exists():
            raise VaultNotFoundError(f"Vault not found at {self.db_path}")

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT key, value FROM vault_meta")
            rows = dict(cursor.fetchall())

        salt = rows.get("salt")
        iterations_bytes = rows.get("iterations")
        verifier_blob = rows.get("auth_verifier")

        if not salt or not verifier_blob:
            raise DiaryVaultError("Corrupted vault metadata")

        iterations = int(iterations_bytes.decode("utf-8")) if iterations_bytes else DEFAULT_ITERATIONS
        key = self._derive_key(master_password, salt, iterations)

        # Validate password against verifier blob
        verifier_nonce = verifier_blob[:NONCE_SIZE]
        verifier_ciphertext = verifier_blob[NONCE_SIZE:]
        aesgcm = AESGCM(key)

        try:
            decrypted_magic = aesgcm.decrypt(verifier_nonce, verifier_ciphertext, AUTH_AAD)
            if decrypted_magic != AUTH_MAGIC:
                raise InvalidPasswordError("Password verification failed")
        except InvalidTag:
            raise InvalidPasswordError("Incorrect master password")

        self._key = key
        self._salt = salt
        self._iterations = iterations
        self._load_and_cache_entries()
        return True

    def lock(self) -> None:
        """Lock the vault, immediately clearing the key and decrypted cache from memory."""
        self._key = None
        self._cached_entries.clear()

    def _require_unlocked(self) -> None:
        if not self.is_unlocked:
            raise VaultLockedError("Vault is currently locked. Please unlock it first.")

    def _load_and_cache_entries(self) -> None:
        """Decrypt all entries from database into memory cache."""
        self._require_unlocked()
        self._cached_entries.clear()

        aesgcm = AESGCM(self._key)  # type: ignore

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT date_token, nonce, ciphertext, updated_at FROM entries")
            rows = cursor.fetchall()

        for date_token, nonce, ciphertext, updated_at in rows:
            try:
                plaintext_bytes = aesgcm.decrypt(nonce, ciphertext, ENTRY_AAD)
                entry_data = json.loads(plaintext_bytes.decode("utf-8"))
                date_str = entry_data.get("date")
                if date_str:
                    self._cached_entries[date_str] = entry_data
            except Exception as e:
                # Log error or skip corrupted entry
                continue

    def save_entry(
        self,
        date_str: str,
        title: str,
        content: str,
        mood: str = "",
        tags: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Encrypt and save a diary entry for the specified date (YYYY-MM-DD).
        Updates cache and database atomically.
        """
        self._require_unlocked()
        
        # Validate date format YYYY-MM-DD
        try:
            datetime.date.fromisoformat(date_str)
        except ValueError:
            raise ValueError(f"Invalid date format '{date_str}', expected YYYY-MM-DD")

        tags_clean = [t.strip() for t in (tags or []) if t.strip()]
        now_iso = datetime.datetime.now().isoformat()
        
        existing = self._cached_entries.get(date_str)
        created_at = existing.get("created_at", now_iso) if existing else now_iso

        entry_data: Dict[str, Any] = {
            "date": date_str,
            "title": title.strip(),
            "content": content,
            "mood": mood.strip(),
            "tags": tags_clean,
            "created_at": created_at,
            "updated_at": now_iso,
        }

        # Encrypt with AES-256-GCM
        payload_bytes = json.dumps(entry_data, ensure_ascii=False).encode("utf-8")
        nonce = os.urandom(NONCE_SIZE)
        aesgcm = AESGCM(self._key)  # type: ignore
        ciphertext = aesgcm.encrypt(nonce, payload_bytes, ENTRY_AAD)

        date_token = self._compute_date_token(date_str)
        timestamp = datetime.datetime.now().timestamp()

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO entries (date_token, nonce, ciphertext, updated_at)
                VALUES (?, ?, ?, ?)
            """, (date_token, nonce, ciphertext, timestamp))
            conn.commit()

        self._cached_entries[date_str] = entry_data
        return entry_data

    def get_entry(self, date_str: str) -> Optional[Dict[str, Any]]:
        """Retrieve the decrypted entry for the given date, or None if not found."""
        self._require_unlocked()
        return self._cached_entries.get(date_str)

    def delete_entry(self, date_str: str) -> bool:
        """Delete entry for the given date. Returns True if deleted, False if not found."""
        self._require_unlocked()
        if date_str not in self._cached_entries:
            return False

        date_token = self._compute_date_token(date_str)
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM entries WHERE date_token = ?", (date_token,))
            conn.commit()

        del self._cached_entries[date_str]
        return True

    def get_all_entries(self, reverse: bool = True) -> List[Dict[str, Any]]:
        """Return all decrypted entries, sorted by date (newest first if reverse=True)."""
        self._require_unlocked()
        entries = list(self._cached_entries.values())
        entries.sort(key=lambda e: e.get("date", ""), reverse=reverse)
        return entries

    def get_entry_dates(self) -> Set[str]:
        """Return the set of all dates (YYYY-MM-DD) that have diary entries."""
        self._require_unlocked()
        return set(self._cached_entries.keys())

    def search_entries(self, query: str) -> List[Dict[str, Any]]:
        """
        Search entries across title, content, mood, tags, and date.
        Returns matching entries sorted by date descending.
        """
        self._require_unlocked()
        q = query.strip().lower()
        if not q:
            return self.get_all_entries()

        matches = []
        for entry in self._cached_entries.values():
            title = entry.get("title", "").lower()
            content = entry.get("content", "").lower()
            date = entry.get("date", "").lower()
            mood = entry.get("mood", "").lower()
            tags = " ".join(entry.get("tags", [])).lower()

            if q in title or q in content or q in date or q in mood or q in tags:
                matches.append(entry)

        matches.sort(key=lambda e: e.get("date", ""), reverse=True)
        return matches

    def change_password(self, old_password: str, new_password: str) -> None:
        """
        Re-encrypt the entire vault with a new master password.
        Uses a fresh salt and generates new nonces for every single entry in an atomic transaction.
        """
        self._require_unlocked()
        if not new_password:
            raise ValueError("New password cannot be empty")

        # Verify old password
        old_salt = self._salt
        old_iterations = self._iterations
        if old_salt is None:
            raise VaultLockedError("Vault is not properly unlocked")
        
        old_test_key = self._derive_key(old_password, old_salt, old_iterations)
        if old_test_key != self._key:
            raise InvalidPasswordError("Current password is incorrect")

        new_salt = os.urandom(SALT_SIZE)
        new_iterations = DEFAULT_ITERATIONS
        new_key = self._derive_key(new_password, new_salt, new_iterations)
        new_aesgcm = AESGCM(new_key)

        # Create new auth verifier
        new_verifier_nonce = os.urandom(NONCE_SIZE)
        new_verifier_ciphertext = new_aesgcm.encrypt(new_verifier_nonce, AUTH_MAGIC, AUTH_AAD)
        new_verifier_blob = new_verifier_nonce + new_verifier_ciphertext

        # Prepare re-encrypted entries
        re_encrypted_rows: List[Tuple[str, bytes, bytes, float]] = []
        for date_str, entry_data in self._cached_entries.items():
            new_date_token = hmac.new(new_key, date_str.encode("utf-8"), hashlib.sha256).hexdigest()
            payload_bytes = json.dumps(entry_data, ensure_ascii=False).encode("utf-8")
            nonce = os.urandom(NONCE_SIZE)
            ciphertext = new_aesgcm.encrypt(nonce, payload_bytes, ENTRY_AAD)
            timestamp = datetime.datetime.now().timestamp()
            re_encrypted_rows.append((new_date_token, nonce, ciphertext, timestamp))

        # Atomic commit
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("BEGIN TRANSACTION")
            try:
                # Update metadata
                cursor.execute("UPDATE vault_meta SET value = ? WHERE key = 'salt'", (new_salt,))
                cursor.execute("UPDATE vault_meta SET value = ? WHERE key = 'iterations'", (str(new_iterations).encode("utf-8"),))
                cursor.execute("UPDATE vault_meta SET value = ? WHERE key = 'auth_verifier'", (new_verifier_blob,))

                # Replace all entries
                cursor.execute("DELETE FROM entries")
                cursor.executemany(
                    "INSERT INTO entries (date_token, nonce, ciphertext, updated_at) VALUES (?, ?, ?, ?)",
                    re_encrypted_rows
                )
                conn.commit()
            except Exception:
                conn.rollback()
                raise

        self._key = new_key
        self._salt = new_salt
        self._iterations = new_iterations

    def get_setting(self, key: str, default: str = "") -> str:
        """Retrieve a stored setting value."""
        if not self.exists():
            return default
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
                row = cursor.fetchone()
                return row[0] if row else default
        except Exception:
            return default

    def set_setting(self, key: str, value: str) -> None:
        """Store a setting value."""
        if not self.exists():
            return
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
            conn.commit()

    def export_to_markdown(self, destination_file: Path | str) -> int:
        """
        Export all decrypted entries to a cleanly formatted Markdown file.
        Returns the number of entries exported.
        """
        self._require_unlocked()
        entries = self.get_all_entries(reverse=False)  # Chronological order
        dest = Path(destination_file).expanduser().resolve()
        dest.parent.mkdir(parents=True, exist_ok=True)

        lines = [
            "# Personal Daily Diary Export",
            f"*Exported on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}*",
            "",
            "---",
            "",
        ]

        for entry in entries:
            date_str = entry.get("date", "Unknown Date")
            title = entry.get("title", "")
            mood = entry.get("mood", "")
            tags = entry.get("tags", [])
            content = entry.get("content", "")

            # Format Date Header
            try:
                dt = datetime.date.fromisoformat(date_str)
                formatted_date = dt.strftime("%A, %B %d, %Y")
            except Exception:
                formatted_date = date_str

            heading = f"## {formatted_date}"
            if title:
                heading += f" - {title}"
            lines.append(heading)
            lines.append("")

            meta_items = []
            if mood:
                meta_items.append(f"**Mood:** {mood}")
            if tags:
                meta_items.append(f"**Tags:** {', '.join('#' + t for t in tags)}")
            if meta_items:
                lines.append(" | ".join(meta_items))
                lines.append("")

            lines.append(content)
            lines.append("")
            lines.append("---")
            lines.append("")

        dest.write_text("\n".join(lines), encoding="utf-8")
        return len(entries)
