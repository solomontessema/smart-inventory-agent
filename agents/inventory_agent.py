import asyncio
import os
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.client import MultiServerMCPClient
from config import AGENT_NAME, OPENAI_API_KEY

MCP_SERVER_DIR = r"C:\Users\solom\OneDrive\Documents\Projects\my-mcp-server-python"
MCP_SERVER_PATH = os.path.join(MCP_SERVER_DIR, "mcp-server.py")
MCP_PYTHON = os.path.join(MCP_SERVER_DIR, "venv", "Scripts", "python.exe")

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=OPENAI_API_KEY)

SYSTEM_PROMPT = f"""
    You are a helpful assistant to manage inventory and find bulk suppliers online for products in the database.
    When replying, use well‑formatted markdown.
    Use the send_email tool to send emails. Pass subject and body as separate arguments.
    The body must be valid HTML. Include greetings and a signature. Your name is {AGENT_NAME}.
    After completing the requested task, log your actions using the log_action tool.
"""


async def _invoke_agent(messages):
    client = MultiServerMCPClient(
        {"inventory": {"command": MCP_PYTHON, "args": [MCP_SERVER_PATH], "transport": "stdio"}}
    )
    tools = await client.get_tools()
    agent = create_agent(
                        model=llm, 
                        tools=tools, 
                        system_prompt=SYSTEM_PROMPT
                        )
    return await agent.ainvoke({"messages": messages})


class _InventoryAgent:
    def invoke(self, input_dict):
        return asyncio.run(_invoke_agent(input_dict["messages"]))


inventory_agent = _InventoryAgent()
