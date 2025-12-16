from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from tools.web_search_tool import web_search_tool
from tools.database_reader import read_database_tool
from tools.email_sender import send_email_tool
from config import OPENAI_API_KEY 

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0
)


inventory_agent = create_agent(
    model=llm, 
    tools=[web_search_tool,read_database_tool,send_email_tool], 
    system_prompt="You are a helpful assistant to manage inventory and find bulk suppliers online for products in the database. when sending email, format it well with greetings and signature. Format it well as html",
    )

