"""
Comprehensive test suite for the Linux Terminal Command Flashcard app.
"""

import os
import tempfile
import unittest
from pathlib import Path

from linux_flashcards.data import CATEGORIES, COMMANDS, COMMAND_MAP, DIFFICULTIES
from linux_flashcards.engine import FlashcardEngine
from linux_flashcards.storage import BOX_INTERVALS, ProgressStorage


class TestDatabaseIntegrity(unittest.TestCase):
    """Test validity and schema conformance of the commands dataset."""

    def test_database_not_empty(self):
        self.assertGreaterEqual(len(COMMANDS), 60, "Should have at least 60 curated Linux commands")

    def test_unique_command_ids(self):
        ids = [c["id"] for c in COMMANDS]
        self.assertEqual(len(ids), len(set(ids)), f"Duplicate command IDs found: {[x for x in ids if ids.count(x) > 1]}")

    def test_command_schema_fields(self):
        required_keys = ["id", "name", "category", "difficulty", "summary", "description", "syntax"]
        for cmd in COMMANDS:
            for k in required_keys:
                self.assertIn(k, cmd, f"Command {cmd.get('id')} missing required key '{k}'")
                self.assertTrue(cmd[k], f"Command {cmd.get('id')} has empty value for '{k}'")

            # Category check
            self.assertIn(cmd["category"], CATEGORIES, f"Command {cmd['id']} has invalid category: {cmd['category']}")

            # Difficulty check
            self.assertIn(cmd["difficulty"], DIFFICULTIES, f"Command {cmd['id']} has invalid difficulty: {cmd['difficulty']}")

            # Challenge check if present
            if "challenge" in cmd:
                ch = cmd["challenge"]
                self.assertIn("scenario", ch, f"Command {cmd['id']} challenge missing 'scenario'")
                self.assertIn("canonical", ch, f"Command {cmd['id']} challenge missing 'canonical'")

    def test_command_map_matches(self):
        self.assertEqual(len(COMMAND_MAP), len(COMMANDS))
        for cmd in COMMANDS:
            self.assertIn(cmd["id"], COMMAND_MAP)
            self.assertEqual(COMMAND_MAP[cmd["id"]]["name"], cmd["name"])


