"""Template for creating a custom Wordle agent.

Copy this file and implement your agent logic.
"""

from typing import List

from agents.base import Agent, GuessResult


class MyAgent(Agent):
    """
    Your custom Wordle agent.

    Implement make_guess() to return a 5-letter word based on feedback history.
    """

    def __init__(self):
        # Initialize any state you need
        self.word_list = [
            "apple",
            "beach",
            "crane",
            "dance",
            "eagle",
            # Add more words as needed
        ]

    def reset(self) -> None:
        """Reset state for a new game. Called before each game."""
        # Reset any per-game state here
        pass

    def make_guess(self, history: List[GuessResult]) -> str:
        """
        Make the next guess based on feedback history.

        Args:
            history: List of (guess, feedback) from previous attempts.
                    Empty list on first guess.

            Each feedback is a list of (letter, status) where:
            - status == 'correct': right letter, right position (green)
            - status == 'present': right letter, wrong position (yellow)
            - status == 'absent': letter not in word (gray)

        Returns:
            A 5-letter word guess.
        """
        if not history:
            # First guess - can be any strategy
            return "crane"

        # Example: Use last feedback to filter words
        # last = history[-1]

        # Your logic here:
        # - Eliminate words with 'absent' letters
        # - Keep words with 'correct' letters in position
        # - Consider 'present' letters (in word but wrong position)

        # For now, just return a random word from your list
        import random

        return random.choice(self.word_list)


# Register your agent so harness can load it
AGENT_REGISTRY = {
    "my_agent": MyAgent,
    # Add more variants here
}
