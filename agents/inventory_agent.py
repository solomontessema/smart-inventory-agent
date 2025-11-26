from langchain.agents import Tool, AgentExecutor, create_react_agent
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from tools.web_search_tool import web_search_tool
from tools.database_reader import read_database_tool
from tools.email_sender import send_email_tool
from tools.log_tracker import track_log_tool
from config import OPENAI_API_KEY 

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    api_key=OPENAI_API_KEY
)


tools = [
    Tool(
        name="Supplier Finder",
        func=web_search_tool,
        description="Search suppliers by product name, barcode, or category."
    ),
    Tool(
        name="Database Reader",
        func=read_database_tool,
        description="Execute a SQL query and return raw tabular results. Use for inventory & thresholds."
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


prompt_template = PromptTemplate(
    input_variables=["input", "tools", "tool_names"],
    template="""
You are a helpful assistant. You have access to the following tools:
{tools}
To answer inventory questions use products and inventory tables. Join them if needed.
The user's query is: {input}

You must follow the ReAct format:
Thought: I need to determine which tool to use.
Action: [tool_name]
Action Input: [input to the tool]
Observation: [Tool result]
...
Thought: I have the final answer.
Final Answer: [The answer to the user]

When using the Email Sender tool:
- Your name is Agent Smith. Address the recipients as "Team"
- Format the body as professional HTML. Use clear title and heading. Include sentences, table of summary, and greetings

After any task:
- Use the "Log Tracker" tool to log the task and the action commited.

Example (for low stock):
Thought: I should run a single SQL that computes total quantities vs thresholds.
Action: Database Reader
Action Input: SELECT p.name, p.barcode, COALESCE(SUM(i.quantity),0) AS total_quantity, p.threshold
FROM products p LEFT JOIN inventory i ON i.barcode = p.barcode
GROUP BY p.name, p.barcode, p.threshold
HAVING COALESCE(SUM(i.quantity),0) < p.threshold
ORDER BY p.name;

Observation: name|barcode|total_quantity|threshold
Widget A|12345|4|10
Cable|99999|0|5

Thought: I have the products below threshold.
Final Answer: Low stock:
- Widget A (12345): total_quantity=4, threshold=10
- Cable (99999): total_quantity=0, threshold=5

Thought: I should log this action.
Action: Log Tracker
Action Input: Task Completed | Identified low stock items and emailed summary to boss.

Available tool names: {tool_names}

{agent_scratchpad}
"""
)

agent = create_react_agent(llm=llm, tools=tools, prompt=prompt_template)

inventory_agent = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True, 
    handle_parsing_errors=True,
)


def run_inventory_agent(user_input: str) -> str:
    """Invokes the agent with a user query."""
    result = inventory_agent.invoke({
        "input": user_input 
    })
    return result.get("output", "")

