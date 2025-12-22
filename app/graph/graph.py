from langgraph.graph import StateGraph, END

from app.core.state import ProjectState
from app.graph.nodes.strategist_node import strategist_node
from app.graph.nodes.architect_node import architect_node
from app.graph.nodes.generate_node import generate_node
from app.graph.nodes.test_node import test_node
from app.graph.nodes.repair_node import repair_node
from app.graph.edges import should_repair


def build_graph():
    graph = StateGraph(ProjectState)

    graph.add_node("strategist", strategist_node)
    graph.add_node("architect", architect_node)
    graph.add_node("generate", generate_node)
    graph.add_node("test", test_node)
    graph.add_node("repair", repair_node)

    graph.set_entry_point("strategist")

    graph.add_edge("strategist", "architect")
    graph.add_edge("architect", "generate")
    graph.add_edge("generate", "test")

    graph.add_conditional_edges(
        "test",
        should_repair,
        {
            "repair": "repair",
            "end": END,
        }
    )

    graph.add_edge("repair", "test")

    return graph.compile()
