"""
Rich Terminal User Interface components and layout renderers for Linux Flashcards.
"""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

from rich.align import Align
from rich.box import DOUBLE, HEAVY, ROUNDED, SIMPLE
from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel
from rich.progress_bar import ProgressBar
from rich.rule import Rule
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text

console = Console()


def clear_screen() -> None:
    """Clear terminal screen."""
    os.system("clear" if os.name != "nt" else "cls")


def print_banner(streak: int = 1) -> None:
    """Display an eye-catching header banner."""
    header_text = Text()
    header_text.append("🐧 LINUX TERMINAL COMMAND FLASHCARDS\n", style="bold cyan")
    header_text.append("Master the Command Line • Spaced Repetition • Interactive Challenges\n", style="italic bright_black")
    header_text.append(f"🔥 Daily Streak: {streak} day{'s' if streak != 1 else ''}", style="bold yellow")

    panel = Panel(
        Align.center(header_text),
        border_style="bright_blue",
        box=ROUNDED,
        padding=(0, 2),
    )
    console.print(panel)


def render_card_front(card: Dict[str, Any], card_index: int, total_cards: int, mode: str = "scenario_first") -> Panel:
    """
    Render front of a flashcard.
    mode can be:
    - 'scenario_first': prompt with scenario/description, guess command
    - 'command_first': prompt with command name, guess syntax & flags
    """
    progress = card.get("progress", {})
    box_num = progress.get("box", 1)
    is_bookmarked = progress.get("bookmarked", False)

    # Badges
    box_styles = {
        1: ("Box 1 (New / Hard)", "bright_red"),
        2: ("Box 2 (Learning)", "yellow"),
        3: ("Box 3 (Familiar)", "bright_blue"),
        4: ("Box 4 (Proficient)", "cyan"),
        5: ("Box 5 (Mastered)", "bold green"),
    }
    box_name, box_color = box_styles.get(box_num, ("Box 1", "red"))
    bm_str = "⭐ Bookmarked" if is_bookmarked else "☆ Unmarked"

    header_bar = (
        f"[bold bright_white]Card {card_index + 1}/{total_cards}[/bold bright_white]  │  "
        f"[magenta]{card['category']}[/magenta]  │  "
        f"[{box_color}]{box_name}[/{box_color}]  │  "
        f"[dim]{card['difficulty']}[/dim]  │  "
        f"[yellow]{bm_str}[/yellow]"
    )

    content = Text()
    content.append("\n")

    if mode == "scenario_first":
        content.append("TASK / SCENARIO:\n", style="bold underline cyan")
        challenge_scenario = card.get("challenge", {}).get("scenario")
        if challenge_scenario:
            content.append(f"{challenge_scenario}\n\n", style="bold white")
        else:
            content.append(f"{card['summary']}\n\n", style="bold white")
        content.append("Question: ", style="bold green")
        content.append("Which Linux terminal command and flags would you use?\n", style="italic")
    else:  # command_first
        content.append("COMMAND:\n", style="bold underline cyan")
        content.append(f"  $ {card['name']}\n\n", style="bold green font_size_large")
        content.append("Question: ", style="bold green")
        content.append(f"What does this command do, what is its syntax, and what are its key flags?\n", style="italic")

    footer_text = "\n[bold yellow]Controls:[/] [Enter/Space] Flip card  │  [h] Peek Hint  │  [b] Bookmark  │  [q] Exit deck"

    return Panel(
        content,
        title=header_bar,
        subtitle=footer_text,
        border_style="bright_cyan",
        box=ROUNDED,
        padding=(1, 3),
    )


