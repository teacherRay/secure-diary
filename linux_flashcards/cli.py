"""
Interactive Command Line Interface and application runner for Linux Flashcards.
"""

from __future__ import annotations

import argparse
import sys
from typing import Any, Dict, List, Optional

from rich.box import ROUNDED
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, IntPrompt, Prompt
from rich.table import Table
from rich.text import Text

from linux_flashcards.data import CATEGORIES, COMMANDS, COMMAND_MAP, DIFFICULTIES
from linux_flashcards.engine import FlashcardEngine
from linux_flashcards.storage import ProgressStorage
from linux_flashcards.ui import (
    clear_screen,
    console,
    print_banner,
    render_card_back,
    render_card_front,
    render_challenge_prompt_panel,
    render_commands_table,
    render_dashboard,
    render_quiz_question_panel,
    render_quiz_result_panel,
)


class FlashcardApp:
    """Main application controller for Linux Terminal Flashcards."""

    def __init__(self, storage_path: Optional[str] = None):
        self.storage = ProgressStorage(storage_path)
        self.engine = FlashcardEngine(self.storage)

    def select_category_filter(self) -> Optional[str]:
        """Prompt user to choose a category."""
        console.print("\n[bold cyan]Select Category:[/bold cyan]")
        console.print("  [bold yellow][0][/bold yellow] All Categories")
        for i, cat in enumerate(CATEGORIES, 1):
            console.print(f"  [bold yellow][{i}][/bold yellow] {cat}")

        try:
            choice = IntPrompt.ask("\nChoose option", default=0)
            if choice == 0 or choice > len(CATEGORIES) or choice < 0:
                return "All"
            return CATEGORIES[choice - 1]
        except (KeyboardInterrupt, EOFError):
            return "All"

    def select_difficulty_filter(self) -> Optional[str]:
        """Prompt user to choose difficulty level."""
        console.print("\n[bold cyan]Select Difficulty:[/bold cyan]")
        console.print("  [bold yellow][0][/bold yellow] All Difficulties")
        for i, diff in enumerate(DIFFICULTIES, 1):
            console.print(f"  [bold yellow][{i}][/bold yellow] {diff}")

        try:
            choice = IntPrompt.ask("\nChoose option", default=0)
            if choice == 0 or choice > len(DIFFICULTIES) or choice < 0:
                return "All"
            return DIFFICULTIES[choice - 1]
        except (KeyboardInterrupt, EOFError):
            return "All"

    # =========================================================================
    # Mode 1: Flashcard Study
    # =========================================================================
    def run_flashcards(
        self,
        category: Optional[str] = None,
        difficulty: Optional[str] = None,
        filter_mode: str = "all",
        limit: int = 15,
        mode: str = "scenario_first",
    ) -> None:
        """Run interactive flashcard study session."""
        deck = self.engine.get_deck(
            category=category,
            difficulty=difficulty,
            filter_mode=filter_mode,
            limit=limit,
            shuffle=True,
        )

        if not deck:
            clear_screen()
            print_banner(self.storage.data["meta"].get("streak_days", 1))
            console.print(
                Panel(
                    "[bold yellow]No cards matched your filter![/bold yellow]\n"
                    "If you selected 'Due for Review', great news: you have no pending reviews right now!\n"
                    "Try studying 'All Cards' or selecting another category.",
                    border_style="yellow",
                )
            )
            Prompt.ask("\nPress Enter to return to main menu")
            return

        total_cards = len(deck)
        idx = 0

        while idx < total_cards:
            card = deck[idx]
            clear_screen()
            print_banner(self.storage.data["meta"].get("streak_days", 1))

            # FRONT
            front_panel = render_card_front(card, idx, total_cards, mode=mode)
            console.print(front_panel)

            try:
                action = Prompt.ask("\n[bold]Action[/bold]", default="")
            except (KeyboardInterrupt, EOFError):
                break

            action_lower = action.strip().lower()

            if action_lower == "q":
                break
            elif action_lower == "h":
                # Show hint
                hint = card.get("hint") or "Think about standard GNU coreutils naming."
                console.print(f"\n💡 [bold yellow]Hint:[/] {hint}")
                Prompt.ask("Press Enter to continue...")
                continue
            elif action_lower == "b":
                # Toggle bookmark
                is_bm = self.storage.toggle_bookmark(card["id"])
                card["progress"]["bookmarked"] = is_bm
                status = "added to" if is_bm else "removed from"
                console.print(f"[bold yellow]Card {status} bookmarks![/bold yellow]")
                Prompt.ask("Press Enter to continue...")
                continue

            # BACK (REVEAL)
            clear_screen()
            print_banner(self.storage.data["meta"].get("streak_days", 1))
            back_panel = render_card_back(card, idx, total_cards)
            console.print(back_panel)

            rating_input = ""
            while True:
                try:
                    rating_input = Prompt.ask("\n[bold]Select Recall Rating [1-4, b, n, q][/bold]", default="3").strip().lower()
                except (KeyboardInterrupt, EOFError):
                    return

                if rating_input == "1":
                    self.storage.record_review(card["id"], "again")
                    break
                elif rating_input == "2":
                    self.storage.record_review(card["id"], "hard")
                    break
                elif rating_input == "3":
                    self.storage.record_review(card["id"], "good")
                    break
                elif rating_input == "4":
                    self.storage.record_review(card["id"], "easy")
                    break
                elif rating_input == "b":
                    is_bm = self.storage.toggle_bookmark(card["id"])
                    card["progress"]["bookmarked"] = is_bm
                    console.print(f"[bold yellow]Bookmark toggled: {is_bm}[/bold yellow]")
                elif rating_input == "n":
                    current_notes = card["progress"].get("notes", "")
                    console.print(f"Current note: {current_notes or '(None)'}")
                    new_notes = Prompt.ask("Enter custom note")
                    self.storage.set_notes(card["id"], new_notes)
                    card["progress"]["notes"] = new_notes
                    console.print("[bold green]Note saved![/bold green]")
                elif rating_input == "q":
                    return
                else:
                    console.print("[dim]Please enter 1 (Again), 2 (Hard), 3 (Good), 4 (Easy), or q to exit.[/dim]")

            idx += 1

        # Session complete
        clear_screen()
        print_banner(self.storage.data["meta"].get("streak_days", 1))
        console.print(
            Panel(
                f"[bold green]🎉 Flashcard Session Complete![/bold green]\n"
                f"You reviewed [bold cyan]{idx}[/bold cyan] cards in this session.\n"
                f"Your spaced repetition intervals have been updated.",
                border_style="green",
            )
        )
        Prompt.ask("\nPress Enter to return to main menu")

    # =========================================================================
    # Mode 2: Multiple Choice Quiz
    # =========================================================================
    def run_quiz(
        self,
        count: int = 10,
        category: Optional[str] = None,
        difficulty: Optional[str] = None,
    ) -> None:
        """Run multiple-choice quiz session."""
        questions = self.engine.generate_quiz_session(count=count, category=category, difficulty=difficulty)

        if not questions:
            console.print("[bold red]Unable to generate quiz for chosen criteria.[/bold red]")
            Prompt.ask("Press Enter to return...")
            return

        score = 0
        total_q = len(questions)

        for i, q in enumerate(questions):
            clear_screen()
            print_banner(self.storage.data["meta"].get("streak_days", 1))

            q_panel = render_quiz_question_panel(q, i, total_q, score)
            console.print(q_panel)

            while True:
                try:
                    user_resp = Prompt.ask("\n[bold]Your choice[/bold]").strip().upper()
                except (KeyboardInterrupt, EOFError):
                    return

                if user_resp == "Q":
                    return
                elif user_resp == "H":
                    hint = q.get("hint") or "Think about the command category and common flags."
                    console.print(f"\n💡 [bold yellow]Hint:[/] {hint}")
                    continue

                # Map answer
                mapping = {"A": 0, "1": 0, "B": 1, "2": 1, "C": 2, "3": 2, "D": 3, "4": 3}
                if user_resp in mapping and mapping[user_resp] < len(q["options"]):
                    chosen_idx = mapping[user_resp]
                    break
                else:
                    console.print("[yellow]Invalid choice. Enter A, B, C, D (or 1, 2, 3, 4).[/yellow]")

            is_correct = (chosen_idx == q["correct_index"])
            if is_correct:
                score += 1
            self.storage.record_quiz_answer(is_correct)

            letters = ["A", "B", "C", "D"]
            correct_letter = letters[q["correct_index"]]
            res_panel = render_quiz_result_panel(
                is_correct=is_correct,
                correct_option_letter=correct_letter,
                correct_value=q["correct_value"],
                explanation=q["explanation"],
            )
            console.print(res_panel)
            try:
                Prompt.ask("")
            except (KeyboardInterrupt, EOFError):
                break

        # Quiz Results Summary
        clear_screen()
        print_banner(self.storage.data["meta"].get("streak_days", 1))
        percentage = round((score / total_q * 100), 1)

        grade_style = "bold green" if percentage >= 80 else ("bold yellow" if percentage >= 60 else "bold red")
        console.print(
            Panel(
                f"[bold bright_white]Quiz Completed![/bold bright_white]\n\n"
                f"Score: [{grade_style}]{score} / {total_q} ({percentage}%)[/{grade_style}]\n"
                f"{'🏆 Outstanding Linux mastery!' if percentage >= 80 else '👍 Good effort! Keep reviewing flashcards.'}",
                title="Results",
                border_style="cyan",
            )
        )
        Prompt.ask("\nPress Enter to return to main menu")

    # =========================================================================
    # Mode 3: Interactive Command Prompt Sandbox Challenge
    # =========================================================================
    def run_command_challenge(
        self,
        category: Optional[str] = None,
        difficulty: Optional[str] = None,
        count: int = 5,
    ) -> None:
        """Run interactive bash command challenge."""
        deck = self.engine.get_deck(category=category, difficulty=difficulty, shuffle=True, limit=count)

        if not deck:
            console.print("[yellow]No challenges available for selection.[/yellow]")
            Prompt.ask("Press Enter to continue...")
            return

        solved = 0
        total = len(deck)

        for i, card in enumerate(deck):
            clear_screen()
            print_banner(self.storage.data["meta"].get("streak_days", 1))

            p_panel = render_challenge_prompt_panel(card, i + 1)
            console.print(p_panel)

            challenge = card["challenge"]
            attempts = 0
            max_attempts = 3
            is_solved = False

            while attempts < max_attempts:
                attempts += 1
                try:
                    # Simulated prompt
                    user_cmd = Prompt.ask("\n[bold green]user@linux[/bold green]:[bold blue]~[/bold blue]$ ")
                except (KeyboardInterrupt, EOFError):
                    return

                clean_cmd = user_cmd.strip()
                if clean_cmd.lower() == "q":
                    return
                elif clean_cmd.lower() == "h":
                    hint = card.get("hint") or "Check flags: " + ", ".join(card.get("flags", {}).keys())
                    console.print(f"💡 [bold yellow]Hint:[/] {hint}")
                    attempts -= 1
                    continue
                elif clean_cmd.lower() == "s":
                    console.print(f"\n[bold cyan]Solution:[/] [bold green]{challenge['canonical']}[/bold green]")
                    console.print(f"Explanation: {card['summary']}")
                    self.storage.record_challenge_attempt(False)
                    Prompt.ask("\nPress Enter to continue to next challenge...")
                    break

                ok, msg = self.engine.evaluate_challenge_answer(card["id"], clean_cmd)
                console.print(f"\n{msg}")

                if ok:
                    is_solved = True
                    solved += 1
                    self.storage.record_challenge_attempt(True)
                    Prompt.ask("\n[bold green]Correct![/] Press Enter to continue...")
                    break
                else:
                    if attempts < max_attempts:
                        console.print(f"[yellow]Attempt {attempts}/{max_attempts}. Try again (or press [s] for solution):[/yellow]")
                    else:
                        console.print(f"\n[bold red]Out of attempts![/bold red] Solution: [bold green]{challenge['canonical']}[/bold green]")
                        self.storage.record_challenge_attempt(False)
                        Prompt.ask("\nPress Enter to continue...")

        # Summary
        clear_screen()
        print_banner(self.storage.data["meta"].get("streak_days", 1))
        console.print(
            Panel(
                f"[bold bright_white]Challenge Session Complete![/bold bright_white]\n\n"
                f"Solved: [bold green]{solved} / {total}[/bold green] challenges.",
                border_style="green",
            )
        )
        Prompt.ask("\nPress Enter to return to main menu")

    # =========================================================================
    # Mode 4: Quick Flag Drill
    # =========================================================================
    def run_flag_drill(self, count: int = 10) -> None:
        """Rapid fire drilling of high-frequency command flags."""
        # Pick commands that have multiple flags
        flag_candidates = [c for c in self.engine.commands if len(c.get("flags", {})) >= 2]
        if not flag_candidates:
            return

        score = 0
        questions_run = 0

        for _ in range(count):
            card = random_card = __import__("random").choice(flag_candidates)
            flags = list(card["flags"].items())
            target_flag, target_desc = __import__("random").choice(flags)

            clear_screen()
            print_banner(self.storage.data["meta"].get("streak_days", 1))

            drill_panel = Panel(
                f"Command: [bold green]{card['name']}[/bold green] ({card['category']})\n\n"
                f"Which flag performs:\n[bold yellow]\"{target_desc}\"[/bold yellow]?",
                title=f"Flag Drill #{questions_run + 1}/{count}  │  Score: {score}",
                border_style="bright_magenta",
            )
            console.print(drill_panel)

            try:
                user_flag = Prompt.ask("\n[bold]Type flag (e.g. -a)[/bold] or [q] to exit").strip()
            except (KeyboardInterrupt, EOFError):
                break

            if user_flag.lower() == "q":
                break

            questions_run += 1
            # Normalization
            if user_flag == target_flag or user_flag in target_flag.split(", "):
                score += 1
                console.print(f"[bold green]✓ Correct![/bold green] [bold cyan]{target_flag}[/bold cyan]: {target_desc}")
            else:
                console.print(f"[bold red]✗ Not quite![/bold red] The correct flag is [bold green]{target_flag}[/bold green]: {target_desc}")

            try:
                Prompt.ask("\nPress Enter for next flag...")
            except (KeyboardInterrupt, EOFError):
                break

        clear_screen()
        print_banner(self.storage.data["meta"].get("streak_days", 1))
        pct = round((score / questions_run * 100), 1) if questions_run > 0 else 0
        console.print(
            Panel(
                f"[bold bright_white]Flag Drill Finished![/bold bright_white]\n\n"
                f"Score: [bold green]{score} / {questions_run}[/bold green] ({pct}%)",
                border_style="magenta",
            )
        )
        Prompt.ask("\nPress Enter to return to main menu")

    # =========================================================================
    # Mode 5: Command Reference / Cheat Sheet & Search
    # =========================================================================
    def run_explorer(self) -> None:
        """Search commands and inspect detailed cheat sheet cards."""
        query = ""
        while True:
            results = self.engine.search_commands(query)
            render_commands_table(results, query)

            console.print(
                "\n[bold yellow]Explorer Options:[/bold yellow]\n"
                "  • Type [bold cyan]/<query>[/bold cyan] to search (e.g. [italic]/search, /grep, /network[/italic])\n"
                "  • Type a [bold green]command name or number[/bold green] to inspect full details\n"
                "  • Type [bold red]q[/bold red] to return to main menu"
            )

            try:
                cmd_input = Prompt.ask("\nEnter search or command", default="").strip()
            except (KeyboardInterrupt, EOFError):
                break

            if not cmd_input or cmd_input.lower() == "q":
                break

            if cmd_input.startswith("/"):
                query = cmd_input[1:].strip()
                continue

            # Check if input is a number in table
            target_card = None
            if cmd_input.isdigit():
                num = int(cmd_input)
                if 1 <= num <= len(results):
                    target_card = results[num - 1]
            else:
                # Direct command name
                target_card = self.engine.command_map.get(cmd_input.lower())
                if not target_card:
                    # check in results
                    for c in results:
                        if c["name"].lower() == cmd_input.lower():
                            target_card = c
                            break

            if target_card:
                clear_screen()
                print_banner(self.storage.data["meta"].get("streak_days", 1))
                detail_panel = render_card_back(target_card, 0, 1)
                console.print(detail_panel)
                try:
                    action = Prompt.ask("\n[b] Bookmark  │  [Enter] Back to list", default="")
                    if action.lower() == "b":
                        is_bm = self.storage.toggle_bookmark(target_card["id"])
                        console.print(f"[bold yellow]Bookmark: {is_bm}[/bold yellow]")
                        Prompt.ask("Press Enter...")
                except (KeyboardInterrupt, EOFError):
                    pass
            else:
                query = cmd_input

    # =========================================================================
    # Mode 6: Mastery Dashboard
    # =========================================================================
    def run_dashboard(self) -> None:
        """Display mastery dashboard and spaced repetition stats."""
        stats = self.storage.get_summary_stats(len(self.engine.commands))
        render_dashboard(stats)
        try:
            Prompt.ask("\nPress Enter to return to main menu")
        except (KeyboardInterrupt, EOFError):
            pass

    # =========================================================================
    # Mode 7: Reset Progress
    # =========================================================================
    def run_reset_confirm(self) -> None:
        """Confirm and reset learning progress."""
        clear_screen()
        print_banner(self.storage.data["meta"].get("streak_days", 1))
        console.print(
            Panel(
                "[bold red]⚠️ DANGER: Reset Learning Progress[/bold red]\n\n"
                "This will clear all spaced repetition review history, mastery boxes,\n"
                "bookmarks, quiz statistics, and streak counters.",
                border_style="red",
            )
        )
        if Confirm.ask("Are you absolutely sure you want to reset all progress?", default=False):
            self.storage.reset_progress()
            console.print("[bold green]Progress has been reset to brand new state![/bold green]")
        else:
            console.print("[yellow]Reset cancelled.[/yellow]")
        Prompt.ask("\nPress Enter to return to main menu")

    # =========================================================================
    # Main Menu Loop
    # =========================================================================
    def main_menu(self) -> None:
        """Run interactive main menu."""
        while True:
            clear_screen()
            streak = self.storage.data["meta"].get("streak_days", 1)
            print_banner(streak)

            # Quick summary header
            stats = self.storage.get_summary_stats(len(self.engine.commands))
            due_count = len(self.storage.get_due_card_ids())

            menu_table = Table(
                title=f"Learning Hub (Mastery: {stats['overall_mastery']}%  │  {stats['reviewed_count']}/{stats['total_database_cards']} Studied  │  {due_count} Due for Review)",
                title_style="bold cyan",
                box=ROUNDED,
                expand=True,
                show_header=False,
            )
            menu_table.add_column("Key", style="bold yellow", width=8)
            menu_table.add_column("Action", style="white")

            menu_table.add_row("[1]", "🗂️  Study Flashcards (Scenario → Command)")
            menu_table.add_row("[2]", "🔄  Study Flashcards (Command → Details & Flags)")
            menu_table.add_row("[3]", f"⏰  Review Spaced Repetition Due Cards ({due_count} pending)")
            menu_table.add_row("[4]", "❓  Multiple Choice Quiz (Test your recall)")
            menu_table.add_row("[5]", "💻  Interactive Terminal Challenge (Type the bash command)")
            menu_table.add_row("[6]", "🚩  Fast Flag Trainer (Drill tricky command flags)")
            menu_table.add_row("[7]", "📖  Command Explorer & Cheat Sheet (Search 70+ commands)")
            menu_table.add_row("[8]", "📊  Mastery Dashboard & Spaced Repetition Progress")
            menu_table.add_row("[9]", "🗑️  Reset Learning Data")
            menu_table.add_row(r"\[q]", "🚪  Exit")

            console.print(menu_table)

            try:
                choice = Prompt.ask("\n[bold]Select an option[/bold]", default="1").strip().lower()
            except (KeyboardInterrupt, EOFError):
                break

            if choice in ("q", "exit", "quit"):
                break
            elif choice == "1":
                cat = self.select_category_filter()
                diff = self.select_difficulty_filter()
                self.run_flashcards(category=cat, difficulty=diff, mode="scenario_first")
            elif choice == "2":
                cat = self.select_category_filter()
                diff = self.select_difficulty_filter()
                self.run_flashcards(category=cat, difficulty=diff, mode="command_first")
            elif choice == "3":
                self.run_flashcards(filter_mode="due", mode="scenario_first")
            elif choice == "4":
                cat = self.select_category_filter()
                count = IntPrompt.ask("How many questions?", default=10)
                self.run_quiz(count=count, category=cat)
            elif choice == "5":
                cat = self.select_category_filter()
                count = IntPrompt.ask("How many challenges?", default=5)
                self.run_command_challenge(category=cat, count=count)
            elif choice == "6":
                count = IntPrompt.ask("How many flag questions?", default=10)
                self.run_flag_drill(count=count)
            elif choice == "7":
                self.run_explorer()
            elif choice == "8":
                self.run_dashboard()
            elif choice == "9":
                self.run_reset_confirm()


