from langgraph.graph import StateGraph
from app.core.state import ProjectState

from app.graph.nodes.strategist_node import strategist_node
from app.graph.nodes.architect_node import architect_node
from app.graph.nodes.coder_plan_node import coder_plan_node
from app.graph.nodes.coder_file_node import coder_file_node
from app.graph.nodes.write_files_node import write_files_node
from app.graph.nodes.test_node import test_node
from app.graph.nodes.repair_node import repair_node
from app.graph.nodes.preview_node import preview_node
from app.graph.nodes.end_node import end_node

from app.graph.edges import should_repair, should_deploy


def build_graph():
    graph = StateGraph(ProjectState)

    # ============================================
    # PHASE 1: COGNITION (Understanding the task)
    # ============================================
    graph.add_node("strategist", strategist_node)
    graph.add_node("architect", architect_node)

    # ============================================
    # PHASE 2: MANUFACTURING (Code generation)
    # ============================================
    graph.add_node("coder_plan", coder_plan_node)
    graph.add_node("coder_file", coder_file_node)
    graph.add_node("write_files", write_files_node)

    # ============================================
    # PHASE 3: TESTING (Validation)
    # ============================================
    graph.add_node("test", test_node)

    # ============================================
    # PHASE 4: SELF-HEALING (Repair loop)
    # ============================================
    graph.add_node("repair", repair_node)

    # ============================================
    # PHASE 5: PREVIEW (Show results to user)
    # ============================================
    graph.add_node("preview", preview_node)

    # ============================================
    # PHASE 6: END
    # ============================================
    graph.add_node("end", end_node)

    # ============================================
    # EDGE DEFINITIONS - CORRECT ORDER
    # ============================================
    
    # Entry point
    graph.set_entry_point("strategist")

    # Cognition flow
    graph.add_edge("strategist", "architect")
    
    # Architecture → Code planning → Code generation
    graph.add_edge("architect", "coder_plan")
    graph.add_edge("coder_plan", "coder_file")
    graph.add_edge("coder_file", "write_files")

    # Write → Test
    graph.add_edge("write_files", "test")

    # Conditional: Test results determine next step
    graph.add_conditional_edges(
        "test",
        should_repair,
        {
            "repair": "repair",
            "preview": "preview",
            "end": "end",
        },
    )

    # Repair loop goes back to write_files
    graph.add_edge("repair", "coder_file")

    # Preview → Ask if user wants Docker deployment
    graph.add_conditional_edges(
        "preview",
        should_deploy,
        {
            "end": "end",
        },
    )

    return graph.compile()
