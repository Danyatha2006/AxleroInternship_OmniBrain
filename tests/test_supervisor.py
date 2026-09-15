from orchestrator.supervisor import route_query


def test_route_query_search():
    assert route_query("What is artificial intelligence?") == "search"


def test_route_query_sql():
    assert route_query("What is the total sales in 2025?") == "sql"


def test_route_query_vision():
    assert route_query("Show me the image diagram") == "vision"
