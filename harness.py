#!/usr/bin/env python3
"""
Wordle Agent Evaluation Harness (Simplified)

Runs batch evaluation against train/test word sets.
Output: JSON only (for machine processing).
"""

import json
import statistics
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import argparse

from wordle import (
    get_feedback,
    is_valid_guess,
    MAX_ATTEMPTS,
    fetch_wordle_word,
)
from agents.base import Agent, GuessResult
from agents.random_agent import RandomAgent
from agents.simple_agent import SimpleAgent

# Agent registry - add custom agents here
AGENT_REGISTRY = {
    "random": RandomAgent,
    "simple": SimpleAgent,
}


@dataclass
class GameResult:
    """Result of a single game."""

    target_word: str
    won: bool
    attempts: int
    guess_history: List[GuessResult] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "target_word": self.target_word,
            "won": self.won,
            "attempts": self.attempts,
            "guess_history": [
                {"guess": g.guess, "feedback": g.feedback} for g in self.guess_history
            ],
        }


@dataclass
class EvaluationResult:
    """Full evaluation results."""

    mode: str  # 'train' or 'test'
    timestamp: str
    total_games: int
    wins: int
    losses: int
    win_rate: float
    avg_attempts: float
    avg_attempts_on_win: float
    attempts_distribution: Dict[str, int]
    games: List[GameResult]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "mode": self.mode,
            "timestamp": self.timestamp,
            "total_games": self.total_games,
            "wins": self.wins,
            "losses": self.losses,
            "win_rate": self.win_rate,
            "avg_attempts": self.avg_attempts,
            "avg_attempts_on_win": self.avg_attempts_on_win,
            "attempts_distribution": self.attempts_distribution,
            "games": [g.to_dict() for g in self.games],
        }


