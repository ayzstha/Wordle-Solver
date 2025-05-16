# 🟩 Wordle Solver Web App

An interactive, Wordle-style web application that helps you solve Wordle puzzles by suggesting the most probable words based on your guesses and feedback.

## 🚀 Features

- Clickable letter tiles that cycle between green 🟩, yellow 🟨, and gray ⬛ just like the real game  
- Intelligent solver using frequency analysis and positional probabilities  
- Supports multiple word lists  
- Web interface powered by Flask  
- Automatically filters out impossible words based on your guess history  

---

## 🧠 How It Works

Enter your guess and click the tiles to mark their correctness:

- 🟩 Green = correct letter, correct position  
- 🟨 Yellow = correct letter, wrong position  
- ⬛ Gray = letter not in word  

The solver updates suggestions based on feedback.

---

## 🗂️ Project Structure

```
wordle-solver/
├── app.py                      # Flask server
├── wordle_solver.py            # Main solver logic
├── utility.py                  # Word list loader, scoring utils
├── english_words_opener.txt   # Small starter word list
├── english_words_full.txt     # Full word list
├── templates/
│   └── index.html              # Wordle-style frontend
```

---

## ✅ Requirements

- Python 3.7+
- Flask

Install dependencies:

```bash
pip install flask
```

---

## ▶️ Running the App

```bash
python app.py
```

Then open your browser to:

```
http://127.0.0.1:5000
```

---

## ✏️ Customization

- Replace `english_words_opener.txt` and `english_words_full.txt` with your preferred word lists.  
- Modify scoring logic in `wordle_solver.py` for smarter suggestions.

---

## 🧪 Example Input

Try guessing:

```
CRANE → bgybb  
AISLE → ggybb  
```

The solver will narrow down and recommend the most probable next word.

---

## 📄 License

MIT License. Feel free to use, modify, and share!

---

## ❤️ Built With

- Flask  
- Python  
- HTML/CSS (Wordle-style UI)
