"""
main.py
-------
Entry point of the A-Team AI Platform.

Currently used only to verify that
core setup works correctly.
"""
from app.agents.strategist.node import build_strategist_node



def main():
    strategist = build_strategist_node()

    result = strategist.invoke(
        {
            "user_prompt": "Build a React todo app using Flask"
        }
    )

    print("\n--- STRATEGIST OUTPUT ---")
    print(result)


if __name__ == "__main__":
    main()
