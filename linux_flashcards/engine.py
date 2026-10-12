"""
Learning engine: deck building, quiz generation, and challenge answer verification.
"""

from __future__ import annotations

import random
import re
import shlex
from typing import Any, Dict, List, Optional, Tuple

from linux_flashcards.data import CATEGORIES, COMMANDS, COMMAND_MAP, DIFFICULTIES
from linux_flashcards.storage import ProgressStorage


class FlashcardEngine:
    """Core logic for card selection, quiz synthesis, and command evaluation."""

    def __init__(self, storage: Optional[ProgressStorage] = None):
        self.storage = storage or ProgressStorage()
        self.commands = list(COMMANDS)
        self.command_map = dict(COMMAND_MAP)

    def get_categories(self) -> List[str]:
        return list(CATEGORIES)

    def get_difficulties(self) -> List[str]:
        return list(DIFFICULTIES)

    def get_deck(
        self,
        category: Optional[str] = None,
        difficulty: Optional[str] = None,
        filter_mode: str = "all",  # "all", "due", "bookmarked", "box1", "box5"
        limit: Optional[int] = None,
        shuffle: bool = True,
    ) -> List[Dict[str, Any]]:
        """Filter and prepare a deck of cards based on user selection."""
        deck = []

        for card in self.commands:
            cid = card["id"]
            progress = self.storage.get_card(cid)

            # Category filter
            if category and category.lower() != "all" and card["category"] != category:
                continue

            # Difficulty filter
            if difficulty and difficulty.lower() != "all" and card["difficulty"] != difficulty:
                continue

            # Spaced repetition / status filter
            if filter_mode == "due":
                if not self.storage.is_due_for_review(cid):
                    continue
            elif filter_mode == "bookmarked":
                if not progress.get("bookmarked"):
                    continue
            elif filter_mode == "box1":
                if progress.get("box", 1) != 1:
                    continue
            elif filter_mode == "box5":
                if progress.get("box", 1) != 5:
                    continue

            # Attach live progress info to card representation
            card_copy = dict(card)
            card_copy["progress"] = progress
            deck.append(card_copy)

        if shuffle:
            random.shuffle(deck)

        if limit and limit > 0:
            deck = deck[:limit]

        return deck

    def search_commands(self, query: str) -> List[Dict[str, Any]]:
        """Search commands by name, syntax, description, or flags."""
        q = query.strip().lower()
        if not q:
            return list(self.commands)

        results = []
        for card in self.commands:
            score = 0
            name_lower = card["name"].lower()
            if q == name_lower:
                score += 100
            elif name_lower.startswith(q):
                score += 50
            elif q in name_lower:
                score += 30

            if q in card["summary"].lower():
                score += 20
            if q in card["description"].lower():
                score += 10

            for flag, desc in card.get("flags", {}).items():
                if q in flag.lower() or q in desc.lower():
                    score += 15

            if score > 0:
                card_copy = dict(card)
                card_copy["progress"] = self.storage.get_card(card["id"])
                results.append((score, card_copy))

        results.sort(key=lambda x: x[0], reverse=True)
        return [item[1] for item in results]

    def generate_quiz_question(
        self,
        category: Optional[str] = None,
        difficulty: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Dynamically synthesize a 4-choice multiple choice question.
        Types:
        1. 'identify_command': Description given -> pick command
        2. 'identify_purpose': Command given -> pick description
        3. 'identify_flag': Flag purpose given -> pick flag
        """
        available_pool = [
            c for c in self.commands
            if (not category or category.lower() == "all" or c["category"] == category)
            and (not difficulty or difficulty.lower() == "all" or c["difficulty"] == difficulty)
        ]

        if len(available_pool) < 4:
            available_pool = self.commands

        target = random.choice(available_pool)
        q_types = ["identify_command", "identify_purpose"]
        if target.get("flags") and len(target["flags"]) >= 2:
            q_types.append("identify_flag")

        chosen_type = random.choice(q_types)

        if chosen_type == "identify_command":
            question_text = f"Which command is described as:\n[italic cyan]\"{target['summary']}\"[/italic cyan]"
            correct_answer = target["name"]

            # Distractors from similar category or pool
            same_cat = [c["name"] for c in available_pool if c["id"] != target["id"]]
            if len(same_cat) < 3:
                same_cat = [c["name"] for c in self.commands if c["id"] != target["id"]]
            distractors = random.sample(same_cat, 3)

            options = [correct_answer] + distractors
            random.shuffle(options)
            explanation = f"[bold green]{target['name']}[/bold green]: {target['summary']}\nSyntax: [yellow]{target['syntax']}[/yellow]"

            return {
                "type": chosen_type,
                "card_id": target["id"],
                "category": target["category"],
                "question": question_text,
                "options": options,
                "correct_index": options.index(correct_answer),
                "correct_value": correct_answer,
                "explanation": explanation,
                "hint": target.get("hint", ""),
            }

        elif chosen_type == "identify_purpose":
            question_text = f"What is the primary function of the [bold yellow]{target['name']}[/bold yellow] command?"
            correct_answer = target["summary"]

            same_cat = [c["summary"] for c in available_pool if c["id"] != target["id"] and c["summary"] != target["summary"]]
            if len(same_cat) < 3:
                same_cat = [c["summary"] for c in self.commands if c["id"] != target["id"] and c["summary"] != target["summary"]]
            distractors = random.sample(same_cat, 3)

            options = [correct_answer] + distractors
            random.shuffle(options)
            explanation = f"[bold green]{target['name']}[/bold green]: {target['description']}"

            return {
                "type": chosen_type,
                "card_id": target["id"],
                "category": target["category"],
                "question": question_text,
                "options": options,
                "correct_index": options.index(correct_answer),
                "correct_value": correct_answer,
                "explanation": explanation,
                "hint": target.get("hint", ""),
            }

        else:  # identify_flag
            flag_items = list(target["flags"].items())
            target_flag, flag_desc = random.choice(flag_items)

            question_text = f"In command [bold yellow]{target['name']}[/bold yellow], which flag corresponds to:\n[italic cyan]\"{flag_desc}\"[/italic cyan]"
            correct_answer = target_flag

            other_flags = [f for f, _ in flag_items if f != target_flag]
            all_other_flags = []
            for c in self.commands:
                for f in c.get("flags", {}):
                    if f != target_flag and f not in other_flags:
                        all_other_flags.append(f)

            needed = 3 - len(other_flags)
            if needed > 0:
                distractors = other_flags + random.sample(all_other_flags, min(needed, len(all_other_flags)))
            else:
                distractors = random.sample(other_flags, 3)

            options = [correct_answer] + distractors[:3]
            random.shuffle(options)
            explanation = f"Flag [bold green]{target_flag}[/bold green] in {target['name']}: {flag_desc}"

            return {
                "type": chosen_type,
                "card_id": target["id"],
                "category": target["category"],
                "question": question_text,
                "options": options,
                "correct_index": options.index(correct_answer),
                "correct_value": correct_answer,
                "explanation": explanation,
                "hint": f"Think about common single-letter Linux flag conventions.",
            }

    def generate_quiz_session(
        self,
        count: int = 10,
        category: Optional[str] = None,
        difficulty: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Generate a complete series of unique quiz questions."""
        questions: List[Dict[str, Any]] = []
        seen_cards = set()

        # Try to vary target cards
        attempts = 0
        max_attempts = count * 4

        while len(questions) < count and attempts < max_attempts:
            attempts += 1
            q = self.generate_quiz_question(category=category, difficulty=difficulty)
            if not q:
                break
            if q["card_id"] not in seen_cards or len(seen_cards) >= len(self.commands):
                seen_cards.add(q["card_id"])
                questions.append(q)

        return questions

    @staticmethod
    def normalize_command(cmd_str: str) -> str:
        """Normalize whitespace, quotes, and common terminal variances."""
        s = cmd_str.strip()
        # Normalize double/single quotes
        s = s.replace('"', "'")
        # Collapse multiple spaces
        s = re.sub(r"\s+", " ", s)
        # Normalize spaces around pipe and redirects
        s = re.sub(r"\s*\|\s*", " | ", s)
        s = re.sub(r"\s*>>\s*", " >> ", s)
        s = re.sub(r"\s*>\s*", " > ", s)
        return s.strip()

    def evaluate_challenge_answer(self, card_id: str, user_answer: str) -> Tuple[bool, str]:
        """
        Evaluate user command input against the card's challenge.
        Returns (is_correct, feedback_message).
        """
        card = self.command_map.get(card_id)
        if not card or "challenge" not in card:
            return False, "Challenge not found for this command."

        challenge = card["challenge"]
        user_norm = self.normalize_command(user_answer)
        canonical = challenge.get("canonical", "")
        canonical_norm = self.normalize_command(canonical)

        # Exact normalized match
        if user_norm == canonical_norm:
            return True, f"Perfect match! Standard command: [bold green]{canonical}[/bold green]"

        # Check pre-defined alternatives
        for alt in challenge.get("alternatives", []):
            if user_norm == self.normalize_command(alt):
                return True, f"Correct! (Accepted alternative for [bold green]{canonical}[/bold green])"

        # Check base command name
        user_parts = user_norm.split()
        canon_parts = canonical_norm.split()

        if not user_parts:
            return False, "No command entered."

        base_cmd_user = user_parts[0]
        base_cmd_canon = canon_parts[0]

        # Sudo tolerance
        if base_cmd_user == "sudo" and len(user_parts) > 1:
            base_cmd_user = user_parts[1]
        if base_cmd_canon == "sudo" and len(canon_parts) > 1:
            base_cmd_canon = canon_parts[1]

        if base_cmd_user != base_cmd_canon:
            return False, f"Incorrect command tool: used '{user_parts[0]}' instead of '{base_cmd_canon}'."

        # Check required keywords
        keywords = challenge.get("keywords", [])
        missing_kw = []
        for kw in keywords:
            kw_clean = kw.replace('"', "").replace("'", "")
            if kw_clean not in user_answer:
                missing_kw.append(kw)

        if missing_kw:
            return (
                False,
                f"Close, but missing required flags or arguments: [bold yellow]{', '.join(missing_kw)}[/bold yellow].\nExpected: [bold cyan]{canonical}[/bold cyan]",
            )

        # If all keywords were present and base command matched
        return True, f"Well done! Effective command: [bold green]{canonical}[/bold green]"
