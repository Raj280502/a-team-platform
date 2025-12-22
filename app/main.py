"""
main.py
-------
Entry point of the A-Team AI Platform.

Currently used only to verify that
core setup works correctly.
"""
from pathlib import Path

from app.agents.strategist.node import build_strategist_node
from app.agents.architect.node import build_architect_node
from app.agents.coder.node import (
    build_generate_node,
    build_repair_node
)
from app.agents.tester.node import tester_node
from app.runtime.test_runner import run_basic_backend_test
from app.utils.file_ops import write_files


def main():
    strategist = build_strategist_node()
    architect = build_architect_node()
    generate_coder  = build_generate_node()
    repair_coder = build_repair_node()
    
    
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
    
    project_dir = Path("workspace/generated_projects/todo_app")
    # ONE retry only (important)
    
    coder_output = generate_coder.invoke(
        {
            "project_scope": strategist_output.model_dump(),
            "architecture": architect_output.model_dump(),
        }
    )
    
    if not coder_output.new_files:
        raise RuntimeError("Initial generation failed: no files returned")
    
    

    write_files(project_dir, coder_output.new_files)
    test_result = run_basic_backend_test(project_dir)
    tester_output = tester_node(test_result)
    print("\nInitial test result:", tester_output)
    
    if not tester_output.tests_passed:
        print("\nAttempting localized repair...")

        repair_output = repair_coder.invoke(
            {
                "existing_files": {
                    path: (project_dir / path).read_text(encoding="utf-8")
                    for path in [
                        p.relative_to(project_dir).as_posix()
                        for p in project_dir.rglob("*")
                        if p.is_file()
                    ]
                },
                "error_message": tester_output.error_message,
            }
        )
        if not repair_output.modified_files:
            raise RuntimeError("Repair failed: no modified files returned")

        # Apply patches ONLY
        write_files(project_dir, repair_output.modified_files)

        # Re-test
        test_result = run_basic_backend_test(project_dir)
        tester_output = tester_node(test_result)

        print("\nPost-repair test result:", tester_output)

    if tester_output.tests_passed:
        print("\n✅ Pipeline completed successfully.")
    else:
        print("\n❌ Pipeline failed after repair.")

    



if __name__ == "__main__":
    main()