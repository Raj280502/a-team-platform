"""
main.py
-------
Entry point of the A-Team AI Platform.

Currently used only to verify that
core setup works correctly.
"""
from app.agents.strategist.node import build_strategist_node
from app.agents.architect.node import build_architect_node
from app.agents.coder.node import build_coder_node
from app.utils.file_ops import write_files
from pathlib import Path

def main():
    strategist = build_strategist_node()
    architect = build_architect_node()
    coder = build_coder_node()
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
    
    # 3. Coder
    coder_output = coder.invoke(
        {
            "project_scope": strategist_output.model_dump(),
            "architecture": architect_output.model_dump(),
        }
    )
    # 4. Write files
    project_dir = Path("workspace/generated_projects/todo_app")
    write_files(project_dir, coder_output.files)

    print("\nProject files generated at:")
    print(project_dir.resolve())



if __name__ == "__main__":
    main()