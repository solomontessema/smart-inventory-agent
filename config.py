import os
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TAVILY_API_KEY=os.getenv("TAVILY_API_KEY") 
BOSS_EMAIL_ADDRESS = os.getenv("BOSS_EMAIL_ADDRESS")
AGENT_EMAIL_ADDRESS = os.getenv("AGENT_EMAIL_ADDRESS")
AGENT_EMAIL_PASSWORD = os.getenv("AGENT_EMAIL_PASSWORD")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database", "data.db")