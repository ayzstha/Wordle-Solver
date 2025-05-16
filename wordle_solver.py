#!/usr/bin/env python3

import string
import sys
import argparse
from typing import List
from collections import Counter
from dataclasses import dataclass

from utility import Utility


@dataclass
class SuggestedWordsResults:
    words: List[str]
    word_list_file_path: str = None


class WorldSolverMultiList:
    def __init__(
        self,
        word_list_file_paths: list = [],
        word_length: int = 5,
        exclude_plurals: bool = True,
        word_scores: dict = {},
        order_words_by_score_desc: bool = False,
        word_symbol_combinations: dict = {},
    ):
        self.word_lists = []
        self.word_list_file_paths = word_list_file_paths
        self.word_length = word_length
        self.exclude_plurals = exclude_plurals
        self.word_scores = word_scores
        self.max_try_indexes_for_lists = []
        self.order_words_by_score_desc = order_words_by_score_desc
        self.word_symbol_combinations = word_symbol_combinations

        for file_path in self.word_list_file_paths:
            word_list = Utility.load_word_list(file_path, self.word_length, self.exclude_plurals)
            self.word_lists.append(word_list)

        self.reset()

    def reset(self):
        self.tries = []
        self.solvers = []
        for word_list in self.word_lists:
            solver = WordleSolver(None, self.word_length, self.exclude_plurals)
            solver.word_list = word_list
            solver.word_scores = self.word_scores
            solver.order_words_by_descending_score = self.order_words_by_score_desc
            solver.word_symbol_combinations = self.word_symbol_combinations
            self.solvers.append(solver)

    def reset_pattern_parameters(self):
        for solver in self.solvers:
            solver.reset()

    def get_pattern_parameter_conflicts(self):
        if self.solvers:
            return self.solvers[0].get_pattern_parameter_conflicts()
        raise Exception("No solvers available")

    def update_pattern_parameters(self):
        for solver in self.solvers:
            solver.tries = self.tries
            solver.update_pattern_parameters()

    def input_guess_result(self, word, result_symbols):
        for solver in self.solvers:
            solver.input_guess_result(word, result_symbols)
        self.tries.append((word, result_symbols))

    def get_suggested_words(self) -> SuggestedWordsResults:
        for i in range(len(self.solvers)):
            if len(self.max_try_indexes_for_lists) > i:
                if len(self.tries) >= self.max_try_indexes_for_lists[i]:
                    continue
            suggested_words = self.solvers[i].get_suggested_words()
            if suggested_words:
                return SuggestedWordsResults(suggested_words, self.word_list_file_paths[i])
        last_path = self.word_list_file_paths[-1] if self.word_list_file_paths else None
        return SuggestedWordsResults([], last_path)

    def set_excluded_words(self, excluded_words: list):
        for solver in self.solvers:
            solver.excluded_words = excluded_words


