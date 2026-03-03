# -*- coding: utf-8 -*-
"""
main.py -- CLI entry point for the Multi-Agent Task Router.
Run: python main.py
"""

from dotenv import load_dotenv
load_dotenv()

from graph.workflow import task_router


def run_task(user_input: str) -> dict:
    """
    Runs a task through the full multi-agent pipeline.
    Returns the final state.
    """
    initial_state = {
        "task": user_input,
        "task_type": "",
        "result": "",
        "error": None,
        "retry_count": 0,
        "messages": [],
        "correction_notes": None,
    }
    final_state = task_router.invoke(initial_state)
    return final_state


def print_result(state: dict):
    """Pretty-prints the pipeline output."""
    print("\n" + "=" * 60)
    print(f"  Task Type : {state.get('task_type', 'N/A').upper()}")
    print(f"  Retries   : {state.get('retry_count', 0)}")
    print("=" * 60)
    print("\n📋 AGENT TRACE:")
    for msg in state.get("messages", []):
        print(f"  {msg}")

    print("\n✅ RESULT:")
    print("-" * 60)
    print(state.get("result") or "⚠️  No result produced.")

    if state.get("error"):
        print(f"\n❌ Final Error: {state['error']}")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    print("\n🤖 Multi-Agent Task Router")
    print("   Type 'exit' or 'quit' to stop.\n")

    while True:
        try:
            user_input = input("You: ").strip()
            if not user_input:
                continue
            if user_input.lower() in {"exit", "quit"}:
                print("Goodbye!")
                break

            print("\n⚙️  Routing task through agents...\n")
            state = run_task(user_input)
            print_result(state)

        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}\n")
