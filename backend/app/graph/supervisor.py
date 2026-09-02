from typing import Any

from langgraph.graph import END, START, StateGraph

from app.graph.state import OmniBrainState
from app.services.search_agent import SearchAgent
from app.services.rag_service import (
    build_context_from_results,
    generate_answer_from_context,
)


search_agent = SearchAgent()


def search_node(state: OmniBrainState) -> dict[str, Any]:
    """
    LangGraph node responsible for executing the Search Agent.
    """

    query = state.get("query", "")
    top_k = state.get("top_k", 5)
    document_id = state.get("document_id")

    result = search_agent.run(
        query=query,
        top_k=top_k,
        document_id=document_id,
    )

    return {
        "search_results": result.get(
            "results",
            [],
        )
    }


def context_node(state: OmniBrainState) -> dict[str, Any]:
    """
    Build LLM context from Search Agent results.
    """

    search_results = state.get(
        "search_results",
        [],
    )

    context, _ = build_context_from_results(
        search_results,
    )

    return {
        "context": context,
    }


def answer_node(state: OmniBrainState) -> dict[str, Any]:
    """
    Generate the final answer from retrieved context.
    """

    query = state.get(
        "query",
        "",
    )

    context = state.get(
        "context",
        "",
    )

    answer = generate_answer_from_context(
        question=query,
        context=context,
    )

    return {
        "final_answer": answer,
    }


def build_search_graph():
    """
    Build the LangGraph workflow.

    Flow:
        START
          ↓
        SearchAgent
          ↓
        Context Builder
          ↓
        Answer Generator
          ↓
        END
    """

    graph = StateGraph(OmniBrainState)

    graph.add_node(
        "search",
        search_node,
    )

    graph.add_node(
        "context",
        context_node,
    )

    graph.add_node(
        "answer",
        answer_node,
    )

    graph.add_edge(
        START,
        "search",
    )

    graph.add_edge(
        "search",
        "context",
    )

    graph.add_edge(
        "context",
        "answer",
    )

    graph.add_edge(
        "answer",
        END,
    )

    return graph.compile()


search_graph = build_search_graph()