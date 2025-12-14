from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from tools.web_search_tool import web_search_tool
from config import OPENAI_API_KEY 

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0
)


inventory_agent = create_agent(
    model=llm, 
    tools=[web_search_tool], 
    system_prompt="You are a helpful assistant."
    )

