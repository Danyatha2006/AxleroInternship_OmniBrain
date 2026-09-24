from typing import Literal


AgentName = Literal["search", "sql", "vision"]


def route_query(query: str) -> AgentName:
    """
    Determine which agent should handle the user query.

    This is a temporary rule-based router used for testing.
    It will later be replaced/augmented with an LLM-based
    LangGraph Supervisor.
    """

    query_lower = query.lower()

    vision_keywords = [
        "chart",
        "graph",
        "image",
        "figure",
        "diagram",
        "visual",
        "bar",
        "pie chart",
        "line graph",
    ]

    sql_keywords = [
        "how many",
        "how much",
        "highest",
        "lowest",
        "maximum",
        "minimum",
        "average",
        "sum",
        "total",
        "count",
        "revenue",
        "sales",
        "2024",
        "2025",
    ]

    if any(keyword in query_lower for keyword in vision_keywords):
        return "vision"

    if any(keyword in query_lower for keyword in sql_keywords):
        return "sql"

    return "search"