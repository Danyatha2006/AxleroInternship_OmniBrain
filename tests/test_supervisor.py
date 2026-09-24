from orchestrator.supervisor import route_query


def test_route_query_search():
    assert route_query("What is artificial intelligence?") == "search"


def test_route_query_sql():
    assert route_query("What is the total sales in 2025?") == "sql"


def test_route_query_vision():
    assert route_query("Show me the image diagram") == "vision"


def test_route_query_case_insensitive():
    assert route_query("SHOW ME A CHART") == "vision"


def test_route_query_sql_keyword():
    assert route_query("What is the total revenue?") == "sql"


def test_route_query_general_question():
    assert route_query("Tell me about Python") == "search"


def test_route_query_case_insensitive():
    assert route_query("SHOW ME A CHART") == "vision"


def test_route_query_sql_keyword():
    assert route_query("What is the total revenue?") == "sql"


def test_route_query_general_question():
    assert route_query("Tell me about Python") == "search"
