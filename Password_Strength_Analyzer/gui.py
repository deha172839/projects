import tkinter as tk
from tkinter import messagebox
from password_analyzer import analyze_password

# ===========================
# Functions
# ===========================

def check_password():
    password = password_entry.get()

    if password == "":
        messagebox.showwarning("Warning", "Please enter a password.")
        return

    result = analyze_password(password)

    strength_label.config(text=f"Password Strength: {result['strength']}")

    # Change label color
    if result["strength"] == "Strong":
        strength_label.config(fg="green")
    elif result["strength"] == "Medium":
        strength_label.config(fg="orange")
    else:
        strength_label.config(fg="red")

    output_box.config(state="normal")
    output_box.delete("1.0", tk.END)

    output_box.insert(tk.END, f"Score : {result['score']}/6\n\n")

    output_box.insert(tk.END, "DETAILS\n")
    output_box.insert(tk.END, "---------------------------\n")

    for item in result["details"]:
        output_box.insert(tk.END, item + "\n")

    output_box.insert(tk.END, "\nSUGGESTIONS\n")
    output_box.insert(tk.END, "---------------------------\n")

    if len(result["suggestions"]) == 0:
        output_box.insert(tk.END, "Excellent Password! Keep using it.\n")
    else:
        for item in result["suggestions"]:
            output_box.insert(tk.END, "• " + item + "\n")

    output_box.config(state="disabled")


def clear_output():
    password_entry.delete(0, tk.END)
    strength_label.config(text="Password Strength:", fg="black")

    output_box.config(state="normal")
    output_box.delete("1.0", tk.END)
    output_box.config(state="disabled")


def toggle_password():
    if show_password.get():
        password_entry.config(show="")
    else:
        password_entry.config(show="*")


# ===========================
# Main Window
# ===========================

window = tk.Tk()
window.title("Password Strength Analyzer")
window.geometry("650x600")
window.configure(bg="#f4f6f9")
window.resizable(False, False)

# ===========================
# Title
# ===========================

title = tk.Label(
    window,
    text="🔐 Password Strength Analyzer",
    font=("Helvetica", 20, "bold"),
    bg="#f4f6f9",
    fg="#2c3e50"
)
title.pack(pady=20)

# ===========================
# Input Frame
# ===========================

input_frame = tk.Frame(window, bg="#ffffff", bd=2, relief="groove")
input_frame.pack(padx=20, pady=10, fill="x")

tk.Label(
    input_frame,
    text="Enter Password",
    font=("Arial", 12, "bold"),
    bg="#ffffff"
).pack(anchor="w", padx=15, pady=(15,5))

password_entry = tk.Entry(
    input_frame,
    font=("Arial", 13),
    width=35,
    show="*"
)
password_entry.pack(padx=15, pady=5)

show_password = tk.BooleanVar()

show_check = tk.Checkbutton(
    input_frame,
    text="Show Password",
    variable=show_password,
    command=toggle_password,
    bg="#ffffff"
)
show_check.pack(anchor="w", padx=15)

# ===========================
# Buttons
# ===========================

button_frame = tk.Frame(window, bg="#f4f6f9")
button_frame.pack(pady=15)

analyze_btn = tk.Button(
    button_frame,
    text="Analyze Password",
    command=check_password,
    bg="#3498db",
    fg="white",
    font=("Arial", 11, "bold"),
    width=18
)
analyze_btn.grid(row=0, column=0, padx=10)

clear_btn = tk.Button(
    button_frame,
    text="Clear",
    command=clear_output,
    bg="#3ce77b",
    fg="white",
    font=("Arial", 11, "bold"),
    width=12
)
clear_btn.grid(row=0, column=1, padx=10)

# ===========================
# Strength Label
# ===========================

strength_label = tk.Label(
    window,
    text="Password Strength:",
    font=("Arial", 14, "bold"),
    bg="#f4f6f9"
)
strength_label.pack()

# ===========================
# Output Frame
# ===========================

output_frame = tk.Frame(window)
output_frame.pack(padx=20, pady=15)

scrollbar = tk.Scrollbar(output_frame)

output_box = tk.Text(
    output_frame,
    width=70,
    height=18,
    font=("Consolas", 11),
    yscrollcommand=scrollbar.set,
    state="disabled",
    wrap="word"
)

scrollbar.config(command=output_box.yview)

scrollbar.pack(side="right", fill="y")
output_box.pack(side="left")

# ===========================
# Footer
# ===========================

footer = tk.Label(
    window,
    text="Internship Project | Python + Tkinter",
    font=("Arial", 10),
    bg="#f4f6f9",
    fg="gray"
)
footer.pack(pady=10)

window.mainloop()