class WordleEvaluator:
    """Evaluates agents on Wordle games."""

    def __init__(
        self,
        train_words: Optional[List[str]] = None,
        test_words: Optional[List[str]] = None,
        cache_dir: Optional[Path] = None,
    ):
        """
        Args:
            train_words: Fixed words for training/development evaluation.
            test_words: Fixed words for testing (or None to use API).
            cache_dir: Directory to cache API words.
        """
        self.train_words = train_words or []
        self.test_words = test_words
        self.cache_dir = Path(cache_dir) if cache_dir else Path("temp/cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._api_cache: List[str] = []

    def _load_or_fetch_words(self, count: int) -> List[str]:
        """Load from cache or fetch from API."""
        cache_file = self.cache_dir / "test_words.txt"

        if cache_file.exists():
            with open(cache_file) as f:
                self._api_cache = [w.strip() for w in f if w.strip()]

        needed = count - len(self._api_cache)
        if needed > 0:
            print(f"Fetching {needed} words from API...", file=sys.stderr)
            for _ in range(needed):
                try:
                    word = fetch_wordle_word()
                    self._api_cache.append(word)
                except Exception as e:
                    print(f"Failed to fetch word: {e}", file=sys.stderr)
                    break
            with open(cache_file, "w") as f:
                for w in self._api_cache:
                    f.write(f"{w}\n")

        return self._api_cache[:count]

    def evaluate_train(self, agent: Agent) -> EvaluationResult:
        """Evaluate on training set (fixed words)."""
        if not self.train_words:
            raise ValueError("No train_words configured")

        return self._run_evaluation(agent, self.train_words, mode="train")

    def evaluate_test(self, agent: Agent, num_games: int) -> EvaluationResult:
        """Evaluate on test set (API words)."""
        if self.test_words:
            words = self.test_words[:num_games]
        else:
            words = self._load_or_fetch_words(num_games)

        return self._run_evaluation(agent, words, mode="test")

    def _run_evaluation(
        self, agent: Agent, words: List[str], mode: str
    ) -> EvaluationResult:
        """Run evaluation on a list of words."""
        results: List[GameResult] = []

        for target in words:
            agent.reset()
            history: List[GuessResult] = []
            won = False
            attempts = 0

            for attempt in range(1, MAX_ATTEMPTS + 1):
                guess = agent.make_guess(history)

                if not is_valid_guess(guess):
                    raise ValueError(f"Invalid guess from agent: {guess}")

                feedback = get_feedback(guess, target)
                history.append(GuessResult(guess=guess, feedback=feedback))

                if guess == target:
                    won = True
                    attempts = attempt
                    break
                attempts = attempt

            if not won:
                attempts = MAX_ATTEMPTS

            results.append(
                GameResult(
                    target_word=target,
                    won=won,
                    attempts=attempts,
                    guess_history=history,
                )
            )

        return self._compute_result(results, mode)

    def _compute_result(self, results: List[GameResult], mode: str) -> EvaluationResult:
        """Compute aggregate statistics."""
        total = len(results)
        wins = sum(1 for r in results if r.won)
        losses = total - wins
        win_rate = wins / total if total > 0 else 0.0

        attempts_dist: Dict[str, int] = {}
        for i in range(1, MAX_ATTEMPTS + 1):
            attempts_dist[str(i)] = 0

        total_attempts = 0
        win_attempts = []

        for r in results:
            attempts = r.attempts if r.won else MAX_ATTEMPTS
            total_attempts += attempts
            attempts_dist[str(attempts)] = attempts_dist.get(str(attempts), 0) + 1
            if r.won:
                win_attempts.append(r.attempts)

        avg_attempts = total_attempts / total if total > 0 else 0.0
        avg_attempts_on_win = statistics.mean(win_attempts) if win_attempts else 0.0

        return EvaluationResult(
            mode=mode,
            timestamp=datetime.now().isoformat(),
            total_games=total,
            wins=wins,
            losses=losses,
            win_rate=win_rate,
            avg_attempts=avg_attempts,
            avg_attempts_on_win=avg_attempts_on_win,
            attempts_distribution=attempts_dist,
            games=results,
        )


def main():
    parser = argparse.ArgumentParser(description="Wordle Agent Evaluation Harness")
    parser.add_argument(
        "--agent",
        choices=list(AGENT_REGISTRY.keys()),
        default="simple",
        help="Agent to evaluate",
    )
    parser.add_argument(
        "--mode",
        choices=["train", "test"],
        default="train",
        help="Evaluation mode: train (fixed words) or test (API)",
    )
    parser.add_argument(
        "--games", type=int, default=100, help="Number of games (for test mode)"
    )
    parser.add_argument(
        "--word-list",
        default="temp/train_words.txt",
        help="Word list file (for train mode)",
    )
    parser.add_argument(
        "--cache", default="temp/api_cache", help="Cache directory for API words"
    )
    parser.add_argument("--output", "-o", required=True, help="Output JSON file")

    args = parser.parse_args()

    agent_class = AGENT_REGISTRY[args.agent]
    agent = agent_class()

    train_words = None
    test_words = None

    if args.mode == "train":
        if not Path(args.word_list).exists():
            default_words = [
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
            ]
            Path(args.word_list).parent.mkdir(parents=True, exist_ok=True)
            with open(args.word_list, "w") as f:
                for w in default_words:
                    f.write(f"{w}\n")

        with open(args.word_list) as f:
            train_words = [w.strip() for w in f if w.strip()]

    evaluator = WordleEvaluator(
        train_words=train_words, test_words=test_words, cache_dir=Path(args.cache)
    )

    if args.mode == "train":
        result = evaluator.evaluate_train(agent)
    else:
        result = evaluator.evaluate_test(agent, num_games=args.games)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(result.to_dict(), f, indent=2)

    print(f"Mode: {result.mode}", file=sys.stderr)
    print(f"Games: {result.total_games}", file=sys.stderr)
    print(f"Wins: {result.wins} ({result.win_rate:.1%})", file=sys.stderr)
    print(f"Avg attempts: {result.avg_attempts:.2f}", file=sys.stderr)
    print(f"Results saved to: {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
