from typing import List, Tuple, Any
import sqlite3
from langchain.tools import tool
from config import DB_PATH

class SQLiteConnector:
    def __init__(self, db_path=DB_PATH):

        uri_path = f"file:///{db_path}"
        self.conn = sqlite3.connect(uri_path, uri=True, check_same_thread=False)
        self.cursor = self.conn.cursor()

    def list_tables(self):
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        return [row[0] for row in self.cursor.fetchall()]

    def describe_table(self, table_name):
        self.cursor.execute(f"PRAGMA table_info({table_name});")
        return self.cursor.fetchall()

    def get_schema_summary(self):
        summary = []
        for table in self.list_tables():
            cols = self.describe_table(table)
            formatted = f"Table: {table} Columns: {[col[1] for col in cols]}"
            summary.append(formatted)
        return "\n".join(summary)

connector = SQLiteConnector()

def _exec_sql(sql: str) -> Tuple[List[str], List[Tuple[Any, ...]]]:
    cur = connector.conn.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    cols = [d[0] for d in cur.description] if cur.description else []
    return cols, rows

def _format_table(cols: List[str], rows: List[Tuple[Any, ...]]) -> str:
    if not cols:
        return "No result columns."
    header = "|".join(cols)
    if not rows:
        return header  # header only when no matches
    lines = [header]
    for r in rows:
        lines.append("|".join("" if v is None else str(v) for v in r))
    return "\n".join(lines)

@tool
def read_database_tool(sql: str) -> str:
    """Execute a SQL query against the SQLite database and return formatted results."""
    if not isinstance(sql, str) or not sql.strip():
        return "Error executing SQL: empty query."

    try:
        cols, rows = _exec_sql(sql)
        return _format_table(cols, rows)
    except Exception as e:
        return f"Error executing SQL: {e}"