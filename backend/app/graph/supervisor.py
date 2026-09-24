from langgraph.graph import END, START, StateGraph

from app.graph.state import OmniBrainState
from app.services.search_agent import SearchAgent
from app.services.rag_service import (
    build_context_from_results,
    generate_answer_from_context,
)
from app.services.langfuse_service import langfuse
from app.vision.vision_agent import VisionAgent


search_agent = SearchAgent()
vision_agent = VisionAgent()


def search_node(state: OmniBrainState):
    query = state.get("query", "")
    top_k = state.get("top_k", 5)
    document_id = state.get("document_id")

    result = search_agent.run(
        query=query,
        top_k=top_k,
        document_id=document_id,
    )

    return {
        "search_results": result.get("results", [])
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

    graph.add_node(
        "search",
        search_node,
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

    graph.add_edge(
        START,
        "search",
    )

    graph.add_edge(
        "search",
        "vision",
    )

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

    return graph.compile()


search_graph = build_search_graph()