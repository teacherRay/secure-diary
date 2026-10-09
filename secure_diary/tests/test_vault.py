"""
Unit tests for DiaryVault cryptographic storage engine.
"""

import os
import sqlite3
import tempfile
import unittest
from pathlib import Path

from secure_diary.vault import (
    DiaryVault,
    DiaryVaultError,
    InvalidPasswordError,
    VaultAlreadyExistsError,
    VaultLockedError,
    VaultNotFoundError,
)


class TestDiaryVault(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_diary.db"
        self.vault = DiaryVault(self.db_path)
        self.password = "CorrectHorseBatteryStaple!2026"

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_init_and_unlock(self):
        # Vault shouldn't exist initially
        self.assertFalse(self.vault.exists())
        self.assertFalse(self.vault.is_unlocked)

        # Initialize
        self.vault.initialize_vault(self.password)
        self.assertTrue(self.vault.exists())
        self.assertTrue(self.vault.is_unlocked)

        # Re-initializing should raise error
        with self.assertRaises(VaultAlreadyExistsError):
            self.vault.initialize_vault("new_password")

        # Lock vault
        self.vault.lock()
        self.assertFalse(self.vault.is_unlocked)

        # Operation while locked should fail
        with self.assertRaises(VaultLockedError):
            self.vault.save_entry("2026-10-09", "Locked", "Cannot save")

        # Wrong password unlock should fail
        with self.assertRaises(InvalidPasswordError):
            self.vault.unlock("WrongPassword123")
        self.assertFalse(self.vault.is_unlocked)

        # Correct password unlock should succeed
        self.assertTrue(self.vault.unlock(self.password))
        self.assertTrue(self.vault.is_unlocked)

    def test_entry_crud_and_encryption_privacy(self):
        self.vault.initialize_vault(self.password)

        date_1 = "2026-10-08"
        date_2 = "2026-10-09"

        # Save entries
        self.vault.save_entry(
            date_str=date_1,
            title="Yesterday's Summary",
            content="A very productive coding session.",
            mood="⚡ Productive",
            tags=["coding", "work"],
        )

        self.vault.save_entry(
            date_str=date_2,
            title="Today's Reflection",
            content="Creating an encrypted daily diary with AES-256.",
            mood="😊 Happy",
            tags=["crypto", "security", "diary"],
        )

        # Verify decrypted retrieval
        entry1 = self.vault.get_entry(date_1)
        self.assertIsNotNone(entry1)
        self.assertEqual(entry1["title"], "Yesterday's Summary")
        self.assertEqual(entry1["mood"], "⚡ Productive")
        self.assertIn("coding", entry1["tags"])

        entry2 = self.vault.get_entry(date_2)
        self.assertIsNotNone(entry2)
        self.assertEqual(entry2["content"], "Creating an encrypted daily diary with AES-256.")

        # Test date list
        dates = self.vault.get_entry_dates()
        self.assertEqual(dates, {date_1, date_2})

        # CRITICAL PRIVACY CHECK: Verify plaintext content & dates are NOT stored in SQLite!
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT date_token, ciphertext FROM entries")
            rows = cursor.fetchall()
            self.assertEqual(len(rows), 2)
            for date_token, ciphertext in rows:
                # Raw database bytes must not contain readable strings
                self.assertNotIn(b"Yesterday's Summary", ciphertext)
                self.assertNotIn(b"AES-256", ciphertext)
                self.assertNotIn(date_1.encode("utf-8"), date_token.encode("utf-8"))
                self.assertNotIn(date_2.encode("utf-8"), date_token.encode("utf-8"))

        # Lock and unlock with a new instance to verify clean persistence
        self.vault.lock()
        new_vault = DiaryVault(self.db_path)
        new_vault.unlock(self.password)

        loaded_entry = new_vault.get_entry(date_2)
        self.assertIsNotNone(loaded_entry)
        self.assertEqual(loaded_entry["title"], "Today's Reflection")

    def test_search_entries(self):
        self.vault.initialize_vault(self.password)

        self.vault.save_entry("2026-10-01", "Meeting notes", "Discussed project architecture", tags=["work"])
        self.vault.save_entry("2026-10-02", "Hiking trip", "Went hiking in the national park", mood="🌲", tags=["outdoors"])
        self.vault.save_entry("2026-10-03", "Reading day", "Read book on cryptography", tags=["books", "crypto"])

        # Search by tag
        results = self.vault.search_entries("crypto")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["date"], "2026-10-03")

        # Search by content
        results = self.vault.search_entries("hiking")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["date"], "2026-10-02")

        # Search empty returns all
        results = self.vault.search_entries("")
        self.assertEqual(len(results), 3)

    def test_change_password(self):
        self.vault.initialize_vault(self.password)
        self.vault.save_entry("2026-10-09", "Secret Diary", "Extremely confidential entry")

        new_password = "BrandNewSuperSecurePassword#999"

        # Wrong old password should fail
        with self.assertRaises(InvalidPasswordError):
            self.vault.change_password("wrong_old_pwd", new_password)

        # Successful password change
        self.vault.change_password(self.password, new_password)

        # Lock and try opening with old password
        self.vault.lock()
        with self.assertRaises(InvalidPasswordError):
            self.vault.unlock(self.password)

        # Unlock with new password
        self.assertTrue(self.vault.unlock(new_password))
        entry = self.vault.get_entry("2026-10-09")
        self.assertIsNotNone(entry)
        self.assertEqual(entry["content"], "Extremely confidential entry")

    def test_markdown_export(self):
        self.vault.initialize_vault(self.password)
        self.vault.save_entry(
            "2026-10-09",
            "Sunny Friday",
            "Today the sun was bright.",
            mood="☀️ Sunny",
            tags=["weather", "life"],
        )

        export_file = Path(self.temp_dir.name) / "exported_journal.md"
        count = self.vault.export_to_markdown(export_file)
        self.assertEqual(count, 1)
        self.assertTrue(export_file.exists())

        content = export_file.read_text(encoding="utf-8")
        self.assertIn("Sunny Friday", content)
        self.assertIn("Today the sun was bright.", content)
        self.assertIn("#weather", content)


if __name__ == "__main__":
    unittest.main()
