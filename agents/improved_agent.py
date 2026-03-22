"""Improved agent with full word list and proper feedback handling."""

from typing import List, Set, Dict
from pathlib import Path
from collections import Counter

from agents.base import Agent, GuessResult


class ImprovedAgent(Agent):
    """Improved agent that uses full dictionary, proper feedback handling, and letter frequency."""

    def __init__(self):
        # Load full valid word list (lowercase for Wordle compatibility)
        word_file = Path(__file__).parent.parent / "valid-words.txt"
        with open(word_file) as f:
            self.all_words = [w.strip().lower() for w in f if w.strip()]
        
        # Precompute letter frequencies across all words
        self.letter_freq: Dict[str, int] = Counter()
        for word in self.all_words:
            self.letter_freq.update(word)
        
        # Best starting words (pre-computed optimal for information gain)
        self.starting_words = ["slate", "crate", "sauce", "reate", "carve", "least", "tales"]
        
        self.remaining: List[str] = []
        # Track constraints from feedback
        self.correct_positions: dict = {}  # position -> letter
        self.absent_letters: Set[str] = set()  # letters confirmed absent
        # For each position, track letters that are known to be NOT there (present elsewhere)
        self.forbidden_pos: Dict[int, Set[str]] = {}
        # Track which letters are known to be in the word somewhere (present in wrong position)
        self.present_letters: Set[str] = set()  # letters that are in word but not at known positions

    def reset(self) -> None:
        self.remaining = self.all_words.copy()
        self.correct_positions = {}
        self.absent_letters = set()
        self.forbidden_pos = {}
        self.present_letters = set()

    def make_guess(self, history: List[GuessResult]) -> str:
        if not history:
            # Use first starting word - slate is known to be excellent
            return "slate"

        # Update constraints from all feedback history
        for h in history:
            self._update_constraints(h)

        # Filter remaining words based on constraints
        self._filter_remaining()

        if not self.remaining:
            self.remaining = self.all_words.copy()

        # Return the best word based on letter frequency
        return self._select_best_word()

    def _select_best_word(self) -> str:
        """Select the word with the highest letter frequency score."""
        if not self.remaining:
            return "slate"
        
        # Score each word by letter frequency (prioritize common letters)
        best_word = None
        best_score = -1
        
        for word in self.remaining:
            score = 0
            seen = set()
            for letter in word:
                if letter not in seen:
                    score += self.letter_freq.get(letter, 0)
                    seen.add(letter)
            if score > best_score:
                best_score = score
                best_word = word
        
        return best_word if best_word else self.remaining[0]

    def _update_constraints(self, last: GuessResult) -> None:
        """Update constraints based on feedback."""
        guess = last.guess.lower()
        feedback = last.feedback
        
        # Track letter statuses for handling duplicates
        letter_statuses: Dict[str, List[str]] = {}
        for letter, status in feedback:
            letter = letter.lower()
            if letter not in letter_statuses:
                letter_statuses[letter] = []
            letter_statuses[letter].append(status)

        # Process each position
        for i, (letter, status) in enumerate(feedback):
            letter = letter.lower()
            if status == "correct":
                self.correct_positions[i] = letter
            elif status == "absent":
                # Check if this SAME letter appears as correct or present elsewhere
                other_statuses = letter_statuses.get(letter, [])
                has_present = "present" in other_statuses
                has_correct = "correct" in other_statuses
                
                if not has_present and not has_correct:
                    self.absent_letters.add(letter)
                else:
                    if i not in self.forbidden_pos:
                        self.forbidden_pos[i] = set()
                    self.forbidden_pos[i].add(letter)
            elif status == "present":
                # Letter must be in word somewhere (just mark as present)
                self.present_letters.add(letter)
                # Also mark this position as forbidden for this letter
                if i not in self.forbidden_pos:
                    self.forbidden_pos[i] = set()
                self.forbidden_pos[i].add(letter)

    def _filter_remaining(self) -> None:
        """Filter remaining words based on current constraints."""
        new_remaining = []
        for word in self.remaining:
            if self._word_matches_constraints(word):
                new_remaining.append(word)
        self.remaining = new_remaining

    def _word_matches_constraints(self, word: str) -> bool:
        """Check if word matches all constraints."""
        # Check correct positions first
        for pos, letter in self.correct_positions.items():
            if word[pos] != letter:
                return False

        # Check forbidden positions (present but not at this position)
        for pos, letters in self.forbidden_pos.items():
            if word[pos] in letters:
                return False

        # Check absent letters
        for letter in self.absent_letters:
            if letter in word:
                return False

        # Check required present letters - just verify each is in word at least once
        for letter in self.present_letters:
            if letter not in word:
                return False

        return True