class TestStorageAndSpacedRepetition(unittest.TestCase):
    """Test progress persistence and Leitner box promotion/demotion."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.storage_file = Path(self.temp_dir.name) / "test_progress.json"
        self.storage = ProgressStorage(self.storage_file)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_initial_state(self):
        card = self.storage.get_card("grep")
        self.assertEqual(card["box"], 1)
        self.assertEqual(card["total_reviews"], 0)
        self.assertFalse(card["bookmarked"])

    def test_review_promotions(self):
        # 'good' rating should promote by 1 box
        self.storage.record_review("grep", "good")
        c1 = self.storage.get_card("grep")
        self.assertEqual(c1["box"], 2)
        self.assertEqual(c1["correct_count"], 1)
        self.assertIsNotNone(c1["next_review"])

        # 'easy' rating should promote by 2 boxes
        self.storage.record_review("grep", "easy")
        c2 = self.storage.get_card("grep")
        self.assertEqual(c2["box"], 4)
        self.assertEqual(c2["correct_count"], 2)

        # 'hard' rating keeps current box
        self.storage.record_review("grep", "hard")
        c3 = self.storage.get_card("grep")
        self.assertEqual(c3["box"], 4)

        # 'again' rating resets to box 1
        self.storage.record_review("grep", "again")
        c4 = self.storage.get_card("grep")
        self.assertEqual(c4["box"], 1)

    def test_bookmark_toggle(self):
        state1 = self.storage.toggle_bookmark("ls")
        self.assertTrue(state1)
        self.assertTrue(self.storage.get_card("ls")["bookmarked"])

        state2 = self.storage.toggle_bookmark("ls")
        self.assertFalse(state2)
        self.assertFalse(self.storage.get_card("ls")["bookmarked"])

    def test_persistence_across_reloads(self):
        self.storage.record_review("find", "good")
        self.storage.toggle_bookmark("find")
        self.storage.set_notes("find", "Remember to quote wildcards like '*.log'")

        # New instance pointing to same file
        reloaded = ProgressStorage(self.storage_file)
        card = reloaded.get_card("find")
        self.assertEqual(card["box"], 2)
        self.assertTrue(card["bookmarked"])
        self.assertEqual(card["notes"], "Remember to quote wildcards like '*.log'")

    def test_summary_stats(self):
        self.storage.record_review("cat", "good")
        self.storage.record_quiz_answer(True)
        self.storage.record_quiz_answer(False)
        self.storage.record_challenge_attempt(True)

        stats = self.storage.get_summary_stats(len(COMMANDS))
        self.assertEqual(stats["reviewed_count"], 1)
        self.assertEqual(stats["quiz_answered"], 2)
        self.assertEqual(stats["quiz_correct"], 1)
        self.assertEqual(stats["quiz_accuracy"], 50.0)
        self.assertEqual(stats["challenge_attempted"], 1)
        self.assertEqual(stats["challenge_solved"], 1)
        self.assertEqual(stats["challenge_rate"], 100.0)


class TestEngineFeatures(unittest.TestCase):
    """Test engine filtering, quiz generation, and challenge matching."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.storage_file = Path(self.temp_dir.name) / "test_progress.json"
        self.storage = ProgressStorage(self.storage_file)
        self.engine = FlashcardEngine(self.storage)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_deck_filtering_by_category(self):
        deck = self.engine.get_deck(category="Networking & Web", shuffle=False)
        self.assertTrue(len(deck) > 0)
        for card in deck:
            self.assertEqual(card["category"], "Networking & Web")

    def test_deck_filtering_by_difficulty(self):
        deck = self.engine.get_deck(difficulty="Beginner", shuffle=False)
        self.assertTrue(len(deck) > 0)
        for card in deck:
            self.assertEqual(card["difficulty"], "Beginner")

    def test_search_commands(self):
        # By exact name
        results = self.engine.search_commands("grep")
        self.assertTrue(len(results) > 0)
        self.assertEqual(results[0]["name"], "grep")

        # By flag/purpose keyword
        results_kw = self.engine.search_commands("recursive")
        self.assertTrue(len(results_kw) > 0)

    def test_quiz_generator(self):
        q = self.engine.generate_quiz_question()
        self.assertIsNotNone(q)
        self.assertIn("question", q)
        self.assertEqual(len(q["options"]), 4)
        self.assertIn(q["correct_index"], [0, 1, 2, 3])
        self.assertEqual(q["options"][q["correct_index"]], q["correct_value"])

    def test_quiz_session(self):
        session = self.engine.generate_quiz_session(count=5)
        self.assertEqual(len(session), 5)
        for q in session:
            self.assertEqual(len(q["options"]), 4)
            self.assertTrue(0 <= q["correct_index"] < 4)

    def test_challenge_evaluation_exact(self):
        ok, msg = self.engine.evaluate_challenge_answer("pwd", "pwd -P")
        self.assertTrue(ok)

    def test_challenge_evaluation_tolerances(self):
        # find command with alternate quotes and spaces
        ok, msg = self.engine.evaluate_challenge_answer("find", "find /var/log -type f -name '*.log' -mtime -7")
        self.assertTrue(ok)

        # wrong tool
        ok_wrong, msg_wrong = self.engine.evaluate_challenge_answer("pwd", "ls -la")
        self.assertFalse(ok_wrong)
        self.assertIn("Incorrect command tool", msg_wrong)


class TestCLILaunch(unittest.TestCase):
    """Test CLI app lifecycle and menu rendering."""

    def test_main_menu_quit(self):
        from unittest.mock import patch
        from linux_flashcards.cli import FlashcardApp

        with tempfile.TemporaryDirectory() as tmpdir:
            profile_path = Path(tmpdir) / "profile.json"
            app = FlashcardApp(storage_path=profile_path)
            with patch("linux_flashcards.cli.Prompt.ask", return_value="q"):
                # Should not raise any NameError or exception
                app.main_menu()


if __name__ == "__main__":
    unittest.main()
