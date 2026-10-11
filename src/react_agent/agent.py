import logging
from os import getenv

import httpx
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

from react_agent.tools import calculator, fetch_page

logger = logging.getLogger(__name__)

GITHUB_TOOLS_ALLOWLIST = {"get_issue", "create_issue", "list_issues"}


def make_safe_tool(tool):
    """Wrap tool execution so exceptions return error messages to the model instead of crashing."""
    orig_coroutine = getattr(tool, "coroutine", None)
    if orig_coroutine:
        async def safe_coroutine(*args, **kwargs):
            try:
                return await orig_coroutine(*args, **kwargs)
            except Exception as e:
                tool_name = getattr(tool, "name", "tool")
                logger.warning("Tool %s failed: %s", tool_name, e)
                if getattr(tool, "response_format", None) == "content_and_artifact":
                    return (f"Error executing {tool_name}: {e}", None)
                return f"Error executing {tool_name}: {e}"
        tool.coroutine = safe_coroutine
    return tool


def get_graph_closure(
    model_id=None,
    base_url=None,
    api_key=None,
    mcp_tools=None,
):
    if not api_key:
        api_key = getenv("API_KEY")
    if not base_url:
        base_url = getenv("BASE_URL")
    if not model_id:
        model_id = getenv("MODEL_ID")

    if not base_url:
        raise ValueError("BASE_URL is required. Set it via argument or BASE_URL env var.")

    raw_tools = [calculator, fetch_page] + [
        t for t in (mcp_tools or []) if t.name in GITHUB_TOOLS_ALLOWLIST
    ]
    tools = [make_safe_tool(t) for t in raw_tools]
    logger.info("tools: %s", [tool.name for tool in tools])

    chat = ChatOpenAI(
        model=model_id,
        temperature=0.01,
        api_key=api_key or "not-needed",
        base_url=base_url,
        streaming=True,
        http_client=httpx.Client(verify=False),
        http_async_client=httpx.AsyncClient(verify=False),
    )

    system_prompt = """You are a helpful assistant. When you receive a result from a tool,
        use that information to provide a FINAL answer to the user immediately.
        Do NOT call tools repeatedly for the same question."""

    return create_agent(model=chat, tools=tools, system_prompt=system_prompt)

