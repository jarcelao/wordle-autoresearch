"""Unit tests for harness.py"""

import sys
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open
from datetime import datetime

from wordle import MAX_ATTEMPTS
from harness import (
    GameResult,
    EvaluationResult,
    WordleEvaluator,
    main,
)
from agents.base import Agent, GuessResult


class TestGameResult:
    """Tests for GameResult dataclass"""

    def test_game_result_creation(self):
        """Test creating a GameResult"""
        result = GameResult(target_word="crane", won=True, attempts=3, guess_history=[])
        assert result.target_word == "crane"
        assert result.won is True
        assert result.attempts == 3

    def test_to_dict(self):
        """Test converting to dictionary"""
        history = [GuessResult(guess="crane", feedback=[("c", "correct")])]
        result = GameResult(
            target_word="crane", won=True, attempts=1, guess_history=history
        )
        d = result.to_dict()
        assert d["target_word"] == "crane"
        assert d["won"] is True
        assert d["attempts"] == 1
        assert len(d["guess_history"]) == 1


class TestEvaluationResult:
    """Tests for EvaluationResult dataclass"""

    def test_evaluation_result_creation(self):
        """Test creating an EvaluationResult"""
        result = EvaluationResult(
            mode="train",
            timestamp=datetime.now().isoformat(),
            total_games=10,
            wins=7,
            losses=3,
            win_rate=0.7,
            avg_attempts=4.0,
            avg_attempts_on_win=3.5,
            attempts_distribution={"1": 1, "2": 2, "3": 4, "4": 3, "5": 0, "6": 0},
            games=[],
        )
        assert result.mode == "train"
        assert result.wins == 7
        assert result.win_rate == 0.7


class TestWordleEvaluator:
    """Tests for WordleEvaluator class"""

    def test_init(self):
        """Test evaluator initialization"""
        evaluator = WordleEvaluator(
            train_words=["apple", "beach"],
            test_words=["crane"],
            cache_dir=Path("temp/test_cache"),
        )
        assert evaluator.train_words == ["apple", "beach"]
        assert evaluator.test_words == ["crane"]
        assert evaluator.cache_dir == Path("temp/test_cache")

    def test_init_default_cache(self):
        """Test default cache directory"""
        evaluator = WordleEvaluator()
        assert evaluator.cache_dir == Path("temp/cache")

    def test_evaluate_train_no_words(self):
        """Test evaluate_train raises error with no train words"""
        evaluator = WordleEvaluator(train_words=[])
        agent = MagicMock(spec=Agent)
        with pytest.raises(ValueError, match="No train_words"):
            evaluator.evaluate_train(agent)

    def test_evaluate_train_single_game_win(self):
        """Test evaluation with a single winning game"""
        evaluator = WordleEvaluator(train_words=["crane"])

        agent = MagicMock(spec=Agent)
        agent.make_guess.return_value = "crane"

        result = evaluator.evaluate_train(agent)

        assert result.total_games == 1
        assert result.wins == 1
        assert result.losses == 0
        assert result.win_rate == 1.0
        assert result.avg_attempts == 1.0

    def test_evaluate_train_single_game_loss(self):
        """Test evaluation with a single losing game"""
        evaluator = WordleEvaluator(train_words=["crane"])

        agent = MagicMock(spec=Agent)
        agent.make_guess.return_value = "wrong"

        result = evaluator.evaluate_train(agent)

        assert result.total_games == 1
        assert result.wins == 0
        assert result.losses == 1
        assert result.win_rate == 0.0
        assert result.avg_attempts == MAX_ATTEMPTS

    def test_evaluate_train_multiple_games(self):
        """Test evaluation with multiple games"""
        evaluator = WordleEvaluator(train_words=["crane", "apple", "beach"])

        agent = MagicMock(spec=Agent)
        # Agent wins first game in 3 attempts, loses second, wins third in 2
        side_effects = [
            "wrong",
            "wrong",
            "crane",  # game 1: win on 3rd
            "wrong",
            "wrong",
            "wrong",
            "wrong",
            "wrong",
            "wrong",  # game 2: loss
            "wrong",
            "beach",  # game 3: win on 2nd
        ]
        agent.make_guess.side_effect = side_effects

        result = evaluator.evaluate_train(agent)

        assert result.total_games == 3
        assert result.wins == 2
        assert result.losses == 1

    @patch("harness.Path.exists")
    @patch("harness.open", new_callable=mock_open, read_data="word1\nword2\nword3\n")
    def test_load_or_fetch_words_from_cache(self, mock_file, mock_exists):
        """Test loading words from cache file"""
        mock_exists.return_value = True

        evaluator = WordleEvaluator(cache_dir=Path("temp/test_cache"))
        words = evaluator._load_or_fetch_words(3)

        assert words == ["word1", "word2", "word3"]


class TestMain:
    """Tests for harness main function"""

    @patch("harness.sys.stderr")
    @patch("harness.WordleEvaluator")
    @patch("harness.open", new_callable=mock_open)
    def test_main_train_mode(self, mock_file, mock_evaluator, mock_stderr):
        """Test main function with train mode - verify evaluator flow"""
        mock_instance = MagicMock()
        mock_result = MagicMock()
        # Use spec to make MagicMock behave like the actual object for string formatting
        mock_result.mode = "train"
        mock_result.total_games = 10
        mock_result.wins = 8
        mock_result.win_rate = 0.8
        mock_result.avg_attempts = 3.5
        mock_result.to_dict.return_value = {"mode": "train", "wins": 8}
        mock_instance.evaluate_train.return_value = mock_result
        mock_evaluator.return_value = mock_instance

        with patch.object(
            sys,
            "argv",
            ["harness", "--agent", "simple", "--mode", "train", "-o", "results.json"],
        ):
            main()

        # Verify evaluator was created and evaluate_train was called
        mock_evaluator.assert_called_once()
        mock_instance.evaluate_train.assert_called_once()
        # Verify JSON was written
        mock_file.assert_called()

    @patch("harness.sys.stderr")
    @patch("harness.WordleEvaluator")
    @patch("harness.open", new_callable=mock_open)
    def test_main_test_mode(self, mock_file, mock_evaluator, mock_stderr):
        """Test main function with test mode - verify num_games parameter"""
        mock_instance = MagicMock()
        mock_result = MagicMock()
        mock_result.mode = "test"
        mock_result.total_games = 50
        mock_result.wins = 40
        mock_result.win_rate = 0.8
        mock_result.avg_attempts = 3.5
        mock_result.to_dict.return_value = {"mode": "test", "wins": 40}
        mock_instance.evaluate_test.return_value = mock_result
        mock_evaluator.return_value = mock_instance

        with patch.object(
            sys,
            "argv",
            [
                "harness",
                "--agent",
                "random",
                "--mode",
                "test",
                "--games",
                "50",
                "-o",
                "results.json",
            ],
        ):
            main()

        # Verify evaluate_test was called with correct num_games
        mock_instance.evaluate_test.assert_called_once()
        call_kwargs = mock_instance.evaluate_test.call_args.kwargs
        assert call_kwargs.get("num_games") == 50


