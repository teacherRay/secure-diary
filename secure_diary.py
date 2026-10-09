#!/usr/bin/env python3
"""
secure_diary.py - Secure, Password-Protected, Encrypted Local Daily Diary

Usage:
  python3 secure_diary.py          # Launches native Desktop GUI (GTK 4 / Libadwaita)
  python3 secure_diary.py --web    # Launches local web interface in browser (127.0.0.1)
  python3 secure_diary.py --cli    # Launches interactive terminal CLI
  python3 secure_diary.py --db /path/to/custom_vault.db
"""

import argparse
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(
        description="Secure Daily Diary - AES-256-GCM Encrypted Local Journal",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Modes:
  GUI (default) : Modern native desktop application (GTK 4 / Libadwaita)
  --web         : Localhost browser interface (127.0.0.1:8765)
  --cli         : Interactive terminal command-line interface
        """
    )
    parser.add_argument(
        "--web",
        action="store_true",
        help="Run local web interface in default browser (127.0.0.1)",
    )
    parser.add_argument(
        "--cli",
        action="store_true",
        help="Run interactive command-line interface in terminal",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8765,
        help="Port for local web interface (default: 8765)",
    )
    parser.add_argument(
        "--db",
        type=str,
        default=None,
        help="Custom path to diary database file (default: ~/.local/share/secure_diary/diary_vault.db)",
    )

    args = parser.parse_args()

    # Route to selected interface
    if args.web:
        from secure_diary.web import start_web_server
        start_web_server(db_path=args.db, port=args.port)
    elif args.cli:
        from secure_diary.cli import run_cli
        run_cli(db_path=args.db)
    else:
        # Default to native Desktop GUI
        try:
            from secure_diary.gui import main as gui_main
            gui_main(db_path=args.db)
        except Exception as e:
            print(f"Warning: Could not launch GUI ({e}). Falling back to local web interface...")
            from secure_diary.web import start_web_server
            start_web_server(db_path=args.db, port=args.port)


if __name__ == "__main__":
    main()
