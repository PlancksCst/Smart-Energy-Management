import tkinter as tk
from tkinter import scrolledtext
import threading
import time
import sqlite3

DB_FILE = "energy.db"

def fetch_circuit_data():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, priority FROM circuits")
    circuits = cursor.fetchall()
    cursor.execute("""
        SELECT circuit_id, current FROM sensor_readings
        WHERE id IN (
            SELECT MAX(id) FROM sensor_readings GROUP BY circuit_id
        )
    """)
    readings = cursor.fetchall()
    conn.close()
    latest_readings = {cid: current for cid, current in readings}
    return [(c[0], c[1], c[2], latest_readings.get(c[0], 0.0)) for c in circuits]

def update_ui():
    for widget in frame.winfo_children():
        widget.destroy()
    data = fetch_circuit_data()
    for i, (cid, name, priority, current) in enumerate(data):
        label = tk.Label(frame, text=f"{name} (Priority {priority})", font=("Segoe UI", 11))
        label.grid(row=i, column=0, sticky="w", padx=10, pady=4)
        current_label = tk.Label(frame, text=f"Current: {current:.2f} A", fg="blue")
        current_label.grid(row=i, column=1, padx=10)
        status = "ON" if current > 0.1 else "OFF"
        color = "green" if status == "ON" else "red"
        status_label = tk.Label(frame, text=status, bg=color, fg="white", width=8)
        status_label.grid(row=i, column=2, padx=10)
    app.after(3000, update_ui)

def ai_assistant_response(user_input):
    responses = {
        "hello": "Hello! How can I assist you with your circuits today?",
        "status": "All circuits are currently operating normally.",
        "help": "You can ask me about circuit statuses, priorities, or current consumption.",
    }
    time.sleep(1)
    return responses.get(user_input.lower(), "Sorry, I don't understand that. Please ask something else.")

def send_message():
    user_msg = chat_entry.get().strip()
    if not user_msg:
        return
    chat_entry.delete(0, tk.END)
    chat_box.config(state=tk.NORMAL)
    chat_box.insert(tk.END, "You: " + user_msg + "\n")
    chat_box.config(state=tk.DISABLED)
    chat_box.see(tk.END)
    def get_response():
        response = ai_assistant_response(user_msg)
        chat_box.config(state=tk.NORMAL)
        chat_box.insert(tk.END, "AI: " + response + "\n\n")
        chat_box.config(state=tk.DISABLED)
        chat_box.see(tk.END)
    threading.Thread(target=get_response, daemon=True).start()

app = tk.Tk()
app.title("Smart Circuit Monitor Dashboard + AI Assistant")
app.geometry("850x400")

header = tk.Label(app, text="Real-Time Circuit Status", font=("Segoe UI", 14, "bold"))
header.pack(pady=10)

main_frame = tk.Frame(app)
main_frame.pack(fill="both", expand=True)

frame = tk.Frame(main_frame)
frame.pack(side="left", fill="both", expand=True, padx=10)

chat_frame = tk.Frame(main_frame, width=300)
chat_frame.pack(side="right", fill="y", padx=10)

chat_label = tk.Label(chat_frame, text="AI Assistant Chat", font=("Segoe UI", 12, "bold"))
chat_label.pack(pady=5)

chat_box = scrolledtext.ScrolledText(chat_frame, wrap=tk.WORD, state=tk.DISABLED, width=40, height=20)
chat_box.pack(pady=5)

entry_frame = tk.Frame(chat_frame)
entry_frame.pack(pady=5)

chat_entry = tk.Entry(entry_frame, width=30)
chat_entry.pack(side="left", padx=5)
chat_entry.focus()

send_button = tk.Button(entry_frame, text="Send", command=send_message)
send_button.pack(side="left")

def on_enter_key(event):
    send_message()
    return "break"

chat_entry.bind("<Return>", on_enter_key)

update_ui()
app.mainloop()