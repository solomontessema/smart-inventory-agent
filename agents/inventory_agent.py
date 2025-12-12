from langchain.agents import create_agent
from langchain_core.tools import Tool
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain.agents.middleware import SummarizationMiddleware
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.messages import HumanMessage, SystemMessage
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

summarization_middleware = SummarizationMiddleware(
    model="gpt-4o-mini",
    trigger=('tokens', 1000),
    keep=('messages', 5),
)


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

chat_agent = create_agent(
    model=llm, 
    tools=tools, 
    system_prompt=prompt_template,
    middleware=[summarization_middleware],
    checkpointer=InMemorySaver(),
    )

 
def run_chat(user_input: str):
    config = {"configurable": {"thread_id": "1001"}}
    response = chat_agent.invoke(
        {"messages": [HumanMessage(content=user_input)]},
        config=config,
    )

    ai_response = response["messages"][-1].content
    return ai_response