class WordleSolver:
    def __init__(self, word_list_file_path: str = None, word_length: int = 5, exclude_plurals: bool = True):
        self.permitted_input_symbols = "gyb"
        self.word_list_file_path = word_list_file_path
        self.word_length = word_length
        self.exclude_plurals = exclude_plurals
        self.symbol_anyletter = "*"
        self.order_words_by_descending_score = False
        self.word_scores = {}
        self.word_symbol_combinations = {}

        self.word_list = []
        if self.word_list_file_path:
            self.word_list = Utility.load_word_list(self.word_list_file_path, self.word_length, self.exclude_plurals)

        self.reset()

    def reset(self):
        self.tries = []
        self.reset_pattern_parameters()

    def reset_pattern_parameters(self):
        self.included_letters = ""
        self.excluded_letters = ""
        self.high_prob_letters = ""
        self.wrong_spot_pattern = [""] * self.word_length
        self.right_spot_pattern = self.symbol_anyletter * self.word_length
        self.max_letter_occurrence = {}
        self.excluded_words = []
        self.effective_word_list = []

    def get_pattern_parameter_conflicts(self):
        conflicts = []
        for letter in self.excluded_letters:
            if letter in self.included_letters + self.high_prob_letters:
                conflicts.append((letter, "excluded letter found in inclusion list"))
            if letter in self.right_spot_pattern:
                conflicts.append((letter, "excluded letter found in right spot pattern"))
        for i in range(self.word_length):
            if self.right_spot_pattern[i] in self.wrong_spot_pattern[i]:
                conflicts.append((self.right_spot_pattern[i], "letter in right spot found in wrong spot pattern"))
        return conflicts

    def update_pattern_parameters(self):
        self.reset_pattern_parameters()
        possible_word_lists = []
        for word, symbol_pattern in self.tries:
            letter_counts = Counter(word)
            for i in range(self.word_length):
                letter = word[i]
                symbol = symbol_pattern[i]
                if symbol in "gy":
                    self.included_letters += letter
                    if symbol == "g":
                        rsp = list(self.right_spot_pattern)
                        rsp[i] = letter
                        self.right_spot_pattern = "".join(rsp)
                    elif symbol == "y":
                        self.wrong_spot_pattern[i] += letter
                elif symbol == "b":
                    if letter not in self.included_letters:
                        self.excluded_letters += letter
                    else:
                        if letter not in self.max_letter_occurrence:
                            self.max_letter_occurrence[letter] = word.count(letter) - 1
            if word in self.word_symbol_combinations:
                if symbol_pattern in self.word_symbol_combinations[word]:
                    possible_word_lists.append(self.word_symbol_combinations[word][symbol_pattern])

        self.included_letters = "".join(set(self.included_letters))
        self.excluded_letters = "".join(set([l for l in self.excluded_letters if l not in self.included_letters]))
        self.wrong_spot_pattern = ["".join(set(p)) for p in self.wrong_spot_pattern]

        if possible_word_lists:
            union = set().union(*possible_word_lists)
            self.effective_word_list = [w for w in union if all(w in lst for lst in possible_word_lists)]

    def get_letter_prob_dict(self, word_list):
        combined = ''.join(word_list)
        freqs = Counter(combined)
        total = len(combined)
        return {c: count / total for c, count in freqs.items()}

    def get_suggested_letters_by_freq(self, words):
        freqs = self.get_letter_prob_dict(words)
        return [(l, p) for l, p in freqs.items() if l not in self.included_letters + self.excluded_letters + self.high_prob_letters]

    def get_letter_positional_prob_dict(self, words):
        prob = []
        for i in range(self.word_length):
            if self.right_spot_pattern[i] == self.symbol_anyletter:
                letters = [word[i] for word in words]
                prob.append(self.get_letter_prob_dict(letters))
            else:
                prob.append({})
        return prob

    def sort_words_with_letter_positional_prob(self, words):
        pos_prob = self.get_letter_positional_prob_dict(words)
        scored = []
        for word in words:
            score = 1
            for i in range(len(word)):
                if pos_prob[i]:
                    score *= pos_prob[i].get(word[i], 1e-5)
            scored.append((word, score))
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored

    def sort_words(self, words):
        if self.word_scores and all(w in self.word_scores for w in words):
            return sorted(words, key=lambda w: self.word_scores[w], reverse=self.order_words_by_descending_score)
        return [w for w, _ in self.sort_words_with_letter_positional_prob(words)]

    def is_not_in_word(self, word):
        return all(c not in word for c in self.excluded_letters)

    def is_in_word(self, word):
        return all(c in word for c in self.included_letters + self.high_prob_letters)

    def is_not_tried(self, word):
        return word not in [w for w, _ in self.tries]

    def match_right_spot_pattern(self, word):
        return all(r == "*" or r == c for r, c in zip(self.right_spot_pattern, word))

    def get_possible_words(self):
        if not self.effective_word_list:
            self.effective_word_list = self.word_list

        excluded = set([w for w, _ in self.tries] + self.excluded_words)

        filtered = [
            word for word in self.effective_word_list
            if self.is_in_word(word)
            and self.is_not_in_word(word)
            and self.is_not_tried(word)
            and word not in excluded
        ]
        filtered = [w for w in filtered if all(w[i] not in self.wrong_spot_pattern[i] for i in range(self.word_length))]
        filtered = [w for w in filtered if self.match_right_spot_pattern(w)]

        for letter, max_occ in self.max_letter_occurrence.items():
            filtered = [w for w in filtered if w.count(letter) <= max_occ]

        return filtered

    def get_suggested_words(self):
        possible = self.get_possible_words()
        if not possible:
            return []

        unknown_count = self.word_length - len(self.included_letters)
        letter_probs = self.get_suggested_letters_by_freq(possible)
        if not letter_probs:
            return []

        letter_probs.sort(key=lambda x: x[1], reverse=True)
        suggested_letters = [l for l, _ in letter_probs]

        for i in range(unknown_count, 0, -1):
            self.high_prob_letters = suggested_letters[:i]
            self.update_pattern_parameters()
            suggestions = self.get_possible_words()
            self.high_prob_letters = ""
            if suggestions:
                return self.sort_words(suggestions)

        return self.sort_words(possible)

    def input_guess_result(self, word, result_symbols):
        if len(word) != self.word_length or len(result_symbols) != self.word_length:
            raise Exception("Word or symbol length mismatch.")
        if not all(c in string.ascii_lowercase for c in word):
            raise Exception("Invalid characters in word.")
        if not all(s in self.permitted_input_symbols for s in result_symbols):
            raise Exception("Invalid symbol in result.")
        self.tries.append((word, result_symbols))
        self.update_pattern_parameters()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--length", type=int, default=5, help="Length of the word")
    parser.add_argument("--plurals", action="store_true", help="Include plurals")
    args = parser.parse_args()

    word_list_file_paths = ["english_words_opener.txt", "english_words_full.txt"]

    solver_multi = WorldSolverMultiList(word_list_file_paths, args.length, not args.plurals)
    solver_multi.max_try_indexes_for_lists = [2, sys.maxsize]

    print(f"\nWORDLE Solver CLI (Word length: {args.length}; Exclude plurals: {not args.plurals})")
    print("Enter guesses like: word:bgybg")
    print("Commands: !done (reset), !tries (list), !remove_last (undo)\n")

    while True:
        try:
            user_input = input("Enter guess: ").strip().lower()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting...")
            break

        if ":" in user_input:
            word, symbols = user_input.split(":")
            if len(word) != args.length or len(symbols) != args.length:
                print("Length mismatch.")
                continue
            if symbols == "g" * args.length:
                print("Congratulations!")
                solver_multi.reset()
                continue
            try:
                solver_multi.input_guess_result(word, symbols)
            except Exception as e:
                print(f"Error: {e}")
                continue

            conflicts = solver_multi.get_pattern_parameter_conflicts()
            if conflicts:
                for c in conflicts:
                    print(f"{c[0]}: {c[1]}")
                solver_multi.tries.pop()
                continue

        elif user_input == "!done":
            solver_multi.reset()
            print("Reset complete.")
            continue
        elif user_input == "!remove_last":
            if solver_multi.tries:
                solver_multi.tries.pop()
                print("Last try removed.")
            continue
        elif user_input == "!tries":
            for i, t in enumerate(solver_multi.tries):
                print(f"Try {i+1}: {t}")
            continue
        else:
            print("Invalid input.")
            continue

        suggestions = solver_multi.get_suggested_words()
        if suggestions.words:
            print(f"Suggestions (from '{suggestions.word_list_file_path}'):")
            for word in suggestions.words[:10]:
                print(f"  - {word}")
        else:
            print("No suggestions left. Double-check your inputs.")
