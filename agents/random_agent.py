"""Random agent that guesses randomly from a word pool."""

import random
from typing import List, Optional

from agents.base import Agent, GuessResult


class RandomAgent(Agent):
    """Example agent that guesses random 5-letter words."""
    
    def __init__(self, word_pool: Optional[List[str]] = None):
        self.word_pool = word_pool or [
            "apple", "beach", "crane", "dance", "eagle",
            "flame", "grape", "house", "image", "jolly"
        ]
    
    def make_guess(self, history: List[GuessResult]) -> str:
        """Make a random guess."""
        return random.choice(self.word_pool)