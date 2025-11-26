from langchain.agents import Tool, AgentExecutor, create_react_agent
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from tools.web_search_tool import web_search_tool
from tools.database_reader import read_database_tool
from tools.email_sender import send_email_tool
from tools.log_tracker import track_log_tool
from config import OPENAI_API_KEY 
from langchain.memory import ConversationBufferMemory   

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    api_key=OPENAI_API_KEY
)

#------------------------------------
memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True,
    input_key="input"
)
#------------------------------------


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
You are a helpful assistant. Your name is Agent Smith. You have access to the following tools:
{tools}
To answer inventory questions use products and transactions tables. Join them if needed.
The user's query is: {input}

Conversation history:  # add this
{chat_history}

Use the Email Sender tool only when you are explicitly asked to send email:
- When you do so address the recipients as "Team"
- Format the body as professional HTML. Use clear title and heading. Include sentences, table of summary, and greetings

You must follow the ReAct format:
Thought: I need to determine which tool to use.
Action: [tool_name]
Action Input: [input to the tool]
Observation: [Tool result]
...
Thought: I have the final answer. Now I must log the final outcome of the task before responding.
Action: Log Tracker
Action Input: Final Task Status | Status: Completed. Details: [The final answer or result summary]
Observation: Log recorded successfully.
Final Answer: [The answer to the user]

Available tool names: {tool_names}

{agent_scratchpad}
"""
)

agent = create_react_agent(llm=llm, tools=tools, prompt=prompt_template)

inventory_agent = AgentExecutor(
    agent=agent,
    tools=tools,
    memory=memory,   # add this
    verbose=True, 
    handle_parsing_errors=True,
)


def run_inventory_agent(user_input: str) -> str:
    """Invokes the agent with a user query."""
    result = inventory_agent.invoke({
        "input": user_input 
    })
    return result.get("output", "")




