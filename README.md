# MCP App

This repository contains a multi-language, multi-service solution for building and interacting with Model Context Protocol (MCP) servers and clients. It includes:

- **api/**: ASP.NET Core Web API for weather forecasting.
- **mcp-server/**: Python MCP server exposing tools (e.g., weather queries).
- **mcp-client/**: Python MCP client that connects to the MCP server and can interact with local LLMs (Ollama) and MCP tools.

## Features

- Query weather forecasts via REST API or MCP tools.
- Use local LLMs (Ollama) for natural language interaction and tool-calling.
- Modular design: add more tools or endpoints easily.
- Supports both synchronous and asynchronous workflows.

## Structure

```
api/           # ASP.NET Core Web API (C#)
mcp-server/    # Python MCP server (tool provider)
mcp-client/    # Python MCP client (tool consumer, LLM integration)
```

## Getting Started

### Prerequisites

- Python 3.10+
- .NET 8 SDK
- Ollama (for local LLMs)

### Running the API

```bash
cd api
dotnet run
```
API will be available at `http://localhost:5024` (default).

### Running the MCP Server

```bash
cd mcp-server
python server.py
```

### Running the MCP Client

```bash
cd mcp-client
python client.py
```

## Tool Calling with Ollama

- The MCP client can wrap MCP tools as Python functions and pass them to Ollama for tool-calling (supported models only).
- Example: Ask "What is the weather like in Rotterdam?" and the LLM will call the MCP weather tool.

## Customization

- Add new tools to server.py.
- Add new endpoints to Program.cs.
- Update client logic in client.py for more advanced agent workflows.