def main() -> None:
    """Parse CLI arguments or launch interactive mode."""
    parser = argparse.ArgumentParser(
        description="🐧 Linux Terminal Command Flashcards - Spaced Repetition CLI App",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--list", "-l", action="store_true", help="List all available Linux commands in database")
    parser.add_argument("--search", "-s", type=str, help="Search for commands matching a keyword")
    parser.add_argument("--info", "-i", type=str, help="Show full manual card for a specific command")
    parser.add_argument("--stats", action="store_true", help="Display mastery dashboard & spaced repetition statistics")
    parser.add_argument("--quiz", action="store_true", help="Launch a multiple-choice quiz directly")
    parser.add_argument("--challenge", action="store_true", help="Launch interactive command prompt challenge directly")
    parser.add_argument("--study", action="store_true", help="Launch flashcard review session directly")
    parser.add_argument("--due", action="store_true", help="Study cards due for review under spaced repetition")
    parser.add_argument("--category", "-c", type=str, help="Filter by category")
    parser.add_argument("--difficulty", "-d", type=str, help="Filter by difficulty (Beginner, Intermediate, Advanced)")
    parser.add_argument("--count", "-n", type=int, default=10, help="Number of cards or quiz questions (default: 10)")
    parser.add_argument("--reset", action="store_true", help="Reset all learning statistics and stored data")
    parser.add_argument("--profile", type=str, help="Custom path to save progress.json file")

    args = parser.parse_args()
    app = FlashcardApp(storage_path=args.profile)

    if args.reset:
        app.storage.reset_progress()
        print("Progress data has been reset.")
        sys.exit(0)

    if args.list:
        results = app.engine.commands
        if args.category:
            results = [c for c in results if c["category"].lower() == args.category.lower()]
        render_commands_table(results)
        sys.exit(0)

    if args.search:
        results = app.engine.search_commands(args.search)
        render_commands_table(results, query=args.search)
        sys.exit(0)

    if args.info:
        card = app.engine.command_map.get(args.info.strip().lower())
        if not card:
            print(f"Command '{args.info}' not found in database.")
            sys.exit(1)
        console.print(render_card_back(card, 0, 1))
        sys.exit(0)

    if args.stats:
        stats = app.storage.get_summary_stats(len(app.engine.commands))
        render_dashboard(stats)
        sys.exit(0)

    if args.quiz:
        app.run_quiz(count=args.count, category=args.category, difficulty=args.difficulty)
        sys.exit(0)

    if args.challenge:
        app.run_command_challenge(category=args.category, difficulty=args.difficulty, count=args.count)
        sys.exit(0)

    if args.study or args.due:
        mode_filter = "due" if args.due else "all"
        app.run_flashcards(
            category=args.category,
            difficulty=args.difficulty,
            filter_mode=mode_filter,
            limit=args.count,
        )
        sys.exit(0)

    # Default to interactive main menu
    app.main_menu()


if __name__ == "__main__":
    main()
