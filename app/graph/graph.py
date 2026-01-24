from langgraph.graph import StateGraph
from app.core.state import ProjectState

from app.graph.nodes.strategist_node import strategist_node
from app.graph.nodes.architect_node import architect_node
from app.graph.nodes.contract_designer_node import contract_designer_node
from app.graph.nodes.contract_verify_node import contract_verify_node

from app.graph.nodes.coder_plan_node import coder_plan_node
from app.graph.nodes.coder_file_node import coder_file_node

from app.graph.nodes.write_files_node import write_files_node
from app.graph.nodes.test_node import test_node
from app.graph.nodes.repair_node import repair_node

from app.graph.nodes.docker_scaffold_node import docker_scaffold_node
from app.graph.nodes.docker_node import docker_node
from app.graph.nodes.end_node import end_node

from app.graph.edges import should_repair


def build_graph():
    graph = StateGraph(ProjectState)

    # Core cognition
    graph.add_node("strategist", strategist_node)
    graph.add_node("architect", architect_node)
    graph.add_node("contract", contract_designer_node)

    # Law verification
    graph.add_node("verify", contract_verify_node)

    # Manufacturing
    graph.add_node("coder_plan", coder_plan_node)
    graph.add_node("coder_file", coder_file_node)
    graph.add_node("write_files", write_files_node)

    # Reality
    graph.add_node("test", test_node)

    # Self-healing
    graph.add_node("repair", repair_node)

    # Deployment
    graph.add_node("docker_scaffold", docker_scaffold_node)
    graph.add_node("docker", docker_node)

    # Legal halting state
    graph.add_node("end", end_node)

    # Entry point
    graph.set_entry_point("strategist")

    # Main pipeline (CORRECT ORDER)

    graph.add_edge("strategist", "architect")

    # LAW FIRST
    graph.add_edge("architect", "contract")
    graph.add_edge("contract", "verify")
    
    # THEN CODE
    graph.add_edge("verify", "coder_plan")
    graph.add_edge("coder_plan", "coder_file")
    graph.add_edge("coder_file", "write_files")

    # THEN REALITY CHECK
    graph.add_edge("write_files", "test")

    # Repair / Deploy governor
    graph.add_conditional_edges(
        "test",
        should_repair,
        {
            "repair": "repair",
            "docker": "docker_scaffold",
            "end": "end",
        },
    )

    # Deployment
    graph.add_edge("docker_scaffold", "docker")
    graph.add_edge("docker", "end")

    # Repair loop
    graph.add_edge("repair", "write_files")

    return graph.compile()