def render_card_back(card: Dict[str, Any], card_index: int, total_cards: int) -> Panel:
    """Render the full revealed back of a flashcard."""
    progress = card.get("progress", {})
    box_num = progress.get("box", 1)
    is_bookmarked = progress.get("bookmarked", False)

    header_bar = (
        f"[bold green]✓ REVEALED[/bold green]  │  "
        f"[bold bright_white]Card {card_index + 1}/{total_cards}[/bold bright_white]  │  "
        f"[magenta]{card['category']}[/magenta]  │  "
        f"[dim]{card['difficulty']}[/dim]"
    )

    elements: List[Any] = []

    # Command Header & Syntax
    cmd_title = Text()
    cmd_title.append(f"$ {card['name']}", style="bold bright_green")
    cmd_title.append(f"  —  {card['summary']}", style="italic white")
    elements.append(cmd_title)
    elements.append(Text(f"\nSyntax:  {card['syntax']}", style="bold yellow"))
    elements.append(Text(f"Details: {card['description']}\n", style="bright_white"))

    # Common Flags Table
    flags = card.get("flags", {})
    if flags:
        table = Table(
            title="Key Flags & Options",
            title_style="bold cyan",
            box=SIMPLE,
            header_style="bold magenta",
            padding=(0, 1),
            expand=True,
        )
        table.add_column("Flag / Option", style="bold yellow", width=18)
        table.add_column("Function", style="white")

        for flag_name, flag_desc in flags.items():
            table.add_row(flag_name, flag_desc)
        elements.append(table)

    # Real-world Examples Table
    examples = card.get("examples", [])
    if examples:
        elements.append(Text("\nPractical Examples:", style="bold cyan"))
        for eg in examples:
            eg_text = Text()
            eg_text.append(f"  $ {eg['cmd']}", style="bold green")
            eg_text.append(f"  →  {eg['desc']}", style="italic bright_black")
            elements.append(eg_text)

    # Pro-tip / Mnemonic
    hint = card.get("hint")
    if hint:
        hint_panel = Panel(
            Text(f"💡 Pro-Tip / Mnemonic: {hint}", style="italic bright_yellow"),
            box=ROUNDED,
            border_style="yellow",
            padding=(0, 1),
        )
        elements.append(Text("\n"))
        elements.append(hint_panel)

    # User Notes
    user_notes = progress.get("notes")
    if user_notes:
        notes_panel = Panel(
            Text(f"📝 Your Personal Note: {user_notes}", style="cyan"),
            box=ROUNDED,
            border_style="cyan",
            padding=(0, 1),
        )
        elements.append(notes_panel)

    # Spaced Repetition Grading Controls
    rating_controls = (
        "\n[bold bright_white]Rate your recall (Spaced Repetition):[/bold bright_white]\n"
        "  [bold red][1] Again[/bold red] (Reset to Box 1)    "
        "  [bold yellow][2] Hard[/bold yellow] (Keep Box)    "
        "  [bold green][3] Good[/bold green] (+1 Box)    "
        "  [bold cyan][4] Easy[/bold cyan] (+2 Boxes)\n"
        "  [dim][b] Bookmark  │  [n] Add note  │  [q] Back to menu[/dim]"
    )

    combined_text = Text()
    for el in elements:
        if isinstance(el, Text):
            combined_text.append_text(el)
            combined_text.append("\n")

    # In case there's a table, render via a group layout or return composite
    from rich.console import Group

    group_renderable = Group(
        cmd_title,
        Text(f"Syntax:  {card['syntax']}", style="bold yellow"),
        Text(f"{card['description']}\n", style="white"),
        *( [table] if flags else [] ),
        Text("\nPractical Examples:", style="bold cyan") if examples else Text(""),
        *(
            [Text.assemble((f"  $ {eg['cmd']}", "bold green"), (f"  →  {eg['desc']}\n", "italic bright_black")) for eg in examples]
        ),
        *( [hint_panel] if hint else [] ),
        *( [notes_panel] if user_notes else [] ),
        Text.from_markup(rating_controls),
    )

    return Panel(
        group_renderable,
        title=header_bar,
        border_style="green",
        box=ROUNDED,
        padding=(1, 2),
    )


