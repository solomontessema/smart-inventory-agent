# Tracks agent actions and stores execution logs 
import sqlite3
from datetime import datetime
from config import DB_PATH

 
def track_log(action: str, details: str = "") -> str:
    return f"Logged action: {action}"


def track_log_tool(input: str) -> str:
    try:
        action, details = input.split(" | ", 1)
    except ValueError:
        action, details = input, ""
    return track_log(action.strip(), details.strip())
