"""
graph.py - LangGraph workflow definition.
Enhanced with SDLC planning stages and stage-gated execution.
"""

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

# SDLC planning nodes
from app.graph.nodes.overview_node import overview_node
from app.graph.nodes.requirements_node import requirements_node
from app.graph.nodes.user_research_node import user_research_node
from app.graph.nodes.task_flows_node import task_flows_node
from app.graph.nodes.user_stories_node import user_stories_node

from app.graph.edges import should_repair, should_deploy


def end_node(state: ProjectState) -> ProjectState:
    """Final node — marks generation complete."""
    print("\n🏁 DONE! Project generation complete.")
    return {
        "current_step": "complete",
    }


# ============================================
# SDLC STAGE GRAPHS (stage-gated, one at a time)
# ============================================

def build_stage_graph(stage_name: str):
    """
    Build a single-node LangGraph for one SDLC stage.
    This allows each stage to run independently (stage-gated).
    
    Args:
        stage_name: One of 'overview', 'requirements', 'user_research',
                    'task_flows', 'user_stories'
    """
    stage_nodes = {
        "overview": overview_node,
        "requirements": requirements_node,
        "user_research": user_research_node,
        "task_flows": task_flows_node,
        "user_stories": user_stories_node,
    }

    if stage_name not in stage_nodes:
        raise ValueError(f"Unknown stage: {stage_name}")

    graph = StateGraph(ProjectState)
    graph.add_node(stage_name, stage_nodes[stage_name])
    graph.set_entry_point(stage_name)
    graph.set_finish_point(stage_name)

    compiled = graph.compile()
    print(f"✅ SDLC stage '{stage_name}' graph compiled")
    return compiled


# Stage execution order
SDLC_STAGES = ["overview", "requirements", "user_research", "task_flows", "user_stories"]

STAGE_LABELS = {
    "overview": "Project Overview",
    "requirements": "Project Requirements",
    "user_research": "User Research",
    "task_flows": "Task Flows",
    "user_stories": "User Stories",
}


# ============================================
# CODE GENERATION GRAPH (runs after all SDLC stages approved)
# ============================================

def build_graph():
    """
    Builds the code generation pipeline (runs AFTER SDLC planning stages):
    
    strategist → architect → coder_plan → coder_file → write_files → test
                                                                        ↓
                                                                  [pass] → preview → end
                                                                  [fail] → repair → coder_file → ...
    """
    graph = StateGraph(ProjectState)

    # ═══════════ PHASE 1: COGNITION ═══════════
    graph.add_node("strategist", strategist_node)
    graph.add_node("architect", architect_node)

    # ═══════════ PHASE 2: MANUFACTURING ═══════════
    graph.add_node("coder_plan", coder_plan_node)
    graph.add_node("coder_file", coder_file_node)
    graph.add_node("write_files", write_files_node)

    # ═══════════ PHASE 3: TESTING ═══════════
    graph.add_node("test", test_node)

    # ═══════════ PHASE 4: SELF-HEALING ═══════════
    graph.add_node("repair", repair_node)

    # ═══════════ PHASE 5: PREVIEW ═══════════
    graph.add_node("preview", preview_node)

    # ═══════════ PHASE 6: END ═══════════
    graph.add_node("end", end_node)

    # ═══════════ EDGES ═══════════
    graph.set_entry_point("strategist")
    graph.add_edge("strategist", "architect")
    graph.add_edge("architect", "coder_plan")
    graph.add_edge("coder_plan", "coder_file")
    graph.add_edge("coder_file", "write_files")
    graph.add_edge("write_files", "test")

    # Test → Repair loop or Preview
    graph.add_conditional_edges(
        "test",
        should_repair,
        {
            "repair": "repair",
            "preview": "preview",
            "end": "end",
        },
    )

    # Repair loops back to coder_file
    graph.add_edge("repair", "coder_file")

    # Preview → End
    graph.add_conditional_edges(
        "preview",
        should_deploy,
        {
            "end": "end",
        },
    )

    compiled = graph.compile()
    print("✅ Code generation pipeline compiled successfully")
    return compiled


def build_chat_graph():
    """
    Builds a simpler graph for iterative chat refinement.
    
    chat → write_files → preview → end
    """
    from app.graph.nodes.chat_node import chat_node

    graph = StateGraph(ProjectState)

    graph.add_node("chat", chat_node)
    graph.add_node("write_files", write_files_node)
    graph.add_node("preview", preview_node)
    graph.add_node("end", end_node)

    graph.set_entry_point("chat")
    graph.add_edge("chat", "write_files")
    graph.add_edge("write_files", "preview")
    graph.add_edge("preview", "end")

    compiled = graph.compile()
    print("✅ Chat refinement graph compiled")
    return compiled