def render_quiz_question_panel(
    q: Dict[str, Any],
    q_index: int,
    total_q: int,
    score: int,
) -> Panel:
    """Render multiple-choice quiz question."""
    title_bar = (
        f"[bold bright_white]Question {q_index + 1}/{total_q}[/bold bright_white]  │  "
        f"[magenta]{q['category']}[/magenta]  │  "
        f"[bold green]Score: {score}/{q_index}[/bold green]"
    )

    content = Text()
    content.append("\n")
    content.append(Text.from_markup(q["question"]))
    content.append("\n\n")

    letters = ["A", "B", "C", "D"]
    for i, opt in enumerate(q["options"]):
        prefix = f" [{letters[i]}] "
        content.append(prefix, style="bold cyan")
        content.append(f"{opt}\n", style="white")

    footer_bar = "[bold yellow]Choose answer:[/] [A/B/C/D or 1/2/3/4]  │  [h] Hint  │  [q] Quit Quiz"

    return Panel(
        content,
        title=title_bar,
        subtitle=footer_bar,
        border_style="bright_blue",
        box=ROUNDED,
        padding=(1, 3),
    )


def render_quiz_result_panel(
    is_correct: bool,
    correct_option_letter: str,
    correct_value: str,
    explanation: str,
) -> Panel:
    """Render answer feedback."""
    if is_correct:
        header = "[bold green]✓ CORRECT![/bold green]"
        border_col = "green"
    else:
        header = f"[bold red]✗ INCORRECT — Correct Answer: [{correct_option_letter}] {correct_value}[/bold red]"
        border_col = "red"

    content = Text()
    content.append(Text.from_markup(explanation))
    content.append("\n\n[dim]Press Enter to continue...[/dim]")

    return Panel(
        content,
        title=header,
        border_style=border_col,
        box=ROUNDED,
        padding=(1, 2),
    )


def render_challenge_prompt_panel(card: Dict[str, Any], attempt_num: int) -> Panel:
    """Render interactive command prompt scenario."""
    challenge = card["challenge"]

    title_bar = (
        f"[bold cyan]Interactive Terminal Challenge[/bold cyan]  │  "
        f"[magenta]{card['category']}[/magenta]  │  "
        f"[dim]{card['difficulty']}[/dim]"
    )

    content = Text()
    content.append("SCENARIO REQUIREMENT:\n", style="bold underline yellow")
    content.append(f"{challenge['scenario']}\n\n", style="bold white")
    content.append("Task: ", style="bold green")
    content.append("Type the full terminal command below as you would run it in bash.\n", style="italic")

    footer = "[h] Peek Hint  │  [s] Show Solution  │  [q] Cancel"

    return Panel(
        content,
        title=title_bar,
        subtitle=footer,
        border_style="yellow",
        box=ROUNDED,
        padding=(1, 3),
    )


