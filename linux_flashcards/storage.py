"""
Storage and Spaced Repetition (Leitner System) manager for Linux Flashcards.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

# Spaced Repetition interval mapping by Leitner Box (in days)
BOX_INTERVALS = {
    1: 1,    # Box 1: 1 day
    2: 3,    # Box 2: 3 days
    3: 7,    # Box 3: 7 days
    4: 14,   # Box 4: 14 days
    5: 30,   # Box 5: 30 days (Mastered)
}

DEFAULT_STORAGE_DIR = Path.home() / ".config" / "linux_flashcards"
DEFAULT_STORAGE_FILE = DEFAULT_STORAGE_DIR / "progress.json"
LOCAL_FALLBACK_FILE = Path(".linux_flashcards_progress.json")


class ProgressStorage:
    """Manages persistent learning state and spaced repetition scheduling."""

    def __init__(self, file_path: Optional[Path | str] = None):
        if file_path:
            self.file_path = Path(file_path)
        else:
            try:
                DEFAULT_STORAGE_DIR.mkdir(parents=True, exist_ok=True)
                self.file_path = DEFAULT_STORAGE_FILE
            except (OSError, PermissionError):
                self.file_path = LOCAL_FALLBACK_FILE

        self.data: Dict[str, Any] = {
            "meta": {
                "created_at": datetime.now(timezone.utc).isoformat(),
                "last_active": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                "streak_days": 1,
            },
            "stats": {
                "total_reviews": 0,
                "quiz_questions_answered": 0,
                "quiz_correct_answers": 0,
                "challenges_attempted": 0,
                "challenges_solved": 0,
            },
            "cards": {},
        }
        self.load()

    def load(self) -> None:
        """Load state from JSON file if present."""
        if not self.file_path.exists():
            return
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                loaded = json.load(f)
                if isinstance(loaded, dict):
                    self.data["meta"].update(loaded.get("meta", {}))
                    self.data["stats"].update(loaded.get("stats", {}))
                    self.data["cards"] = loaded.get("cards", {})
            self._update_streak()
        except Exception:
            # Fall back gracefully to fresh state if corrupted
            pass

    def save(self) -> None:
        """Persist current state to JSON file."""
        try:
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
        except (OSError, PermissionError):
            try:
                with open(LOCAL_FALLBACK_FILE, "w", encoding="utf-8") as f:
                    json.dump(self.data, f, indent=2, ensure_ascii=False)
            except Exception:
                pass

    def _update_streak(self) -> None:
        """Update daily active streak counter."""
        today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        last_active = self.data["meta"].get("last_active", "")
        if not last_active:
            self.data["meta"]["last_active"] = today_str
            self.data["meta"]["streak_days"] = 1
            return

        if last_active == today_str:
            return

        try:
            last_date = datetime.strptime(last_active, "%Y-%m-%d").date()
            today_date = datetime.strptime(today_str, "%Y-%m-%d").date()
            delta = (today_date - last_date).days
            if delta == 1:
                self.data["meta"]["streak_days"] = self.data["meta"].get("streak_days", 0) + 1
            elif delta > 1:
                self.data["meta"]["streak_days"] = 1
            self.data["meta"]["last_active"] = today_str
        except Exception:
            self.data["meta"]["last_active"] = today_str
            self.data["meta"]["streak_days"] = 1

    def get_card(self, card_id: str) -> Dict[str, Any]:
        """Retrieve progress for a single card or create default record."""
        if card_id not in self.data["cards"]:
            self.data["cards"][card_id] = {
                "box": 1,
                "total_reviews": 0,
                "correct_count": 0,
                "incorrect_count": 0,
                "last_reviewed": None,
                "next_review": None,
                "bookmarked": False,
                "notes": "",
            }
        return self.data["cards"][card_id]

    def record_review(self, card_id: str, rating: str) -> Dict[str, Any]:
        """
        Record user review for card.
        rating can be:
        - 'easy': advance 2 boxes (max 5)
        - 'good': advance 1 box (max 5)
        - 'hard': remain in current box
        - 'again': reset to box 1
        """
        card = self.get_card(card_id)
        now = datetime.now(timezone.utc)
        current_box = card.get("box", 1)

        is_correct = rating in ("easy", "good")
        if rating == "easy":
            new_box = min(5, current_box + 2)
        elif rating == "good":
            new_box = min(5, current_box + 1)
        elif rating == "hard":
            new_box = current_box
        else:  # 'again' or failure
            new_box = 1

        card["box"] = new_box
        card["total_reviews"] = card.get("total_reviews", 0) + 1
        if is_correct:
            card["correct_count"] = card.get("correct_count", 0) + 1
        else:
            card["incorrect_count"] = card.get("incorrect_count", 0) + 1

        card["last_reviewed"] = now.isoformat()
        interval_days = BOX_INTERVALS.get(new_box, 1)
        next_due = now + timedelta(days=interval_days)
        card["next_review"] = next_due.isoformat()

        self.data["stats"]["total_reviews"] = self.data["stats"].get("total_reviews", 0) + 1
        self._update_streak()
        self.save()
        return card

    def toggle_bookmark(self, card_id: str) -> bool:
        """Toggle favorite bookmark on a card."""
        card = self.get_card(card_id)
        card["bookmarked"] = not card.get("bookmarked", False)
        self.save()
        return card["bookmarked"]

    def set_notes(self, card_id: str, notes: str) -> None:
        """Save custom user notes on a card."""
        card = self.get_card(card_id)
        card["notes"] = notes
        self.save()

    def record_quiz_answer(self, is_correct: bool) -> None:
        """Track individual quiz answer result."""
        self.data["stats"]["quiz_questions_answered"] = self.data["stats"].get("quiz_questions_answered", 0) + 1
        if is_correct:
            self.data["stats"]["quiz_correct_answers"] = self.data["stats"].get("quiz_correct_answers", 0) + 1
        self._update_streak()
        self.save()

    def record_challenge_attempt(self, is_success: bool) -> None:
        """Track interactive terminal command challenge result."""
        self.data["stats"]["challenges_attempted"] = self.data["stats"].get("challenges_attempted", 0) + 1
        if is_success:
            self.data["stats"]["challenges_solved"] = self.data["stats"].get("challenges_solved", 0) + 1
        self._update_streak()
        self.save()

    def is_due_for_review(self, card_id: str) -> bool:
        """Check if a card's review interval has expired or if it is unreviewed."""
        card = self.get_card(card_id)
        next_review = card.get("next_review")
        if not next_review:
            return True
        try:
            due_dt = datetime.fromisoformat(next_review)
            return datetime.now(timezone.utc) >= due_dt
        except Exception:
            return True

    def get_due_card_ids(self) -> List[str]:
        """Return list of card IDs currently due for review."""
        return [cid for cid, card in self.data["cards"].items() if self.is_due_for_review(cid)]

    def get_summary_stats(self, total_database_cards: int) -> Dict[str, Any]:
        """Compute holistic learning statistics for dashboard."""
        cards = self.data["cards"]
        box_distribution = {b: 0 for b in range(1, 6)}
        reviewed_count = len(cards)
        bookmarked_count = 0
        total_correct = 0
        total_attempts = 0

        for card in cards.values():
            box = card.get("box", 1)
            box_distribution[box] = box_distribution.get(box, 0) + 1
            if card.get("bookmarked"):
                bookmarked_count += 1
            total_correct += card.get("correct_count", 0)
            total_attempts += card.get("total_reviews", 0)

        unseen_count = max(0, total_database_cards - reviewed_count)
        mastered_count = box_distribution.get(5, 0)

        card_accuracy = round((total_correct / total_attempts * 100), 1) if total_attempts > 0 else 0.0

        quiz_answered = self.data["stats"].get("quiz_questions_answered", 0)
        quiz_correct = self.data["stats"].get("quiz_correct_answers", 0)
        quiz_accuracy = round((quiz_correct / quiz_answered * 100), 1) if quiz_answered > 0 else 0.0

        challenge_attempted = self.data["stats"].get("challenges_attempted", 0)
        challenge_solved = self.data["stats"].get("challenges_solved", 0)
        challenge_rate = round((challenge_solved / challenge_attempted * 100), 1) if challenge_attempted > 0 else 0.0

        # Mastery percentage (weight boxes 1..5)
        # Unseen = 0 pts, Box 1 = 20%, Box 2 = 40%, Box 3 = 60%, Box 4 = 80%, Box 5 = 100%
        total_points = sum(count * (b * 20) for b, count in box_distribution.items())
        max_points = total_database_cards * 100
        overall_mastery = round((total_points / max_points * 100), 1) if max_points > 0 else 0.0

        return {
            "total_database_cards": total_database_cards,
            "reviewed_count": reviewed_count,
            "unseen_count": unseen_count,
            "mastered_count": mastered_count,
            "bookmarked_count": bookmarked_count,
            "box_distribution": box_distribution,
            "overall_mastery": overall_mastery,
            "card_accuracy": card_accuracy,
            "total_card_reviews": total_attempts,
            "quiz_answered": quiz_answered,
            "quiz_correct": quiz_correct,
            "quiz_accuracy": quiz_accuracy,
            "challenge_attempted": challenge_attempted,
            "challenge_solved": challenge_solved,
            "challenge_rate": challenge_rate,
            "streak_days": self.data["meta"].get("streak_days", 1),
            "last_active": self.data["meta"].get("last_active", "Today"),
        }

    def reset_progress(self) -> None:
        """Clear all stored progress and reset stats."""
        self.data["cards"] = {}
        self.data["stats"] = {
            "total_reviews": 0,
            "quiz_questions_answered": 0,
            "quiz_correct_answers": 0,
            "challenges_attempted": 0,
            "challenges_solved": 0,
        }
        self.data["meta"]["streak_days"] = 1
        self.data["meta"]["last_active"] = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        self.save()
