from src.generate import generate_answer

def chat_loop():
    print("RAG Chatbot (type 'exit' to quit)\n")
    while True:
        question = input("You: ")
        if question.lower() in ["exit", "quit"]:
            print("Goodbye!")
            break

        answer = generate_answer(question)
        print(f"\nBot: {answer}\n")

if __name__ == "__main__":
    chat_loop()