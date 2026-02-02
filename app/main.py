"""
main.py
-------
Entry point for the AI Code Factory.

This is a GENERALIZED application generator that can create
any type of web application based on natural language prompts.
"""

import re
import sys
from datetime import datetime
from pathlib import Path

from app.graph.graph import build_graph


def slugify(text: str) -> str:
    """Convert text to a valid folder name."""
    # Convert to lowercase and replace spaces with underscores
    slug = text.lower()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[\s_-]+', '_', slug)
    slug = slug.strip('_')
    return slug[:50] or "project"


def create_project_dir(prompt: str) -> str:
    """Create a unique project directory based on prompt."""
    base_name = slugify(prompt)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    project_name = f"{base_name}_{timestamp}"
    
    project_dir = Path("app/workspace/generated_projects") / project_name
    project_dir.mkdir(parents=True, exist_ok=True)
    
    return str(project_dir)


def run_pipeline(user_prompt: str):
    """
    Run the generation pipeline programmatically (for web UI).
    
    Args:
        user_prompt: Natural language description of the app to build.
    
    Returns:
        Path to the generated project directory.
    """
    # Create unique project directory
    project_dir = create_project_dir(user_prompt)
    
    # Build the graph
    graph = build_graph()
    
    # Initialize state
    initial_state = {
        "user_prompt": user_prompt,
        "project_name": slugify(user_prompt),
        "project_dir": project_dir,
        "project_scope": None,
        "architecture": None,
        "contract": None,
        "files": {},
        "file_plan": [],
        "tests_passed": None,
        "error_message": None,
        "repair_attempts": 0,
        "extracted_routes": [],
        "request_fields": {},
        "preview_started": False,
        "preview_url": None,
        "generation_issues": [],
        "files_to_regenerate": [],
        "failed_file_history": [],
    }
    
    # Run the graph
    final_state = graph.invoke(initial_state)
    
    return project_dir, final_state


def main(user_prompt: str = None):
    """
    Run the AI Code Factory.
    
    Args:
        user_prompt: Natural language description of the app to build.
                    If None, will prompt user for input.
    """
    
    print("\n" + "=" * 60)
    print("🏭 AI CODE FACTORY - Generalized Application Generator")
    print("=" * 60)
    
    # Get user prompt
    if user_prompt is None:
        print("\nDescribe the application you want to build:")
        print("(Examples: 'todo app', 'calculator', 'note taking app', 'expense tracker')\n")
        user_prompt = input(">>> ").strip()
        
        if not user_prompt:
            print("❌ No prompt provided. Exiting.")
            return None
    
    print(f"\n📝 Building: {user_prompt}")
    
    # Create unique project directory
    project_dir = create_project_dir(user_prompt)
    print(f"📁 Project directory: {project_dir}")
    
    # Build the graph
    graph = build_graph()
    
    # Initialize state
    initial_state = {
        "user_prompt": user_prompt,
        "project_name": slugify(user_prompt),
        "project_dir": project_dir,
        "project_scope": None,
        "architecture": None,
        "contract": None,
        "files": {},
        "file_plan": [],
        "tests_passed": None,
        "error_message": None,
        "repair_attempts": 0,
        "extracted_routes": [],
        "request_fields": {},
        "preview_started": False,
        "preview_url": None,
    }
    
    print("\n" + "=" * 60)
    print("🚀 Starting generation pipeline...")
    print("=" * 60)
    
    try:
        # Run the graph
        final_state = graph.invoke(initial_state)
        
        print("\n" + "=" * 60)
        print("✅ GENERATION COMPLETE!")
        print("=" * 60)
        
        # Print summary
        print(f"\n📊 Summary:")
        print(f"   Project: {final_state.get('project_name', 'unknown')}")
        print(f"   Directory: {final_state.get('project_dir', 'unknown')}")
        print(f"   Files generated: {len(final_state.get('files', {}))}")
        print(f"   Tests passed: {final_state.get('tests_passed', False)}")
        print(f"   Repair attempts: {final_state.get('repair_attempts', 0)}")
        
        if final_state.get('preview_url'):
            print(f"   Preview URL: {final_state.get('preview_url')}")
        
        return final_state
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Generation interrupted by user.")
        return None
    except Exception as e:
        print(f"\n❌ Error during generation: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    # Allow passing prompt as command line argument
    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:])
        main(prompt)
    else:
        main()
