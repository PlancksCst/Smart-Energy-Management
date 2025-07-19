import ollama

def main():
    print("🔌 AI Assistant for Energy Management System")
    print("Type 'exit' to quit\n")

    while True:
        prompt = input("🧠 You: ")
        if prompt.lower() in ["exit", "quit"]:
            break

        response = ollama.chat(model="gemma:2b", messages=[
            {"role": "user", "content": prompt}
        ])

        print(f"🤖 Assistant: {response['message']['content']}\n")

if __name__ == "__main__":
    main()
