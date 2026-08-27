from langgraph.graph import StateGraph, START, END

from orchestrator.state import AgentState
from orchestrator.supervisor import route_query


def supervisor_node(state: AgentState) -> AgentState:
    """
    Supervisor node.

    Determines which agent should handle the query.
    """

    query = state["query"]

    selected_agent = route_query(query)

    return {
        **state,
        "selected_agent": selected_agent,
    }


def search_node(state: AgentState) -> AgentState:
    """
    Temporary Search Agent node.

    This will later call the team's actual
    vector database / retrieval implementation.
    """

    return {
        **state,
        "agent_result": f"Search agent selected for: {state['query']}",
    }


def sql_node(state: AgentState) -> AgentState:
    """
    Temporary SQL Agent node.

    This will later call the team's actual
    SQL implementation.
    """

    return {
        **state,
        "agent_result": f"SQL agent selected for: {state['query']}",
    }


def vision_node(state: AgentState) -> AgentState:
    """
    Temporary Vision Agent node.

    This will later call the team's actual
    VLM / image retrieval implementation.
    """

    return {
        **state,
        "agent_result": f"Vision agent selected for: {state['query']}",
    }


def final_response_node(state: AgentState) -> AgentState:
    """
    Create the final response from the selected agent's result.
    """

    return {
        **state,
        "final_response": state.get(
            "agent_result",
            "No agent result was produced."
        ),
    }


def route_to_agent(state: AgentState) -> str:
    """
    Choose the next LangGraph node based on
    the Supervisor's decision.
    """

    return state["selected_agent"]


def build_graph():
    """
    Build the LangGraph Supervisor workflow.
    """

    graph = StateGraph(AgentState)

    # Nodes
    graph.add_node("supervisor", supervisor_node)
    graph.add_node("search", search_node)
    graph.add_node("sql", sql_node)
    graph.add_node("vision", vision_node)
    graph.add_node("final_response", final_response_node)

    # Start → Supervisor
    graph.add_edge(START, "supervisor")

    # Supervisor → selected agent
    graph.add_conditional_edges(
        "supervisor",
        route_to_agent,
        {
            "search": "search",
            "sql": "sql",
            "vision": "vision",
        },
    )

    # Agent → Final Response
    graph.add_edge("search", "final_response")
    graph.add_edge("sql", "final_response")
    graph.add_edge("vision", "final_response")

    # Final Response → End
    graph.add_edge("final_response", END)

    return graph.compile()


app = build_graph()