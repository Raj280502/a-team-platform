"""
chat_node.py
------------
Handles iterative refinement of existing projects.
Takes user follow-up messages and modifies existing code.
"""

from app.core.state import ProjectState
from app.core.llm import get_llm
from app.utils.file_ops import normalize_code
import json


def chat_node(state: ProjectState) -> ProjectState:
    """
    Iterative refinement node: takes a follow-up user message
    and modifies/adds files to the existing project.
    """
    print("\n💬 CHAT: Processing refinement request...")

    llm = get_llm(role="chat")

    user_prompt = state.get("user_prompt", "")
    existing_files = state.get("files", {})
    project_scope = state.get("project_scope", {})

    # Build context from existing code
    file_summaries = []
    for file_path, content in existing_files.items():
        lines = content.split("\n")
        preview = "\n".join(lines[:40])  # First 40 lines for context
        file_summaries.append(f"### {file_path}\n```\n{preview}\n```")

    files_context = "\n\n".join(file_summaries)

    prompt = f"""You are modifying an existing web application based on a user's follow-up request.

EXISTING PROJECT:
Goal: {project_scope.get('project_goal', 'N/A')}

EXISTING FILES:
{files_context}

USER REQUEST:
{user_prompt}

INSTRUCTIONS:
1. Analyze what the user wants changed
2. Identify which files need modification
3. For EACH file that needs changes, output the COMPLETE updated file content
4. If new files are needed, include them too
5. Do NOT modify files that don't need changes

Output your response as a JSON object with this structure:
{{
  "modified_files": {{
    "path/to/file": "complete file content here"
  }},
  "summary": "Brief description of what was changed"
}}

RULES:
- Output ONLY valid JSON
- File contents must be COMPLETE (not diffs or patches)
- Use the same file paths as the existing project
- Do NOT remove or break existing functionality
- Make minimal, targeted changes
"""

    response = llm.invoke(prompt)
    raw = response.content.strip()

    # Try to parse the JSON response
    try:
        # Extract JSON from potential markdown wrapper
        if "```json" in raw:
            raw = raw.split("```json")[1].split("```")[0]
        elif "```" in raw:
            raw = raw.split("```")[1].split("```")[0]

        result = json.loads(raw)
        modified_files = result.get("modified_files", {})
        summary = result.get("summary", "Applied changes")

        # Merge modified files with existing files
        updated_files = existing_files.copy()
        for file_path, content in modified_files.items():
            updated_files[file_path] = normalize_code(content)
            print(f"   ✏️ Modified: {file_path}")

        print(f"   📝 Summary: {summary}")

        # Update chat history
        chat_history = state.get("chat_history", [])
        chat_history.append({"role": "user", "content": user_prompt})
        chat_history.append({"role": "assistant", "content": summary})

        return {
            "files": updated_files,
            "chat_history": chat_history,
            "current_step": "chat_complete",
        }

    except (json.JSONDecodeError, Exception) as e:
        print(f"   ❌ Failed to parse chat response: {e}")
        print(f"   Raw response: {raw[:200]}...")

        chat_history = state.get("chat_history", [])
        chat_history.append({"role": "user", "content": user_prompt})
        chat_history.append({"role": "assistant", "content": f"Error: {str(e)}"})

        return {
            "chat_history": chat_history,
            "current_step": "chat_error",
        }
