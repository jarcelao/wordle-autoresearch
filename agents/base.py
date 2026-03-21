"""Base agent interface for Wordle."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class GuessResult:
    """Result of a single guess."""
    guess: str
    feedback: List[Tuple[str, str]]  # (letter, status) pairs


class Agent(ABC):
    """
    Abstract base class for Wordle agents.
    
    Agents must implement make_guess() to receive feedback history
    and return their next 5-letter guess.
    """
    
    @abstractmethod
    def make_guess(self, history: List[GuessResult]) -> str:
        """
        Make the next guess based on feedback history.
        
        Args:
            history: List of previous guesses and their feedback.
                    Empty list on first guess.
        
        Returns:
            A 5-letter word guess.
        """
        pass
    
    def reset(self) -> None:
        """Reset agent state for a new game. Override if needed."""
        pass