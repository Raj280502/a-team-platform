"""
main.py
-------
Entry point of the A-Team AI Platform.

Currently used only to verify that
core setup works correctly.
"""
from app.agents.strategist.node import build_strategist_node
from app.agents.architect.node import build_architect_node


def main():
    strategist = build_strategist_node()
    architect = build_architect_node()

    strategist_output = strategist.invoke(
        {
            "user_prompt": "Build a React todo app using Flask"
        }
    )

    print("\n--- STRATEGIST OUTPUT ---")
    print(strategist_output)

    architect_output = architect.invoke(
        {
            "project_scope": strategist_output.model_dump()
        }
    )

    print("\n--- ARCHITECT OUTPUT ---")
    print(architect_output)


if __name__ == "__main__":
    main()