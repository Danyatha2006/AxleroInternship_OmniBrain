from typing import TypedDict


class AgentState(TypedDict, total=False):
    """
    Shared state passed between LangGraph nodes.
    """

    query: str
    selected_agent: str
    agent_result: str
    final_response: str