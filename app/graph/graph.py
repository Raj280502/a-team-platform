from langgraph.graph import StateGraph, END

from app.core.state import ProjectState
from app.graph.nodes.strategist_node import strategist_node
from app.graph.nodes.architect_node import architect_node

from app.graph.nodes.coder_plan_node import coder_plan_node
from app.graph.nodes.coder_file_node import coder_file_node

from app.graph.nodes.test_node import test_node
from app.graph.nodes.repair_node import repair_node
from app.graph.edges import should_repair
from app.graph.nodes.write_files_node import write_files_node
from app.graph.nodes.docker_node import docker_node


def build_graph():
    graph = StateGraph(ProjectState)

    graph.add_node("strategist", strategist_node)
    graph.add_node("architect", architect_node)

    # NEW ATOMIC PIPELINE
    graph.add_node("coder_plan", coder_plan_node)
    graph.add_node("coder_file", coder_file_node)

    graph.add_node("write_files", write_files_node)
    graph.add_node("test", test_node)
    graph.add_node("repair", repair_node)
    graph.add_node("docker", docker_node)

    graph.set_entry_point("strategist")

    graph.add_edge("strategist", "architect")
    graph.add_edge("architect", "coder_plan")
    graph.add_edge("coder_plan", "coder_file")
    graph.add_edge("coder_file", "write_files")
    graph.add_edge("write_files", "test")
    graph.add_edge("test", "docker")

    graph.add_conditional_edges(
        "test",
        should_repair,
        {
            "repair": "repair",
            "end": END,
        }
    )

    graph.add_edge("repair", "coder_file")  # repair regenerates only broken file(s)

    return graph.compile()
