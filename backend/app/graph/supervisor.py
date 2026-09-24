from langgraph.graph import END, START, StateGraph

from app.graph.state import OmniBrainState
from app.services.search_agent import SearchAgent
from app.services.relevance_checker import is_relevant
from app.services.query_rewriter import rewrite_query
from app.services.rag_service import (
    build_context_from_results,
    generate_answer_from_context,
)
from app.services.langfuse_service import langfuse
from app.vision.vision_agent import VisionAgent


search_agent = SearchAgent()
vision_agent = VisionAgent()


# Maximum number of retrieval attempts:
# 1 = original query
# 2 = rewritten query
MAX_RETRIEVAL_ATTEMPTS = 2


def search_node(state: OmniBrainState):
    """
    Retrieve document chunks using the original query
    or the rewritten query after a failed relevance check.
    """

    query = state.get("rewritten_query") or state.get("query", "")
    top_k = state.get("top_k", 5)
    document_id = state.get("document_id")

    current_attempt = state.get("retrieval_attempt", 0) + 1

    result = search_agent.run(
        query=query,
        top_k=top_k,
        document_id=document_id,
    )

    return {
        "search_results": result.get("results", []),
        "retrieval_attempt": current_attempt,
    }


def relevance_node(state: OmniBrainState):
    """
    Check whether the retrieved results are relevant enough.
    """

    search_results = state.get("search_results", [])

    relevant = is_relevant(search_results)

    return {
        "retrieval_relevant": relevant,
    }


def rewrite_node(state: OmniBrainState):
    """
    Rewrite the original user query when retrieval
    is not relevant enough.
    """

    query = state.get("query", "")

    rewritten = rewrite_query(query)

    return {
        "rewritten_query": rewritten,
    }


def relevance_router(state: OmniBrainState):
    """
    Decide what to do after relevance checking.
    """

    if state.get("retrieval_relevant", False):
        return "relevant"

    attempt = state.get("retrieval_attempt", 1)

    if attempt >= MAX_RETRIEVAL_ATTEMPTS:
        return "no_relevant_information"

    return "rewrite"


def no_relevant_information_node(state: OmniBrainState):
    """
    Handle the case where no relevant information was found
    after the allowed retrieval attempts.
    """

    return {
        "final_answer": (
            "I could not find relevant information in the "
            "available document for this question."
        )
    }


def vision_node(state: OmniBrainState):

    query = state.get("query", "")
    search_results = state.get("search_results", [])

    with langfuse.start_as_current_observation(
        as_type="agent",
        name="vision-agent",
        input={
            "query": query,
            "search_result_count": len(search_results),
        },
    ) as vision_observation:

        vision_results = []

        for result in search_results:

            image_reference = result.get(
                "image_reference"
            )

            if not image_reference:
                continue

            vision_result = vision_agent.run(
                image_reference=image_reference,
                query=query,
            )

            vision_results.append(vision_result)

        vision_observation.update(
            output={
                "vision_result_count": len(
                    vision_results
                )
            }
        )

    return {
        "vision_results": vision_results
    }


def context_node(state: OmniBrainState):

    search_results = state.get("search_results", [])
    vision_results = state.get("vision_results", [])

    context, _ = build_context_from_results(
        search_results
    )

    visual_parts = []

    for result in vision_results:

        answer = result.get(
            "answer",
            "",
        ).strip()

        if not answer:
            continue

        image_reference = result.get(
            "image_reference",
            "",
        )

        visual_parts.append(
            "Visual information:\n"
            + answer
            + "\nImage reference: "
            + image_reference
        )

    if visual_parts:

        visual_context = (
            "\n\n"
            + "\n\n".join(visual_parts)
        )

        if context:
            context += visual_context
        else:
            context = visual_context.strip()

    return {
        "context": context
    }


def answer_node(state: OmniBrainState):

    query = state.get("query", "")
    context = state.get("context", "")

    answer = generate_answer_from_context(
        question=query,
        context=context,
    )

    return {
        "final_answer": answer
    }


def build_search_graph():

    graph = StateGraph(OmniBrainState)

    # Nodes
    graph.add_node(
        "search",
        search_node,
    )

    graph.add_node(
        "relevance",
        relevance_node,
    )

    graph.add_node(
        "rewrite",
        rewrite_node,
    )

    graph.add_node(
        "no_relevant_information",
        no_relevant_information_node,
    )

    graph.add_node(
        "vision",
        vision_node,
    )

    graph.add_node(
        "context",
        context_node,
    )

    graph.add_node(
        "answer",
        answer_node,
    )

    # Initial retrieval
    graph.add_edge(
        START,
        "search",
    )

    graph.add_edge(
        "search",
        "relevance",
    )

    # Self-RAG decision
    graph.add_conditional_edges(
        "relevance",
        relevance_router,
        {
            "relevant": "vision",
            "rewrite": "rewrite",
            "no_relevant_information": "no_relevant_information",
        },
    )

    # Query rewriting
    graph.add_edge(
        "rewrite",
        "search",
    )

    # Vision -> Context -> Answer
    graph.add_edge(
        "vision",
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

    # No relevant information
    graph.add_edge(
        "no_relevant_information",
        END,
    )

    return graph.compile()


search_graph = build_search_graph()