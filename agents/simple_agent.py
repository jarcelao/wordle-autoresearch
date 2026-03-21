"""Simple agent that uses feedback to filter possible words."""

from typing import List

from agents.base import Agent, GuessResult


class SimpleAgent(Agent):
    """Example agent that uses feedback to filter a word list."""

    def __init__(self):
        self.all_words = [
            "apple",
            "beach",
            "crane",
            "dance",
            "eagle",
            "flame",
            "grape",
            "house",
            "image",
            "jolly",
            "kneel",
            "lemon",
            "melon",
            "noble",
            "ocean",
            "peace",
            "queen",
            "rider",
            "sunny",
            "table",
            "uncle",
            "vivid",
            "water",
            "yeast",
            "zebra",
        ]
        self.remaining: List[str] = []

    def reset(self) -> None:
        self.remaining = self.all_words.copy()

    def make_guess(self, history: List[GuessResult]) -> str:
        if not history:
            return "crane"  # Good starting word

        # Filter based on last feedback
        last = history[-1]
        feedback = last.feedback

        new_remaining = []
        for word in self.remaining:
            valid = True
            for i, (letter, status) in enumerate(feedback):
                if status == "absent" and letter in word:
                    valid = False
                    break
                if status == "correct" and word[i] != letter:
                    valid = False
                    break
            if valid:
                new_remaining.append(word)

        self.remaining = new_remaining if new_remaining else self.all_words
        return self.remaining[0] if self.remaining else "crane"
