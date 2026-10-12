# 🐧 Linux Terminal Command Flashcard App

A feature-packed, interactive terminal application built in Python for learning, mastering, and retaining Linux terminal commands with **Spaced Repetition (Leitner System)**, **Multiple-Choice Quizzes**, and **Interactive Bash Prompt Challenges**.

---

## 🌟 Highlights

- **📚 70+ Curated Linux Commands**:
  - Across 10 core sysadmin & developer categories:
    - *Files & Navigation* (`pwd`, `ls`, `cd`, `cp`, `mv`, `rm`, `mkdir`, `touch`, `find`, `tree`, `ln`, `which`, `file`)
    - *Viewing & Text Processing* (`cat`, `less`, `head`, `tail`, `grep`, `wc`, `sort`, `uniq`, `cut`, `sed`, `awk`, `diff`)
    - *System Info & Performance* (`uname`, `top`, `htop`, `df`, `du`, `free`, `ps`, `lsof`, `uptime`)
    - *Process Control* (`kill`, `pkill`, `killall`, `nohup`)
    - *Permissions & Security* (`chmod`, `chown`, `sudo`, `whoami`)
    - *Networking & Web* (`curl`, `wget`, `ping`, `ssh`, `scp`, `rsync`, `ss`, `ip`, `dig`)
    - *Archiving & Compression* (`tar`, `gzip`, `zip`)
    - *Pipes, Redirection & Utilities* (`|`, `>`, `>>`, `tee`, `xargs`, `man`, `history`, `alias`, `export`, `apt`)
    - *Services & Logs* (`systemctl`, `journalctl`, `crontab`, `dmesg`)
    - *Disk & Storage Management* (`lsblk`, `mount`, `umount`, `dd`)
- **🧠 Leitner Spaced Repetition System**:
  - Automatically schedules review intervals based on recall difficulty:
    - **Box 1 (New / Hard)**: Every session / 1 day
    - **Box 2 (Learning)**: Every 3 days
    - **Box 3 (Familiar)**: Every 7 days
    - **Box 4 (Proficient)**: Every 14 days
    - **Box 5 (Mastered)**: Every 30 days
- **🎮 Multiple Learning Modes**:
  1. **Flashcard Study (Scenario → Command)**: Read a real-world task scenario, think of the command, flip to reveal syntax, flags, examples, and pro-tips.
  2. **Flashcard Study (Command → Flags & Meaning)**: Drill what a command does and its key flags.
  3. **Multiple Choice Quiz**: Fast-paced 4-choice questions testing command identification, flags, and options with instant feedback.
  4. **Interactive Command Prompt Challenge**: Type actual commands into a simulated `user@linux:~$ ` terminal prompt with intelligent argument and syntax validation.
  5. **Fast Flag Trainer**: Rapid drill focusing on high-frequency flags (`-r`, `-h`, `-i`, `-a`, `-P`, etc.).
  6. **Command Explorer & Live Search**: Instant search and cheat-sheet view across all 70+ commands.
  7. **Mastery Dashboard**: Progress KPIs, Leitner box distribution graph, quiz accuracy, and daily active streak.
- **✨ Rich Terminal Interface**: Built with `rich` for syntax highlighting, color badges, clean tables, and formatted cards.

---

## 🚀 Quick Start

### Run the App Interactively
```bash
python3 main.py
```
Or directly if executable:
```bash
./main.py
```

---

## 🛠️ Command-Line Options

You can also run specific modes or queries directly without navigating menus:

```bash
# View mastery statistics and spaced repetition breakdown
python3 main.py --stats

# Search for any command or flag by keyword
python3 main.py --search grep
python3 main.py --search "recursive"

# View complete cheat sheet manual for a specific command
python3 main.py --info tar
python3 main.py --info find

# Start a 10-question quiz directly
python3 main.py --quiz -n 10

# Start a quiz filtered to a specific category
python3 main.py --quiz -c "Networking & Web" -n 5

# Start interactive command prompt challenge
python3 main.py --challenge -n 5

# Review only cards that are currently due for spaced repetition review
python3 main.py --due

# List all commands in a category
python3 main.py --list -c "Files & Navigation"
```

---

## ⌨️ Flashcard Controls

| Key | Action |
| :--- | :--- |
| `Enter` / `Space` | Flip card to reveal answer and examples |
| `h` | Peek at mnemonic hint / pro-tip |
| `b` | Toggle bookmark (favorite) |
| `1` | **Again**: Forgot / reset to Box 1 |
| `2` | **Hard**: Correct with difficulty, keep Box |
| `3` | **Good**: Recalled successfully, promote +1 Box |
| `4` | **Easy**: Effortless recall, promote +2 Boxes |
| `n` | Attach personal note to card |
| `q` | Exit back to menu |

---

## 🧪 Running Unit Tests

Run the test suite with Python's built-in `unittest`:

```bash
python3 -m unittest discover -s tests -p "test_*.py" -v
```

---

## 📁 Project Architecture

```
linux_flashcards/
├── __init__.py           # Package metadata
├── data.py               # Database of 70+ commands, categories, flags, and challenges
├── storage.py            # Spaced repetition engine, Leitner box intervals, JSON persistence
├── engine.py             # Deck filtering, quiz generator, and command validator
├── ui.py                 # Rich terminal layout components, cards, tables, dashboard
├── cli.py                # Interactive CLI loops, prompt handlers, and argument parsing
└── README.md             # Documentation
main.py                   # Root executable entrypoint
tests/
└── test_flashcards.py    # 16 unit tests for schemas, logic, and spaced repetition
```
