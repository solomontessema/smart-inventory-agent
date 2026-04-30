from mcp.server.fastmcp import FastMCP
import sqlite3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from datetime import datetime
from typing import Optional
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import (
    DB_PATH,
    AGENT_EMAIL_ADDRESS,
    AGENT_EMAIL_PASSWORD,
    RECIPIENT_EMAIL_ADDRESS,
    TAVILY_API_KEY
)
from langchain_tavily import TavilySearch

# ── serve over HTTP so both Claude and LangChain can connect ──
mcp = FastMCP("central-tools", host="0.0.0.0", port=8000)

# ── SQLite helper ─────────────────────────────────────────────
def get_connection():
    uri_path = f"file:///{DB_PATH}"
    return sqlite3.connect(uri_path, uri=True, check_same_thread=False)

# ── Tools ─────────────────────────────────────────────────────
@mcp.tool()
def query_database(sql: str) -> str:
    """Execute a SQL query against the SQLite database and return results."""
    if not sql.strip():
        return "Error: empty query."
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        cols = [d[0] for d in cur.description] if cur.description else []
        conn.close()

        if not cols:
            return "No result columns."

        header = "|".join(cols)
        if not rows:
            return header

        lines = [header]
        for r in rows:
            lines.append("|".join("" if v is None else str(v) for v in r))
        return "\n".join(lines)
    except Exception as e:
        return f"Error executing SQL: {e}"

@mcp.tool()
def get_schema() -> str:
    """Get a summary of all tables and columns in the database."""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cur.fetchall()]
        summary = []
        for table in tables:
            cur.execute(f"PRAGMA table_info({table});")
            cols = [row[1] for row in cur.fetchall()]
            summary.append(f"Table: {table} Columns: {cols}")
        conn.close()
        return "\n".join(summary)
    except Exception as e:
        return f"Error getting schema: {e}"

@mcp.tool()
def send_email(subject: str, body: str, to_address: Optional[str] = None) -> str:
    """Send an email with a subject and body."""
    try:
        recipient = to_address or RECIPIENT_EMAIL_ADDRESS
        msg = MIMEMultipart("alternative")
        msg["From"] = AGENT_EMAIL_ADDRESS
        msg["To"] = recipient
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))
        msg.attach(MIMEText(body, "html"))

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(AGENT_EMAIL_ADDRESS, AGENT_EMAIL_PASSWORD)
            server.send_message(msg)

        return "Email sent successfully."
    except Exception as e:
        return f"Failed to send email: {e}"

@mcp.tool()
def log_action(action: str, details: str = "") -> str:
    """Log an action with optional details to the database."""
    try:
        conn = get_connection()
        cur = conn.cursor()
        timestamp = datetime.now().isoformat()
        cur.execute(
            "INSERT INTO logs (timestamp, action, details) VALUES (?, ?, ?)",
            (timestamp, action, details)
        )
        conn.commit()
        conn.close()
        return f"Logged action: {action}"
    except Exception as e:
        return f"Failed to log: {e}"

@mcp.tool()
def web_search(query: str) -> str:
    """Search the web using Tavily and return formatted results."""
    try:
        search = TavilySearch(
            api_key=TAVILY_API_KEY,
            max_results=5,
            include_answer=True
        )
        results = search.invoke({"query": query})
        output = f"Search results for **{query}**:\n"
        for r in results["results"]:
            title = r.get("title", "No title")
            url = r.get("url", "")
            snippet = r.get("content", "")
            output += f"- [{title}]({url})\n  {snippet}\n\n"
        return output.strip()
    except Exception as e:
        return f"Search failed: {e}"

if __name__ == "__main__":
    mcp.run(transport="streamable-http")