import os
from langchain_tavily import TavilySearch
from langchain.tools import tool
from config import TAVILY_API_KEY

# Initialize Tavily search tool
search_tool = TavilySearch(
    api_key=TAVILY_API_KEY,
    max_results=5,
    include_answer=True
)

@tool
def web_search_tool(query: str) -> str:
    """Perform a web search using Tavily and return formatted results."""
    results = search_tool.invoke({"query": query})
    output = f"Search results for **{query}**:\n"
    for result in results["results"]:
        title = result.get("title", "No title")
        url = result.get("url", "")
        snippet = result.get("content", "")
        output += f"- \\[{title}\\]({url})\n  {snippet}\n\n"

    return output.strip()

