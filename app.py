from flask import Flask, render_template, request
from wordle_solver import WorldSolverMultiList

app = Flask(__name__)

solver_multi = WorldSolverMultiList(
    word_list_file_paths=["english_words_opener.txt", "english_words_full.txt"],
    word_length=5,
    exclude_plurals=True
)
solver_multi.max_try_indexes_for_lists = [2, 999]

@app.route("/", methods=["GET", "POST"])
def index():
    suggestions = []
    conflicts = []
    tries = solver_multi.tries

    if request.method == "POST":
        word = request.form.get("word", "").lower()
        result = request.form.get("result", "").lower()

        if word and result and len(word) == len(result) == solver_multi.word_length:
            if result == "g" * solver_multi.word_length:
                solver_multi.reset()
            else:
                solver_multi.input_guess_result(word, result)
                conflicts = solver_multi.get_pattern_parameter_conflicts()
                if conflicts:
                    solver_multi.tries.pop()

        suggestions_data = solver_multi.get_suggested_words()
        suggestions = suggestions_data.words[:10]

    return render_template("index.html", tries=tries, suggestions=suggestions, conflicts=conflicts)

@app.route("/reset", methods=["POST"])
def reset():
    solver_multi.reset()
    return render_template("index.html", tries=[], suggestions=[], conflicts=[])

if __name__ == "__main__":
    app.run(debug=True)
