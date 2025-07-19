# llm_agent.py

import requests
import sqlite3

OLLAMA_URL = "http://localhost:11434/api/generate"

def ask_gemma(prompt: str) -> str:
    response = requests.post(OLLAMA_URL, json={
        "model": "gemma:2b",
        "prompt": prompt,
        "stream": False
    })
    if response.status_code == 200:
        return response.json()["response"]
    else:
        return f"Error from LLM: {response.text}"


def get_high_priority_circuits():
    conn = sqlite3.connect("energy.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT name, priority, average_consumption_Wh
        FROM circuits
        WHERE priority >= 4
    """)
    data = cursor.fetchall()
    conn.close()

    if not data:
        return "No high-priority circuits found."

    prompt = "These are the current high-priority circuits:\n"
    for row in data:
        prompt += f"- Name: {row[0]}, Priority: {row[1]}, Avg Consumption: {row[2]} Wh\n"

    prompt += "\nWhich circuits should we consider switching off to reduce load?"
    return prompt
