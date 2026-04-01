import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from app.core.state import ProjectState
from app.graph.nodes.strategist_node import strategist_node

state: ProjectState = {
    "user_prompt": "build a simple counter app with a reset button",
    "project_name": "counter-test",
    "project_dir": "workspace/counter-test",
    "files": {},
    "current_step": "init",
    "project_scope": {},
    "architecture_plan": {},
    "tests_status": {},
    "tests_passed": False,
    "repair_attempts": 0,
    "preview_url": "",
    "preview_started": False,
}

try:
    result = strategist_node(state)
    print("Strategist succeeded!")
    print(result["project_scope"])
except Exception as e:
    import traceback
    traceback.print_exc()
