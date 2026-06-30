# 🔐 Password Strength Analyzer

A simple Python application that analyzes the strength of a user-entered password. The project uses **Tkinter** for the graphical user interface (GUI) and follows a modular design by separating the password analysis logic from the GUI.

---

##  Project Objective

The goal of this project is to help users create stronger passwords by evaluating their passwords based on common security rules and providing suggestions for improvement.

This project also helps beginners understand:
- Password security
- Regular Expressions (Regex)
- Python functions
- Tkinter GUI development
- Modular programming

---

##  Features

- ✅ Check password length
- ✅ Check uppercase letters
- ✅ Check lowercase letters
- ✅ Check numeric digits
- ✅ Check special characters
- ✅ Detect common weak passwords
- ✅ Display password strength (Weak / Medium / Strong)
- ✅ Show detailed analysis
- ✅ Suggest improvements for stronger passwords

---

##  Project Structure

```
Password_Strength_Analyzer/
│
├── password_analyzer.py     # Core password analysis logic
├── gui.py                   # Tkinter GUI
└── README.md                # Project documentation
```

---

## 🛠 Technologies Used

- Python 3
- Tkinter
- Regular Expressions (`re`)

---

##  How to Run the Project

### Step 1

Install Python (Version 3.8 or above).

Download from:

https://www.python.org/downloads/

---

### Step 2

Download or clone this project.

---

### Step 3

Open the project folder in VS Code.

---

### Step 4

Run the GUI file.

```bash
python gui.py
```

---

## 🖥 Application Workflow

1. User enters a password.
2. The GUI sends the password to the analyzer.
3. The analyzer checks:
   - Password length
   - Uppercase letters
   - Lowercase letters
   - Numbers
   - Special characters
   - Common password list
4. A score is calculated.
5. Password strength is displayed.
6. Suggestions are shown if improvements are needed.

---

##  Password Strength Criteria

| Criteria | Points |
|----------|--------|
| Length ≥ 12 | +2 |
| Length 8–11 | +1 |
| Uppercase Letter | +1 |
| Lowercase Letter | +1 |
| Number | +1 |
| Special Character | +1 |

### Strength Levels

- **0 – 3** → Weak
- **4 – 5** → Medium
- **6** → Strong

---

## 📷 Example

### Input

```
Hello123
```

### Output

```
Strength : Medium

Details

✔ Password length is acceptable.
✔ Contains uppercase letter.
✔ Contains lowercase letter.
✔ Contains number.
✘ No special character.

Suggestions

- Increase password length to at least 12 characters.
- Add at least one special character.
```

---

##  Concepts Used

- Functions
- Lists
- Conditional Statements
- Dictionaries
- String Handling
- Regular Expressions (Regex)
- Tkinter Widgets
- Event Handling
- Modular Programming

---

##  Future Improvements

- Show / Hide Password button
- Password Generator
- Strength Progress Bar
- SQLite database to prevent password reuse
- Password history management
- Password hashing using SHA-256
- Dark mode interface
- Export analysis report

---

##  Learning Outcomes

After completing this project, you will understand:

- Password security principles
- Strong password requirements
- GUI development with Tkinter
- Python project structure
- Regular Expressions
- Writing reusable functions
- Creating beginner-friendly desktop applications

---

##  Author

**Name:** Your Name

**Internship Project**

Password Strength Analyzer using Python and Tkinter.

---

## License

This project is developed for educational and internship learning purposes.