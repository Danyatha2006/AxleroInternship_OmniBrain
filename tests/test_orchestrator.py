from orchestrator.graph import app


def test_search_routing():
    result = app.invoke({
        "query": "What is machine learning?"
    })

    assert result["selected_agent"] == "search"
    assert "agent_result" in result
    assert "final_response" in result


def test_sql_routing():
    result = app.invoke({
        "query": "What was the highest revenue in 2024?"
    })

    assert result["selected_agent"] == "sql"
    assert "agent_result" in result
    assert "final_response" in result


def test_vision_routing():
    result = app.invoke({
        "query": "What does the bar chart show?"
    })

    assert result["selected_agent"] == "vision"
    assert "agent_result" in result
    assert "final_response" in result
