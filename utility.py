class Utility:

    @staticmethod
    def load_word_list(word_list_file_path: str, word_length: int = 5, exclude_plurals: bool = True):
        with open(word_list_file_path, "r") as f:
            english_words = [line.strip() for line in f]
        word_list = [word for word in english_words if len(word) == word_length]
        if exclude_plurals:
            word_list = [word for word in word_list if not (word.endswith("s") and not word.endswith("ss"))]
        return word_list

    @staticmethod
    def load_word_scores_dict(word_score_file_path: str):
        with open(word_score_file_path, "r") as f:
            word_score_lines = [line.strip().split("\t") for line in f]
        return {word: float(score) for word, score in word_score_lines}
