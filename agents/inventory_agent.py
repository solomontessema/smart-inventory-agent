from langchain.agents import Tool, AgentExecutor, create_react_agent
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from tools.web_search_tool import web_search_tool
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
    )
]


prompt_template = PromptTemplate(
    input_variables=["input", "tools", "tool_names"],
    template="""
You are a helpful assistant. You have access to the following tools:
{tools}

The user's query is: {input}

You must follow the ReAct format:
Thought: I need to determine which tool to use.
Action: [tool_name]
Action Input: [input to the tool]
Observation: [Tool result]
...
Thought: I have the final answer.
Final Answer: [The answer to the user]

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
        "input": user_input,
    })
    return result.get("output", "")

