
from typing import Any, Dict
from langchain_community.chat_models import ChatOpenAI
from langchain.agents import Tool, AgentExecutor, create_react_agent
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate

from tools.database_reader import read_database_tool         
from tools.web_searcher import web_search_tool        
from tools.email_sender import send_email_tool              
from config import OPENAI_API_KEY, AGENT_NAME, BOSS_NAME

# ---------------------------
# LLM
# ---------------------------
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    api_key=OPENAI_API_KEY
)

# ---------------------------
# Tools
# ---------------------------
tools = [
    Tool(
        name="Database Reader",
        func=read_database_tool,
        description="Execute a SQL query and return raw tabular results."
    ),
    Tool(
        name="Supplier Finder",
        func=web_search_tool,
        description="Search suppliers by product name, barcode, or category."
    ),
    Tool(
        name="Email Sender",
        func=send_email_tool,
        description="Send an email using: subject || body"
    )
]

# ---------------------------
# Prompt
# ---------------------------
prompt_template = PromptTemplate(
    input_variables=["input", "tools", "tool_names"],
    template="""
You are an inventory assistant.

You have access to these tools:
{tools}

Available tool names: {tool_names}

Follow this format exactly:
Thought: <your reasoning>
Action: <one of [{tool_names}]>
Action Input: <input for the action>
Observation: <result of the action>
... (you may repeat Thought/Action/Action Input/Observation as needed) ...
Thought: I now know the final answer
Final Answer: <a concise answer grounded in the latest Observation>

Rules:
- Do not include a Final Answer and an Action in the same step.
- Prefer minimal tool calls. Stop once you have enough information.
- Ground your Final Answer strictly in the actual Observation.
- If a tool fails, try once more with a corrected attempt before concluding.

User query: {input}

{agent_scratchpad}
"""
)


# ---------------------------
# Agent
# ---------------------------
agent = create_react_agent(llm=llm, tools=tools, prompt=prompt_template)

inventory_agent = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=False,
    handle_parsing_errors=True,
    max_iterations=3,
    return_intermediate_steps=False
)

# ---------------------------
# Runner
# ---------------------------
def run_inventory_agent(user_input: str) -> str:
    result = inventory_agent.invoke({
        "input": user_input
    })

    final_answer = result.get("output", "")
    return final_answer
