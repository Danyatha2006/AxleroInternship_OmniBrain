from typing import TypedDict


class AgentState(TypedDict, total=False):
    """
    Shared state passed between LangGraph nodes.
    """

    # Original user query
    query: str

    # Agent selected by supervisor
    selected_agent: str

    # Result returned by the selected agent
    agent_result: str

    # Final response shown to the user
    final_response: str

    # Week 3 Self-RAG fields
    retrieved_results: list[dict]
    relevance_score: float
    retry_count: int
    rewritten_query: str