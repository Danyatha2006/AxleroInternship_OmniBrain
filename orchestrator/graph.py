from langgraph.graph import StateGraph, START, END

from orchestrator.state import AgentState
from orchestrator.supervisor import route_query

from app.services.qdrant_search import search_qdrant
from app.services.relevance_checker import is_relevant
from app.services.query_rewriter import rewrite_query
from app.services.rag_service import (
    build_context_from_results,
    generate_answer_from_context,
)


MAX_RETRIES = 2


def supervisor_node(state: AgentState) -> AgentState:
    query = state["query"]

    selected_agent = route_query(query)

    return {
        **state,
        "selected_agent": selected_agent,
        "retry_count": 0,
    }


def search_node(state: AgentState) -> AgentState:
    """
    Retrieve relevant document chunks from Qdrant.
    Uses the rewritten query when a retry is happening.
    """

    query = state.get("rewritten_query") or state["query"]

    results = search_qdrant(
        query=query,
        top_k=5,
    )

    best_score = max(
        (
            float(result.get("score", 0.0))
            for result in results
        ),
        default=0.0,
    )

    return {
        **state,
        "retrieved_results": results,
        "relevance_score": best_score,
        "agent_result": f"Retrieved {len(results)} results.",
    }


def relevance_check_node(state: AgentState) -> AgentState:
    """
    Check whether the retrieved information is relevant enough.
    """

    results = state.get("retrieved_results", [])

    relevant = is_relevant(results)

    return {
        **state,
        "agent_result": (
            "Retrieved information is relevant."
            if relevant
            else "Retrieved information is not relevant."
        ),
    }


def rewrite_query_node(state: AgentState) -> AgentState:
    """
    Rewrite the original query when retrieval is not relevant.
    """

    original_query = state["query"]

    rewritten = rewrite_query(original_query)

    retry_count = state.get("retry_count", 0) + 1

    return {
        **state,
        "rewritten_query": rewritten,
        "retry_count": retry_count,
        "agent_result": f"Query rewritten for retry {retry_count}.",
    }


def sql_node(state: AgentState) -> AgentState:
    return {
        **state,
        "agent_result": f"SQL agent selected for: {state['query']}",
    }


def vision_node(state: AgentState) -> AgentState:
    return {
        **state,
        "agent_result": f"Vision agent selected for: {state['query']}",
    }


def final_response_node(state: AgentState) -> AgentState:
    """
    Generate the final answer after retrieval.
    """

    results = state.get("retrieved_results", [])

    if results and is_relevant(results):
        context, _ = build_context_from_results(results)

        answer = generate_answer_from_context(
            question=state.get(
                "rewritten_query"
            ) or state["query"],
            context=context,
        )

        return {
            **state,
            "final_response": answer,
        }

    return {
        **state,
        "final_response": (
            "I could not find sufficiently relevant "
            "information in the document to answer this question."
        ),
    }


def route_to_agent(state: AgentState) -> str:
    return state["selected_agent"]


def route_after_relevance(state: AgentState) -> str:
    """
    Decide whether to answer or retry retrieval.
    """

    results = state.get("retrieved_results", [])

    if is_relevant(results):
        return "final_response"

    retry_count = state.get("retry_count", 0)

    if retry_count < MAX_RETRIES:
        return "rewrite_query"

    return "final_response"


def build_graph():
    graph = StateGraph(AgentState)

    # Nodes
    graph.add_node("supervisor", supervisor_node)

    graph.add_node("search", search_node)
    graph.add_node("relevance_check", relevance_check_node)
    graph.add_node("rewrite_query", rewrite_query_node)

    graph.add_node("sql", sql_node)
    graph.add_node("vision", vision_node)

    graph.add_node("final_response", final_response_node)

    # Start
    graph.add_edge(START, "supervisor")

    # Supervisor → Agent
    graph.add_conditional_edges(
        "supervisor",
        route_to_agent,
        {
            "search": "search",
            "sql": "sql",
            "vision": "vision",
        },
    )

    # Search → Relevance Check
    graph.add_edge(
        "search",
        "relevance_check",
    )

    # Relevance Check → Answer or Retry
    graph.add_conditional_edges(
        "relevance_check",
        route_after_relevance,
        {
            "final_response": "final_response",
            "rewrite_query": "rewrite_query",
        },
    )

    # Rewrite → Search again
    graph.add_edge(
        "rewrite_query",
        "search",
    )

    # SQL / Vision → Final Response
    graph.add_edge(
        "sql",
        "final_response",
    )

    graph.add_edge(
        "vision",
        "final_response",
    )

    # End
    graph.add_edge(
        "final_response",
        END,
    )

    return graph.compile()


app = build_graph()