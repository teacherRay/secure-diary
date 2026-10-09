# 🔐 Secure Daily Diary

A private, password-protected, and end-to-end encrypted daily diary application designed for local-first privacy.

---

## 🛡️ Security & Cryptography Architecture

All journal data is encrypted at rest using industry-standard cryptographic primitives:

- **Authenticated Encryption**: **AES-256-GCM** (Galois/Counter Mode). Every entry is encrypted with an authenticated ciphertext and a tamper-detection tag.
- **Key Derivation Function (KDF)**: **PBKDF2-HMAC-SHA256** with **600,000 iterations** (OWASP recommendation) and a cryptographically secure random 32-byte salt (`os.urandom(32)`).
- **Nonce/IV Generation**: Cryptographically secure 12-byte random nonces generated per entry. Nonces are never reused.
- **Date Masking at Rest**: Entry records in SQLite are indexed by **HMAC-SHA256** tokens keyed with the derived master key. Even if an attacker inspects the database file directly, they cannot tell which dates have diary entries.
- **Zero Cloud Exposure**: All operations and databases reside strictly on your local filesystem (`~/.local/share/secure_diary/diary_vault.db`). No telemetry, no network calls, and no remote dependencies.
- **Memory Hygiene**: Encryption keys and decrypted caches are cleared from memory when the diary is locked or when inactivity auto-lock fires.

---

## ✨ Features

- 📅 **Daily Journaling & Calendar**: Effortless date jumping (Today, Yesterday, Next/Previous Day, and Calendar view).
- 🎭 **Mood Tracking**: 8 quick-select moods (😊 Happy, 😌 Calm, 💡 Inspired, ⚡ Productive, 💖 Grateful, 🧘 Reflective, 😴 Tired, 🌧️ Down).
- 🏷️ **Tagging & Categories**: Organize entries with custom tags (e.g. `#work`, `#goals`, `#health`).
- ✍️ **Markdown Toolbar & Live Formatting**: Quick formatting buttons for Bold, Italic, Headings, Bullet Lists, Checklists, Quotes, Code Blocks, and Timestamp stamps (`HH:MM`).
- 💾 **Debounced Auto-Save**: Automatically saves and re-encrypts changes 1.5 seconds after typing stops.
- 🔍 **Encrypted Full-Text Search**: Live search across entries, filtering by title, text, mood, tags, or dates.
- ⏱️ **Auto-Lock on Inactivity**: Automatically locks the diary after 5 minutes of inactivity (configurable to 1, 5, 15, 30 minutes, or Disabled).
- 🔑 **Master Password Change**: Seamlessly re-encrypts all journal entries with a new master key in an atomic SQLite transaction.
- 📄 **Markdown Export**: Export all decrypted entries chronologically to a cleanly formatted Markdown file.

---

## 🚀 How to Run

### 1. Native Desktop GUI (Default)
Integrated with Ubuntu GNOME using GTK 4 and Libadwaita:

```bash
python3 secure_diary.py
```
*(Or click the **Secure Daily Diary** icon in your application launcher.)*

---

### 2. Localhost Web Browser Interface
Opens a private web application in your default browser, bound strictly to `127.0.0.1`:

```bash
python3 secure_diary.py --web
```
Or specify a custom port:
```bash
python3 secure_diary.py --web --port 9000
```

---

### 3. Interactive Terminal CLI
Ideal for quick journaling in headless environments or terminal workflows:

```bash
python3 secure_diary.py --cli
```

---

## 🧪 Automated Test Suite

Run the cryptographic unit tests to verify encryption, wrong password rejection, HMAC date masking, and export functions:

```bash
python3 -m unittest secure_diary/tests/test_vault.py
```

---

## 📂 File Layout

```
.
├── secure_diary.py                  # Main launcher (GUI, Web, CLI modes)
├── secure-diary.desktop             # GNOME desktop launcher
├── README.md                        # Documentation
└── secure_diary/
    ├── __init__.py
    ├── vault.py                     # AES-256-GCM & PBKDF2 storage engine
    ├── gui.py                       # GTK 4 / Libadwaita desktop GUI
    ├── web.py                       # Localhost Web UI (zero-dependency)
    ├── cli.py                       # Interactive terminal CLI
    ├── assets/
    │   ├── diary_icon.svg           # High-resolution SVG application icon
    │   └── diary_icon.png           # 256x256 PNG application icon
    └── tests/
        └── test_vault.py            # Unit test suite
```

**Local Storage Location:**
- Default database: `~/.local/share/secure_diary/diary_vault.db`
- Can be overridden using the `--db /path/to/vault.db` argument or `SECURE_DIARY_DB` environment variable.