def render_dashboard(stats: Dict[str, Any]) -> None:
    """Render visual mastery statistics and progress bars."""
    clear_screen()
    print_banner(stats["streak_days"])

    # High level KPI cards
    grid = Table.grid(expand=True, padding=(0, 1))
    grid.add_column(ratio=1)
    grid.add_column(ratio=1)
    grid.add_column(ratio=1)
    grid.add_column(ratio=1)

    kpi1 = Panel(
        Align.center(f"[bold cyan]{stats['overall_mastery']}%[/bold cyan]\n[dim]Overall Mastery[/dim]"),
        box=ROUNDED,
        border_style="cyan",
    )
    kpi2 = Panel(
        Align.center(f"[bold green]{stats['reviewed_count']}[/bold green] / [white]{stats['total_database_cards']}[/white]\n[dim]Commands Studied[/dim]"),
        box=ROUNDED,
        border_style="green",
    )
    kpi3 = Panel(
        Align.center(f"[bold yellow]{stats['quiz_accuracy']}%[/bold yellow]\n[dim]Quiz Accuracy ({stats['quiz_answered']} Qs)[/dim]"),
        box=ROUNDED,
        border_style="yellow",
    )
    kpi4 = Panel(
        Align.center(f"[bold magenta]{stats['challenge_rate']}%[/bold magenta]\n[dim]Challenges Solved ({stats['challenge_solved']})[/dim]"),
        box=ROUNDED,
        border_style="magenta",
    )

    grid.add_row(kpi1, kpi2, kpi3, kpi4)
    console.print(grid)
    console.print()

    # Leitner Box Distribution
    box_dist = stats["box_distribution"]
    box_table = Table(
        title="Spaced Repetition (Leitner Boxes)",
        title_style="bold cyan",
        box=ROUNDED,
        expand=True,
    )
    box_table.add_column("Leitner Box", style="bold white", width=22)
    box_table.add_column("Review Frequency", style="italic bright_black", width=20)
    box_table.add_column("Cards", justify="right", style="bold yellow", width=10)
    box_table.add_column("Distribution", style="green", ratio=1)

    box_labels = {
        1: ("Box 1 (New / Hard)", "Every session (1 day)", "red"),
        2: ("Box 2 (Learning)", "Every 3 days", "yellow"),
        3: ("Box 3 (Familiar)", "Every 7 days", "bright_blue"),
        4: ("Box 4 (Proficient)", "Every 14 days", "cyan"),
        5: ("Box 5 (Mastered)", "Every 30 days", "bold green"),
    }

    total_cards = stats["total_database_cards"]
    for b in range(1, 6):
        count = box_dist.get(b, 0)
        pct = (count / total_cards * 100) if total_cards > 0 else 0
        bar = "█" * int(pct // 4)
        lbl, freq, col = box_labels[b]
        box_table.add_row(
            f"[{col}]{lbl}[/{col}]",
            freq,
            str(count),
            f"[{col}]{bar}[/{col}] [dim]{pct:.1f}%[/dim]",
        )

    console.print(box_table)
    console.print()

    # Secondary metrics summary
    extra_info = Text()
    extra_info.append(f"⭐ Bookmarked Cards: {stats['bookmarked_count']}    ", style="yellow")
    extra_info.append(f"🔄 Total Card Review Reps: {stats['total_card_reviews']}    ", style="cyan")
    extra_info.append(f"🎯 Card Accuracy: {stats['card_accuracy']}%    ", style="green")
    extra_info.append(f"📅 Last Activity: {stats['last_active']}", style="dim")

    console.print(Panel(Align.center(extra_info), box=ROUNDED, border_style="bright_black"))


def render_commands_table(commands: List[Dict[str, Any]], query: str = "") -> None:
    """Render searchable tabular overview of Linux commands."""
    clear_screen()
    title = f"Linux Commands Reference ({len(commands)} commands found)"
    if query:
        title += f" — Search: '{query}'"

    table = Table(title=title, title_style="bold cyan", box=ROUNDED, expand=True)
    table.add_column("#", justify="right", style="dim", width=4)
    table.add_column("Command", style="bold green", min_width=8, max_width=14)
    table.add_column("Category", style="magenta", min_width=14, max_width=20)
    table.add_column("Diff", style="cyan", width=6)
    table.add_column("Summary", style="white", min_width=25)
    table.add_column("Box", justify="center", style="yellow", width=5)
    table.add_column("⭐", justify="center", width=3)

    for i, cmd in enumerate(commands):
        prog = cmd.get("progress", {})
        box_str = f"B{prog.get('box', 1)}"
        bm_str = "⭐" if prog.get("bookmarked") else "-"
        table.add_row(
            str(i + 1),
            cmd["name"],
            cmd["category"],
            cmd["difficulty"][:3],
            cmd["summary"],
            box_str,
            bm_str,
        )

    console.print(table)
