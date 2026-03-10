"""
main.py - Entry point for the AI Code Factory pipeline.
Handles project directory setup and LangGraph execution.
"""

import os
import sys
import json
import argparse
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import WORKSPACE_DIR
from app.graph.graph import build_graph, build_chat_graph


def create_project_dir(project_name: str) -> Path:
    """Create project directory and return its path."""
    workspace = Path(WORKSPACE_DIR)
    workspace.mkdir(parents=True, exist_ok=True)

    project_dir = workspace / project_name
    project_dir.mkdir(parents=True, exist_ok=True)
    (project_dir / "backend").mkdir(exist_ok=True)
    (project_dir / "frontend" / "src" / "components").mkdir(parents=True, exist_ok=True)

    return project_dir


def generate_project_name(prompt: str) -> str:
    """Generate a clean project name from user prompt."""
    import re
    # Extract first few meaningful words
    words = re.sub(r"[^a-zA-Z0-9\s]", "", prompt).lower().split()
    name = "_".join(words[:4]) or "my_project"
    return name[:40]


def run_pipeline(user_prompt: str, project_name: str = None, callback=None):
    """
    Run the full generation pipeline.
    
    Args:
        user_prompt: Description of the app to build
        project_name: Optional custom project name
        callback: Optional callback for progress updates
    """
    if not project_name:
        project_name = generate_project_name(user_prompt)

    print(f"\n{'='*60}")
    print(f"🏭 AI CODE FACTORY")
    print(f"{'='*60}")
    print(f"📝 Prompt: {user_prompt}")
    print(f"📁 Project: {project_name}")
    print(f"{'='*60}\n")

    # Create project directory
    project_dir = create_project_dir(project_name)

    # Build and run the LangGraph pipeline
    graph = build_graph()

    initial_state = {
        "user_prompt": user_prompt,
        "project_name": project_name,
        "project_dir": str(project_dir),
        "tech_stack": "react-flask",
        "chat_history": [],
        "is_followup": False,
        "files": {},
        "file_plan": [],
        "extracted_routes": [],
        "request_fields": {},
        "generation_issues": [],
        "files_to_regenerate": [],
        "failed_file_history": [],
        "tests_passed": False,
        "error_message": None,
        "contract_report": {},
        "repair_attempts": 0,
        "preview_started": False,
        "preview_url": "",
        "current_step": "starting",
    }

    # Run the pipeline
    final_state = graph.invoke(initial_state)

    print(f"\n{'='*60}")
    print(f"📊 FINAL REPORT")
    print(f"{'='*60}")
    print(f"   Files generated: {len(final_state.get('files', {}))}")
    print(f"   Tests passed: {final_state.get('tests_passed', False)}")
    print(f"   Preview URL: {final_state.get('preview_url', 'N/A')}")
    print(f"   Project dir: {project_dir}")
    print(f"{'='*60}\n")

    return final_state


def run_pipeline_streaming(user_prompt: str, project_name: str = None, on_node_complete=None):
    """
    Run the generation pipeline with streaming — calls on_node_complete(node_name, node_output)
    after each node so the UI can update in real-time.
    
    Args:
        user_prompt: Description of the app to build
        project_name: Optional custom project name
        on_node_complete: Callback(node_name: str, node_output: dict) called after each node
    """
    if not project_name:
        project_name = generate_project_name(user_prompt)

    print(f"\n{'='*60}")
    print(f"🏭 AI CODE FACTORY (Streaming)")
    print(f"{'='*60}")
    print(f"📝 Prompt: {user_prompt}")
    print(f"📁 Project: {project_name}")
    print(f"{'='*60}\n")

    # Create project directory
    project_dir = create_project_dir(project_name)

    # Build LangGraph pipeline
    graph = build_graph()

    initial_state = {
        "user_prompt": user_prompt,
        "project_name": project_name,
        "project_dir": str(project_dir),
        "tech_stack": "react-flask",
        "chat_history": [],
        "is_followup": False,
        "files": {},
        "file_plan": [],
        "extracted_routes": [],
        "request_fields": {},
        "generation_issues": [],
        "files_to_regenerate": [],
        "failed_file_history": [],
        "tests_passed": False,
        "error_message": None,
        "contract_report": {},
        "repair_attempts": 0,
        "preview_started": False,
        "preview_url": "",
        "current_step": "starting",
    }

    # Stream the pipeline — each yield is {node_name: node_output}
    final_state = initial_state.copy()
    try:
        for event in graph.stream(initial_state):
            # event is a dict like {"strategist": {"project_scope": {...}, "current_step": "..."}}
            for node_name, node_output in event.items():
                print(f"  🔄 Node '{node_name}' completed")
                final_state.update(node_output)
                if on_node_complete:
                    try:
                        on_node_complete(node_name, node_output)
                    except Exception as cb_err:
                        print(f"  ⚠️ Callback error: {cb_err}")
    except Exception as e:
        print(f"  ⚠️ Stream error, falling back to invoke: {e}")
        final_state = graph.invoke(initial_state)

    print(f"\n{'='*60}")
    print(f"📊 FINAL REPORT")
    print(f"{'='*60}")
    print(f"   Files generated: {len(final_state.get('files', {}))}")
    print(f"   Tests passed: {final_state.get('tests_passed', False)}")
    print(f"   Preview URL: {final_state.get('preview_url', 'N/A')}")
    print(f"   Project dir: {project_dir}")
    print(f"{'='*60}\n")

    return final_state


def run_chat_pipeline(user_prompt: str, existing_state: dict):
    """
    Run the chat refinement pipeline on an existing project.
    
    Args:
        user_prompt: Follow-up modification request
        existing_state: State from previous generation
    """
    print(f"\n💬 CHAT REFINEMENT: {user_prompt[:80]}...")

    graph = build_chat_graph()

    # Update state with new prompt
    existing_state["user_prompt"] = user_prompt
    existing_state["is_followup"] = True

    final_state = graph.invoke(existing_state)

    print(f"   ✅ Chat refinement complete")
    return final_state


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="AI Code Factory")
    parser.add_argument("prompt", nargs="?", default=None, help="Application description")
    parser.add_argument("--name", default=None, help="Project name")

    args = parser.parse_args()

    if args.prompt:
        run_pipeline(args.prompt, project_name=args.name)
    else:
        # Interactive mode
        print("🏭 AI Code Factory — Interactive Mode")
        print("Type your app idea and press Enter:\n")
        prompt = input(">>> ").strip()
        if prompt:
            run_pipeline(prompt)
        else:
            print("No prompt provided. Exiting.")


if __name__ == "__main__":
    main()
