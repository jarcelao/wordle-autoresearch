"""Unit tests for wordle.py"""
import pytest
from unittest.mock import patch, MagicMock
import sys
from io import StringIO

from wordle import (
    fetch_wordle_word,
    get_feedback,
    is_valid_guess,
    print_feedback,
    print_keyboard,
    play_wordle,
    WORD_LENGTH,
    MAX_ATTEMPTS,
)


class TestFetchWordleWord:
    """Tests for fetch_wordle_word function"""

    @patch('wordle.requests.get')
    def test_fetch_wordle_word_success(self, mock_get):
        """Test successful API fetch"""
        mock_response = MagicMock()
        mock_response.json.return_value = [{"word": "CRANE"}]
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        result = fetch_wordle_word()
        assert result == "crane"
        mock_get.assert_called_once()

    @patch('wordle.requests.get')
    @patch('wordle.random.choice')
    def test_fetch_wordle_word_api_failure(self, mock_choice, mock_get):
        """Test fallback when API fails"""
        mock_get.side_effect = Exception("Connection error")
        mock_choice.return_value = "crane"

        result = fetch_wordle_word()
        assert result == "crane"


class TestGetFeedback:
    """Tests for get_feedback function"""

    def test_all_correct(self):
        """All letters correct position"""
        result = get_feedback("crane", "crane")
        assert len(result) == 5
        for letter, status in result:
            assert status == "correct"

    def test_all_absent(self):
        """All letters not in word"""
        result = get_feedback("xxxxx", "crane")
        assert len(result) == 5
        for letter, status in result:
            assert status == "absent"

    def test_all_present(self):
        """All letters present but wrong position"""
        result = get_feedback("necra", "crane")
        assert len(result) == 5
        for letter, status in result:
            assert status == "present"

    def test_mixed_feedback(self):
        """Mix of correct, present, and absent"""
        result = get_feedback("crown", "crane")
        # c is correct, r is correct, o is absent, w is absent, n is present
        assert result[0] == ("c", "correct")
        assert result[1] == ("r", "correct")
        assert result[2] == ("o", "absent")
        assert result[3] == ("w", "absent")
        assert result[4] == ("n", "present")

    def test_duplicate_letters_correct_counting(self):
        """Handle duplicate letters correctly - only mark if target has them"""
        # Target has one 'e', guess has two 'e's
        result = get_feedback("eagle", "crane")
        # e at pos 0 is present, a is absent, g is absent, l is absent, e at pos 4 is correct
        statuses = [status for _, status in result]
        # Should have one correct (last e), one present (first e)
        assert statuses.count("correct") == 1
        assert statuses.count("present") == 1
        assert statuses.count("absent") == 3


class TestIsValidGuess:
    """Tests for is_valid_guess function"""

    def test_valid_5_letter_word(self):
        assert is_valid_guess("crane") is True
        assert is_valid_guess("apple") is True

    def test_too_short(self):
        assert is_valid_guess("cat") is False

    def test_too_long(self):
        assert is_valid_guess("cranes") is False

    def test_non_alpha(self):
        assert is_valid_guess("cr4ne") is False
        assert is_valid_guess("cr ne") is False

    def test_uppercase(self):
        # isalpha() returns True for uppercase
        assert is_valid_guess("CRANE") is True


class TestPrintFeedback:
    """Tests for print_feedback function"""

    @pytest.mark.parametrize("feedback,expected_pieces", [
        ([("a", "correct")], [" A "]),
        ([("b", "present")], [" B "]),
        ([("c", "absent")], [" C "]),
    ])
    def test_outputs_contain_letters(self, feedback, expected_pieces, capsys):
        print_feedback(feedback)
        captured = capsys.readouterr()
        for piece in expected_pieces:
            assert piece in captured.out


class TestPrintKeyboard:
    """Tests for print_keyboard function"""

    def test_prints_keyboard_layout(self, capsys):
        used_letters = {"a": "correct", "b": "absent"}
        print_keyboard(used_letters)
        captured = capsys.readouterr()
        # Should contain keyboard rows
        assert "q" in captured.out.lower()
        assert "a" in captured.out.lower()
        assert "z" in captured.out.lower()
        assert "Keyboard:" in captured.out


class TestPlayWordle:
    """Tests for play_wordle function"""

    @patch('wordle.input', side_effect=["crane"])
    @patch('wordle.print_feedback')
    @patch('wordle.print_keyboard')
    def test_win_on_first_guess(self, mock_keyboard, mock_feedback, mock_input, capsys):
        """Test winning immediately"""
        play_wordle("crane")
        captured = capsys.readouterr()
        assert "Congratulations" in captured.out or "WORD=CRANE" in captured.out

    @patch('wordle.input', side_effect=["wrong", "crane"])
    @patch('wordle.print_feedback')
    @patch('wordle.print_keyboard')  
    def test_win_on_second_guess(self, mock_keyboard, mock_feedback, mock_input, capsys):
        """Test eventually winning"""
        play_wordle("crane")
        captured = capsys.readouterr()
        assert "Congratulations" in captured.out

    @patch('wordle.input', side_effect=["aaaaa", "crane"])
    @patch('wordle.print_feedback')
    @patch('wordle.print_keyboard')
    def test_invalid_then_valid(self, mock_keyboard, mock_feedback, mock_input, capsys):
        """Test handling invalid input then valid"""
        play_wordle("crane")
        captured = capsys.readouterr()
        # Should have prompted for 5 letters
        assert "5 letters" in captured.out or "Congratulations" in captured.out

    @patch('wordle.input', side_effect=["quit"])
    def test_quit_game(self, mock_input, capsys):
        """Test quitting the game"""
        with pytest.raises(SystemExit) as exc_info:
            play_wordle("crane")
        assert exc_info.value.code == 0

    @patch('wordle.input', side_effect=["guess"] * 6)
    @patch('wordle.print_feedback')
    @patch('wordle.print_keyboard')
    def test_game_over_max_attempts(self, mock_keyboard, mock_feedback, mock_input, capsys):
        """Test losing after max attempts"""
        play_wordle("crane")
        captured = capsys.readouterr()
        assert "Game Over" in captured.out or "word was" in captured.out.lower()

    @patch('wordle.input', side_effect=EOFError())
    def test_eof_error(self, mock_input, capsys):
        """Test handling EOFError (e.g., piped input)"""
        play_wordle("crane")
        captured = capsys.readouterr()
        assert "Game ended" in captured.out
