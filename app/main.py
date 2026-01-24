from app.graph.graph import build_graph


def main():
    graph = build_graph()

    final_state = graph.invoke(
        {
            "user_prompt": "Build a simple calculator app with  React.",
            "project_scope": None,
            "architecture": None,
            "contract": None,
            "files": {},
            "tests_passed": None,
            "error_message": None,
            "repair_attempts": 0,
            "project_dir": "app/workspace/generated_projects/todo_app",
        }
    )

    print("\nFINAL STATE:")
    print(final_state)


if __name__ == "__main__":
    main()
