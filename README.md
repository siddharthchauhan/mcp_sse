# MCP SSE Example

This repository contains a minimal example of running a [FastMCP](https://pypi.org/project/fastmcp/) server using Server-Sent Events (SSE) and a simple client that connects to it. The example exposes two basic tools for web search and page content retrieval.

## Requirements

* Python 3.9+
* The following Python packages:
  - `fastmcp`
  - `httpx`
  - `langchain-mcp-adapters`
  - `asyncpg`
  - `neo4j`

You can install everything with `pip`:

```bash
pip install fastmcp httpx langchain-mcp-adapters asyncpg neo4j
```

## Environment Variables

Several environment variables are used or expected by the example and supporting libraries:

| Variable | Description |
|----------|-------------|
| `BRAVE_API_KEY` | Required by the server for performing web searches via the Brave Search API. |
| `POSTGRES_*` | Optional connection details for PostgreSQL when using database-backed tools. |
| `NEO4J_*` | Optional connection details for Neo4j-based tools. |
| `OPENAI_API_KEY` | Optional API key for tools or libraries that integrate with OpenAI. |

At minimum you must set `BRAVE_API_KEY` in your environment for the web search tool to function.

## Running the Server

Start the server which listens on port `9001` by default:

```bash
python server.py
```

You can change the port by setting the `PORT` environment variable before starting the server.

## Running the Client

In a separate terminal, run the client to connect to the server via SSE:

```bash
python client.py
```

The client will attempt to connect to `http://localhost:9001/sse` and list the available tools provided by the server.

