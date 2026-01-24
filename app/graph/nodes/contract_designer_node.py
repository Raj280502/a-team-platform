from app.core.state import ProjectState


def contract_designer_node(state: ProjectState) -> ProjectState:
    """
    This node NO LONGER uses LLM.

    Contract is derived PURELY from the routes extracted by coder_plan_node.
    Law must come from code plan, not from English description.
    """

    extracted_routes = state.get("extracted_routes", [])

    contract = {
        "backend": {
            "must_exist": [
                "backend/app.py",
                "frontend/index.html",
                "frontend/src/App.jsx",
            ],
            "must_expose_routes": extracted_routes,
        }
    }

    return {"contract": contract}
