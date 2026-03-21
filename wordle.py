#!/usr/bin/env python3
"""Wordle game using the Random Words API."""

import random
import requests
import sys
from typing import List, Tuple

API_URL = "https://random-words-api.kushcreates.com/api"
MAX_ATTEMPTS = 6
WORD_LENGTH = 5


def fetch_wordle_word() -> str:
    """Fetch a random 5-letter Wordle word from the API."""
    params = {
        "language": "en",
        "category": "wordle",
        "length": WORD_LENGTH,
        "words": 1,
    }
    try:
        response = requests.get(API_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        word = data[0]["word"].lower().strip()
        return word
    except Exception as e:
        print(f"Error fetching word: {e}", flush=True)
        fallback = ["apple", "beach", "crane", "dance", "eagle", "flame", "grape", "house", "image", "jolly"]
        return random.choice(fallback)


def get_feedback(guess: str, target: str) -> List[Tuple[str, str]]:
    """
    Return feedback for each letter in the guess.
    Each tuple contains (letter, status) where status is:
    - 'correct': right letter, right position (green)
    - 'present': right letter, wrong position (yellow)
    - 'absent': letter not in target (gray)
    """
    result = []
    target_list = list(target)
    guess_list = list(guess)
    
    for i in range(WORD_LENGTH):
        if guess_list[i] == target_list[i]:
            result.append((guess_list[i], 'correct'))
            target_list[i] = None
        else:
            result.append((guess_list[i], 'absent'))
    
    for i in range(WORD_LENGTH):
        if result[i][1] == 'absent' and guess_list[i] in target_list:
            result[i] = (guess_list[i], 'present')
            target_list[target_list.index(guess_list[i])] = None
    
    return result


def print_feedback(feedback: List[Tuple[str, str]]) -> None:
    """Print the feedback with colors."""
    output = ""
    for letter, status in feedback:
        if status == 'correct':
            output += f"\033[42m\033[30m {letter.upper()} \033[0m "
        elif status == 'present':
            output += f"\033[43m\033[30m {letter.upper()} \033[0m "
        else:
            output += f"\033[100m\033[37m {letter.upper()} \033[0m "
    print(output, flush=True)


def print_keyboard(used_letters: dict) -> None:
    """Print the keyboard with used letter status."""
    keyboard = [
        ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p'],
        ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l'],
        ['z', 'x', 'c', 'v', 'b', 'n', 'm']
    ]
    
    print("\nKeyboard:", flush=True)
    for row in keyboard:
        line = " " * (3 - len(row) // 4)
        for letter in row:
            status = used_letters.get(letter, 'unused')
            if status == 'correct':
                line += f"\033[42m\033[30m{letter}\033[0m "
            elif status == 'present':
                line += f"\033[43m\033[30m{letter}\033[0m "
            elif status == 'absent':
                line += f"\033[100m\033[37m{letter}\033[0m "
            else:
                line += f"{letter} "
        print(line, flush=True)
    print(flush=True)


def is_valid_guess(guess: str) -> bool:
    """Check if the guess is valid (5 letters, alphabetic)."""
    return len(guess) == WORD_LENGTH and guess.isalpha()


def play_wordle(target_word: str = None) -> None:
    """Main game loop.
    
    Args:
        target_word: Optional specific word to guess (for testing)
    """
    print("=" * 50, flush=True)
    print("           W O R D L E", flush=True)
    print("=" * 50, flush=True)
    print(f"\nGuess the {WORD_LENGTH}-letter word. You have {MAX_ATTEMPTS} attempts.", flush=True)
    print("\033[42m\033[30m Green \033[0m = Correct letter & position", flush=True)
    print("\033[43m\033[30m Yellow \033[0m = Correct letter, wrong position", flush=True)
    print("\033[100m\033[37m Gray \033[0m = Letter not in word", flush=True)
    print("\n" + "-" * 50, flush=True)
    
    if target_word:
        target = target_word.lower().strip()
    else:
        print("Fetching word...", flush=True)
        target = fetch_wordle_word()
    
    attempts = 0
    used_letters = {}
    
    while attempts < MAX_ATTEMPTS:
        print(f"\nAttempt {attempts + 1}/{MAX_ATTEMPTS}", flush=True)
        
        while True:
            try:
                guess = input("Enter your guess: ").strip().lower()
            except EOFError:
                print(f"\nGame ended. Word was: {target.upper()}", flush=True)
                return
            
            if guess == 'quit':
                print(f"\nThe word was: {target.upper()}", flush=True)
                sys.exit(0)
            
            if not is_valid_guess(guess):
                print(f"Please enter exactly {WORD_LENGTH} letters.", flush=True)
                continue
            
            break
        
        feedback = get_feedback(guess, target)
        print_feedback(feedback)
        
        for letter, status in feedback:
            if letter not in used_letters:
                used_letters[letter] = status
            elif status == 'correct':
                used_letters[letter] = 'correct'
        
        print_keyboard(used_letters)
        
        attempts += 1
        
        if guess == target:
            print(f"\n🎉 Congratulations! You guessed the word in {attempts} attempt(s)!", flush=True)
            print(f"WORD={target.upper()}", flush=True)
            return
    
    print(f"\n😔 Game Over! The word was: {target.upper()}", flush=True)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Wordle game")
    parser.add_argument("--word", help="Target word (for testing)")
    args = parser.parse_args()
    
    try:
        play_wordle(target_word=args.word)
    except KeyboardInterrupt:
        print("\n\nGame interrupted. Goodbye!", flush=True)
        sys.exit(0)
