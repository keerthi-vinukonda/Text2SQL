# main.py

from pipeline import run_pipeline, display_result


def main():
    print("\n" + "=" * 60)
    print("   🤖 Text-to-SQL AI Assistant")
    print("   Powered by Claude + Snowflake")
    print("=" * 60)
    print("\n💡 Ask questions about employees in plain English.")
    print("   Type 'history' to see past questions.")
    print("   Type 'exit' to quit.\n")

    # Conversation history — enables follow-up questions
    conversation_history = []

    while True:
        user_input = input("🧑 You: ").strip()

        if not user_input:
            continue

        if user_input.lower() == "exit":
            print("\n👋 Goodbye!\n")
            break

        if user_input.lower() == "history":
            if not conversation_history:
                print("   No history yet.\n")
            else:
                print("\n📜 Conversation History:")
                for i, turn in enumerate(conversation_history, 1):
                    print(f"   {i}. Q: {turn['question']}")
                    print(f"      SQL: {turn['sql']}\n")
            continue

        # Run the full pipeline
        result = run_pipeline(user_input, conversation_history)

        # Display result
        display_result(result)

        # Save to conversation history (for follow-up support)
        if result["status"] == "success":
            conversation_history.append({
                "question": user_input,
                "sql":      result["sql"],
                "answer":   result["answer"]
            })


if __name__ == "__main__":
    main()