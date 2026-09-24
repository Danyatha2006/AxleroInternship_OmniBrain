# LangGraph Supervisor / Orchestrator

The Supervisor is responsible for deciding which specialized agent should handle a user query.

## Agent Routing

- **Search Agent** → General information and document-related queries
- **SQL Agent** → Data, database, numerical and statistical queries
- **Vision Agent** → Image, chart, graph and visual queries

## Routing Flow

User Query
    ↓
Supervisor
    ↓
┌──────────────┬──────────────┬──────────────┐
Search Agent   SQL Agent      Vision Agent

The current implementation uses rule-based keyword routing for testing.
It can later be extended with an LLM-based Supervisor.
