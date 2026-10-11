# Machha Kiran AI &bull; Production LangGraph ReAct Agent

<div align="center">

[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![LangGraph](https://img.shields.io/badge/framework-LangGraph-orange.svg)](https://langchain-ai.github.io/langgraph/)
[![MCP](https://img.shields.io/badge/protocol-Model_Context_Protocol-purple.svg)](https://modelcontextprotocol.io/)
[![Ollama](https://img.shields.io/badge/inference-Ollama_|_OGX-green.svg)](https://ollama.com/)
[![FastAPI](https://img.shields.io/badge/server-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Author](https://img.shields.io/badge/Author-Machha_Kiran-red.svg)](https://github.com/machhakiran)

**A production-grade, local-first ReAct agent by [Machha Kiran](https://github.com/machhakiran) demonstrating the full lifecycle of agent engineering:**  
*Harness &bull; ReAct Loop &bull; MCP Tool Integration &bull; Sandboxing &bull; Auth Gateway &bull; LLM-Ops*

[Overview](#-overview) &bull;
[Quickstart](#-quickstart) &bull;
[Architecture](#-architecture) &bull;
[MCP Tools](#-mcp--tools) &bull;
[AgentOps & Deployment](#-agentops--production-deployment) &bull;
[API Reference](#-api-reference) &bull;
[Author](#-author)

</div>

---

## 🌟 Overview

Modern autonomous agents require more than just prompt engineering—they require robust loop mechanics, reliable tool protocols, bulletproof error handling, and end-to-end observability.

This repository provides a reference implementation of a **LangGraph ReAct Agent** that transitions seamlessly from a local development sandbox into a hardened Kubernetes / OpenShift production deployment.

### Key Pillars

- 🧠 **Reason & Act Loop**: Built with LangGraph, managing state, recursion limits, and multi-turn tool execution.
- 🔌 **Model Context Protocol (MCP)**: Native integration with MCP servers (e.g. GitHub MCP for issues, PRs, and repositories).
- ⚡ **Local-First Inference**: Zero-cost, privacy-first local inference using **Ollama** (`qwen3:1.7b`) and **OGX**, plus pluggable cloud inference (vLLM, OpenAI, OpenShift).
- 🛡️ **Fault-Tolerant Tool Execution**: Safe tool isolation preventing tool runtime failures from crashing the agent loop.
- 🖥️ **Interactive Cockpit**: Real-time SSE streaming chat playground UI with live status indicator and suggestion prompts.
- 📊 **Enterprise AgentOps**: OpenShell sandboxing, identity-based tool authorization via MCP Gateway, and MLflow distributed tracing.

---

## 🚀 Quickstart

### Prerequisites

- [uv](https://docs.astral.sh/uv/) (recommended) or Python 3.12+
- [GNU Make](https://www.gnu.org/software/make/)
- [Ollama](https://ollama.com/) for local model execution
- Node.js / `npx` (for GitHub MCP server)

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/machhakiran/agent-ops-series.git
cd agent-ops-series

# Initialize environment configuration
make init

# Create virtualenv and install dependencies
make env
```

### 2. Configure Environment

Edit your `.env` file:

```ini
# Local Inference (OGX + Ollama)
API_KEY=not-needed-for-local-development
BASE_URL=http://localhost:8321/v1
MODEL_ID=ollama/qwen3:1.7b

# Tools (optional but recommended)
FIRECRAWL_API_KEY=your-firecrawl-key
GITHUB_TOKEN=your-github-personal-access-token
```

### 3. Start Inference & App

In **Terminal 1** — Start Ollama & OGX Server:
```bash
make ollama MODEL=qwen3:1.7b    # Pulls model and starts Ollama
make ogx-server                 # Starts OGX server on port 8321
```

In **Terminal 2** — Start the Agent API & UI:
```bash
make run-app-fresh              # Starts FastAPI server on port 8000
```

Open your browser at **[http://localhost:8000](http://localhost:8000)** to launch the interactive cockpit.

---

## 🏗️ Architecture

```
+-------------------------------------------------------------------------+
|                           User / Playground UI                          |
|                  (Browser Cockpit · SSE Streaming)                      |
+------------------------------------+------------------------------------+
                                     |
                                     v
+-------------------------------------------------------------------------+
|                     FastAPI Agent Service (main.py)                     |
|                 /chat/completions (OpenAI Compatible)                   |
+------------------------------------+------------------------------------+
                                     |
                                     v
+-------------------------------------------------------------------------+
|                  LangGraph ReAct Agent (react_agent)                    |
|                                                                         |
|   +-----------------------+              +--------------------------+   |
|   |                       |  Tool Calls  |                          |   |
|   |     LLM (ChatOpenAI)  | -----------> |        Tool Node         |   |
|   |      (Qwen3 / vLLM)   | <----------- |     (Safe Execution)     |   |
|   |                       |   Results    |                          |   |
|   +-----------------------+              +--------------------------+   |
+-------------------+------------------------------------+----------------+
                    |                                    |
                    v                                    v
+-----------------------------------+  +----------------------------------+
|          Inference Layer          |  |         External Tools           |
|  - Ollama (qwen3:1.7b)            |  |  - GitHub MCP Server (npx)       |
|  - OGX Server (Port 8321)         |  |  - Firecrawl Web Scraper         |
|  - vLLM (Cloud / OpenShift)       |  |  - AST Math Calculator           |
+-----------------------------------+  +----------------------------------+
```

---

## 🛠️ MCP & Tools

The agent leverages external tools through function calling and the Model Context Protocol:

| Tool | Source | Description |
| :--- | :--- | :--- |
| `calculator` | Native AST | Safe arithmetic and math evaluation without `eval()` |
| `fetch_page` | Firecrawl API | Clean Markdown web scraping fit for LLM context |
| `get_issue` | GitHub MCP | Fetch issue details by owner, repo, and issue number |
| `list_issues` | GitHub MCP | Query and filter open/closed issues in a repository |
| `create_issue` | GitHub MCP | Programmatically create GitHub issues with labels/body |

### MCP Server Configuration

Located in `src/react_agent/tools.py`:
```python
MCP_SERVER_CONFIG = {
    "github": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-github"],
        "transport": "stdio",
        "env": {**os.environ, "GITHUB_PERSONAL_ACCESS_TOKEN": os.getenv("GITHUB_TOKEN", "")},
    },
}
```

---

## 🛡️ AgentOps & Production Deployment

### 1. Containerization
Build container images using Docker or Podman:
```bash
make build       # Build container image
make push        # Push to container registry (Quay/DockerHub/GHCR)
```

### 2. Kubernetes / OpenShift Helm Deployment
Deploy the agent to a cluster using Helm:
```bash
make dry-run     # Inspect rendered Helm manifests
make deploy      # Install or upgrade Helm release
make undeploy    # Clean up deployment from cluster
```

### 3. OpenShell Sandboxing
Enforce strict security boundaries (filesystem restriction, network egress whitelisting, process sandboxing) with NVIDIA OpenShell:
```bash
helm install openshell oci://ghcr.io/nvidia/openshell/helm-chart \
  --version 0.1.0 \
  --namespace openshell \
  -f openshell/values.yaml
```

### 4. Kuadrant MCP Gateway Authorization
Govern tool usage at the gateway level. Enforce fine-grained token identity policies (e.g. read-only vs. read-write access to GitHub MCP servers). See `deployment/mcp_gateway/` for manifests.

### 5. LLM Observability & Tracing
Integrate with MLflow Tracing to record inputs, intermediate tool executions, latency, and token consumption:
```bash
uv run --extra tracing mlflow server --port 5000
```
Enable in `.env`:
```ini
MLFLOW_TRACKING_URI="http://localhost:5000"
MLFLOW_EXPERIMENT_NAME="machhakiran-react-agent"
```

---

## 📡 API Reference

The service exposes an OpenAI-compatible HTTP interface:

### Chat Completions (`POST /chat/completions`)

```bash
curl -X POST http://localhost:8000/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "What is issue 1 in machhakiran/KaviAgent?"}
    ],
    "stream": true
  }'
```

### Health Check (`GET /health`)

```bash
curl http://localhost:8000/health
```
```json
{
  "status": "healthy",
  "agent_initialized": true
}
```

---

## 🧪 Testing

```bash
make test                  # Run unit tests
make test-integration      # Run deployment integration tests
make test-auth-integration # Run auth middleware integration tests
```

---

## 📂 Repository Layout

```
├── main.py                     # FastAPI server & SSE streaming engine
├── agent.yaml                  # Agent deployment metadata specification
├── Makefile                    # Automation commands (setup, run, deploy, test)
├── pyproject.toml              # Python package metadata & dependencies
├── run_ogx_server.yaml         # OGX local inference server configuration
├── src/
│   └── react_agent/
│       ├── agent.py            # LangGraph ReAct agent loop & safe tool runner
│       ├── tools.py            # Native tools & MCP server configuration
│       └── tracing.py          # MLflow observability & telemetry
├── playground/
│   └── templates/
│       └── index.html          # Interactive chat cockpit UI
├── images/
│   ├── machhakiran_logo.svg    # Machha Kiran brand logo
│   └── langgraph_logo.svg      # LangGraph logo
├── deployment/                 # Helm charts and OpenShift manifests
├── openshell/                  # Sandbox policy configurations
└── tests/                      # Unit & integration test suites
```

---

## 👤 Author

**Machha Kiran**
- GitHub: [@machhakiran](https://github.com/machhakiran)
- Repository: [machhakiran/agent-ops-series](https://github.com/machhakiran/agent-ops-series)
- Ecosystem: [machhakiran/KaviAgent](https://github.com/machhakiran/KaviAgent)

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
