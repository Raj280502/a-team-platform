from app.graph.graph import build_graph


def main():
    graph = build_graph()

    final_state = graph.invoke(
        {
            "user_prompt": "Build a simple React todo app using Flask",
            "project_scope": None,
            "architecture": None,
            "files": {},
            "tests_passed": None,
            "error_message": None,
            "repair_attempts": 0,
        }
    )

    print("\nFINAL STATE:")
    print(final_state)


if __name__ == "__main__":
    main()
