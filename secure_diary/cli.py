"""
cli.py - Interactive Terminal Interface for Secure Daily Diary

Allows full journaling operations directly from the terminal with getpass security:
- Setup & master password unlock
- Today's entry reading and editing
- Search entries
- List recent entries
- Export journal to Markdown
- Change master password
"""

from __future__ import annotations

import datetime
import getpass
import sys
from pathlib import Path
from typing import Optional

from .vault import (
    DiaryVault,
    DiaryVaultError,
    InvalidPasswordError,
    VaultAlreadyExistsError,
    VaultLockedError,
    get_default_vault_path,
)


def prompt_password(prompt_text: str = "Master Password: ") -> str:
    """Prompt for password securely using getpass."""
    try:
        return getpass.getpass(prompt_text)
    except (EOFError, KeyboardInterrupt):
        print("\nAborted.")
        sys.exit(0)


def unlock_or_setup_vault(vault: DiaryVault) -> bool:
    """Handle vault unlock or first-time setup in CLI."""
    if not vault.exists():
        print("=" * 60)
        print("🌟 Welcome to Secure Daily Diary (First-Time Setup)")
        print("Your diary will be encrypted locally using AES-256-GCM.")
        print("Zero cloud sync. Note: If you forget this password, data cannot be recovered.")
        print("=" * 60)

        while True:
            pwd = prompt_password("Create Master Password (min 8 chars): ")
            if len(pwd) < 8:
                print("❌ Password must be at least 8 characters long.\n")
                continue
            confirm = prompt_password("Confirm Master Password: ")
            if pwd != confirm:
                print("❌ Passwords do not match. Try again.\n")
                continue

            try:
                vault.initialize_vault(pwd)
                print("✅ Vault successfully initialized and unlocked!\n")
                return True
            except Exception as e:
                print(f"❌ Failed to initialize vault: {e}\n")
                return False
    else:
        print("=" * 60)
        print("🔒 Secure Daily Diary - Encrypted Local Storage")
        print("=" * 60)

        for attempt in range(3):
            pwd = prompt_password("Enter Master Password: ")
            try:
                vault.unlock(pwd)
                print("🔓 Vault unlocked successfully!\n")
                return True
            except InvalidPasswordError:
                remaining = 2 - attempt
                print(f"❌ Incorrect password. ({remaining} attempts remaining)\n")
            except Exception as e:
                print(f"❌ Error unlocking vault: {e}\n")
                return False

        print("Too many incorrect attempts. Exiting.")
        return False


def view_or_edit_entry(vault: DiaryVault, date_str: str):
    """Display an entry and optionally edit it."""
    entry = vault.get_entry(date_str)
    print("\n" + "-" * 50)
    print(f"📅 Diary Entry: {date_str}")
    if entry:
        if entry.get("title"):
            print(f"📌 Title: {entry['title']}")
        if entry.get("mood"):
            print(f"🎭 Mood:  {entry['mood']}")
        if entry.get("tags"):
            print(f"🏷️  Tags:  {', '.join('#' + t for t in entry['tags'])}")
        print(f"🕒 Updated: {entry.get('updated_at', 'N/A')}")
        print("-" * 50)
        print(entry.get("content", ""))
        print("-" * 50)
    else:
        print("No entry recorded for this date yet.")
        print("-" * 50)

    choice = input("\n[E]dit / [W]rite entry, [D]elete, or [B]ack? [e/d/B]: ").strip().lower()
    if choice == "d":
        if entry and input(f"Are you sure you want to delete {date_str}? (y/N): ").strip().lower() == "y":
            vault.delete_entry(date_str)
            print("🗑️ Entry deleted.")
    elif choice in ("e", "w"):
        current_title = entry.get("title", "") if entry else ""
        current_mood = entry.get("mood", "") if entry else ""
        current_tags = ", ".join(entry.get("tags", [])) if entry else ""
        current_content = entry.get("content", "") if entry else ""

        print(f"\nTitle [{current_title}]: ", end="")
        new_title = input().strip() or current_title

        print(f"Mood [{current_mood}] (e.g. 😊, ⚡, 😌, 😴): ", end="")
        new_mood = input().strip() or current_mood

        print(f"Tags [{current_tags}] (comma-separated): ", end="")
        new_tags_raw = input().strip() or current_tags
        tags = [t.strip().lstrip("#") for t in new_tags_raw.split(",") if t.strip()]

        print("\nEnter diary content. Type 'EOF' on a new line or Ctrl+D when finished:")
        lines = []
        try:
            while True:
                line = input()
                if line.strip() == "EOF":
                    break
                lines.append(line)
        except EOFError:
            pass

        new_content = "\n".join(lines).strip()
        if not new_content and current_content:
            new_content = current_content

        vault.save_entry(
            date_str=date_str,
            title=new_title,
            content=new_content,
            mood=new_mood,
            tags=tags,
        )
        print("💾 Entry encrypted and saved locally!")


def run_cli(db_path: Optional[Path | str] = None):
    """Run interactive terminal CLI."""
    vault = DiaryVault(db_path)

    if not unlock_or_setup_vault(vault):
        sys.exit(1)

    while True:
        today_str = datetime.date.today().isoformat()
        print("\n📋 Main Menu:")
        print(f"1. Today's Entry ({today_str})")
        print("2. Browse / Edit Entry by Date")
        print("3. Search Journal Entries")
        print("4. List Recent Entries")
        print("5. Export Journal to Markdown")
        print("6. Change Master Password")
        print("7. Lock & Exit")

        try:
            choice = input("\nSelect an option [1-7]: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nLocking vault...")
            vault.lock()
            break

        if choice == "1":
            view_or_edit_entry(vault, today_str)

        elif choice == "2":
            target = input("Enter date (YYYY-MM-DD): ").strip()
            try:
                datetime.date.fromisoformat(target)
                view_or_edit_entry(vault, target)
            except ValueError:
                print("❌ Invalid date format. Please use YYYY-MM-DD.")

        elif choice == "3":
            query = input("Enter search query: ").strip()
            results = vault.search_entries(query)
            print(f"\n🔍 Found {len(results)} matching entries:")
            for e in results:
                title = e.get("title", "Untitled")
                mood = e.get("mood", "")
                snippet = (e.get("content", "").replace("\n", " ")[:60])
                print(f"  • {e['date']} {mood} [{title}] - {snippet}...")

        elif choice == "4":
            entries = vault.get_all_entries()[:10]
            print(f"\n📖 Recent {len(entries)} Entries:")
            for e in entries:
                title = e.get("title", "Untitled")
                mood = e.get("mood", "")
                print(f"  • {e['date']} {mood} [{title}]")

        elif choice == "5":
            dest = input("Export file path [~/Documents/diary_export.md]: ").strip()
            if not dest:
                dest = str(Path.home() / "Documents" / "diary_export.md")
            count = vault.export_to_markdown(dest)
            print(f"📄 Successfully exported {count} entries to {dest}")

        elif choice == "6":
            old_p = prompt_password("Current Master Password: ")
            new_p = prompt_password("New Master Password: ")
            conf = prompt_password("Confirm New Master Password: ")
            if new_p != conf:
                print("❌ Passwords do not match.")
                continue
            if len(new_p) < 8:
                print("❌ Password must be at least 8 characters.")
                continue
            try:
                vault.change_password(old_p, new_p)
                print("🔑 Master password changed and all entries re-encrypted!")
            except Exception as e:
                print(f"❌ Error: {e}")

        elif choice == "7":
            print("🔒 Locking vault and exiting...")
            vault.lock()
            break
        else:
            print("Invalid choice.")
