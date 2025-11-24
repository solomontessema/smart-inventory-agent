
from typing import Any, Dict
from langchain_community.chat_models import ChatOpenAI
from langchain.agents import Tool, AgentExecutor, create_react_agent
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate

from tools.database_reader import read_database_tool         
from tools.web_searcher import web_search_tool        
from tools.email_sender import send_email_tool     
from tools.log_tracker import track_log_tool           
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
        description="Execute a SQL query and return raw tabular results. Use for inventory & thresholds."
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
    ),
    Tool(
        name="Log Tracker",
        func=track_log_tool,
        description="Record actions/results for auditing & debugging."
    ),
]

# ---------------------------
# Prompt
# ---------------------------
prompt_template = PromptTemplate(
    input_variables=["input", "agent_scratchpad", "tools", "tool_names"],
    template="""
You are an inventory assistant
You have tools:
{tools}

Rules:
- You must NEVER include a Final Answer and an Action in the same response.
- If you have completed the task, first give the Final Answer and STOP.
- Prefer ONE SQL that joins products with inventory, aggregates quantity, and filters total < threshold.
- When writing SQL, write ONLY the SQL (no backticks/markdown/comments).
- Always ground your Final Answer in the actual tool Observation.
- If a tool fails, try a corrected attempt; do not conclude after an error.
- Keep the final answer concise and helpful.

Available tool names: {tool_names}

Format:
Thought: reasoning
Action: one of [{tool_names}]
Action Input: input for the action (SQL on one line, no fences)
Observation: (system will insert the tool result)
... (repeat Thought/Action/Action Input/Observation if needed)
Thought: I now know the final answer
Final Answer: concise result grounded in Observation


Example (for low stock):
Thought: I should run a single SQL that computes total quantities vs thresholds.
Action: Database Reader
Action Input: SELECT p.name, p.barcode, COALESCE(SUM(i.quantity),0) AS total_quantity, p.threshold
FROM products p LEFT JOIN inventory i ON i.barcode = p.barcode
GROUP BY p.name, p.barcode, p.threshold
ORDER BY p.name;

Observation: name|barcode|total_quantity|threshold
Widget A|12345|4|10
Cable|99999|0|5|8



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
    max_iterations=30,
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
