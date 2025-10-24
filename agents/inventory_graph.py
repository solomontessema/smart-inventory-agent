from typing import TypedDict, List, Optional
from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableLambda
from tools.database_reader import read_database_tool
from tools.web_searcher import web_search_tool
from tools.email_sender import send_email_tool
from tools.log_tracker import track_log_tool
from config import BOSS_EMAIL_ADDRESS
from langchain_community.chat_models import ChatOpenAI
from config import OPENAI_API_KEY

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# ---------------------------
# LLM
# ---------------------------
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    api_key=OPENAI_API_KEY
)



# ---------------------------
# Shared State Definition
# ---------------------------
class InventoryState(TypedDict):
    low_stock_items: Optional[str]
    supplier_links: Optional[str]
    email_body: Optional[str]
    final_status: Optional[str]

# ---------------------------
# Node: Check Inventory
# ---------------------------
def check_inventory_node(state: InventoryState) -> InventoryState:
    sql = """
    SELECT p.name, p.barcode, COALESCE(SUM(i.quantity),0) AS total_quantity, p.threshold
    FROM products p
    LEFT JOIN inventory i ON i.barcode = p.barcode
    GROUP BY p.name, p.barcode, p.threshold
    HAVING COALESCE(SUM(i.quantity),0) < p.threshold
    ORDER BY p.name;
    """
    result = read_database_tool(sql)
    return {**state, "low_stock_items": result}

# ---------------------------
# Node: Search Suppliers
# ---------------------------
def search_suppliers_node(state: InventoryState) -> InventoryState:
    if not state.get("low_stock_items"):
        return {**state, "supplier_links": "No low stock items found."}
    
    lines = state["low_stock_items"].split("\n")[1:]  # skip header
    queries = [line.split("|")[0].strip() for line in lines if line]
    results = [web_search_tool(q) for q in queries]
    return {**state, "supplier_links": "\n\n".join(results)}


# ---------------------------
# Node: Search Suppliers
# ---------------------------

def format_supplier_links_node(state: InventoryState) -> InventoryState:
    raw_links = state.get("supplier_links", "")
    prompt = f"Format the following supplier search results into clean HTML:\n\n{raw_links}"
    formatted = llm.invoke(prompt)
    return {**state, "supplier_links": formatted}

# ---------------------------
# Node: Compose Email
# ---------------------------
def compose_email_node(state: InventoryState) -> InventoryState:
    if not state.get("low_stock_items"):
        return {**state, "email_body": "No low stock items to report."}
    
    body = "<p><b>Low Stock Items:</b></p><ul>"
    for line in state["low_stock_items"].split("\n")[1:]:
        parts = line.split("|")
        if len(parts) >= 4:
            name, barcode, qty, threshold = parts
            body += f"<li>{name} ({barcode}): {qty} units, threshold {threshold}</li>"
    supplier_links = state.get("supplier_links", "")
    if hasattr(supplier_links, "content"):
        supplier_links = supplier_links.content
    body += "</ul><p><b>Supplier Links:</b></p><p>" + supplier_links + "</p>"
    return {**state, "email_body": body}

# ---------------------------
# Node: Send Email
# ---------------------------
def send_email_node(state: InventoryState) -> InventoryState:
    subject = "Inventory Alert: Low Stock Summary"
    body = state.get("email_body", "No content.")
    result = send_email_tool(f"{subject} || {body}")
    return {**state, "final_status": result}

# ---------------------------
# Node: Log Action
# ---------------------------
def log_action_node(state: InventoryState) -> InventoryState:
    summary = state.get("final_status", "No status.")
    track_log_tool(f"Inventory Run | {summary}")
    return state

# ---------------------------
# LangGraph DAG Definition
# ---------------------------
def run_inventory_graph():
    builder = StateGraph(InventoryState)
    builder.add_node("CheckInventory", RunnableLambda(check_inventory_node))
    builder.add_node("SearchSuppliers", RunnableLambda(search_suppliers_node))
    builder.add_node("FormatSupplierLinks", RunnableLambda(format_supplier_links_node))
    builder.add_node("ComposeEmail", RunnableLambda(compose_email_node))
    builder.add_node("SendEmail", RunnableLambda(send_email_node))
    builder.add_node("LogAction", RunnableLambda(log_action_node))
    builder.set_entry_point("CheckInventory")
    builder.add_edge("CheckInventory", "SearchSuppliers")
    builder.add_edge("SearchSuppliers", "FormatSupplierLinks")
    builder.add_edge("FormatSupplierLinks", "ComposeEmail")
    builder.add_edge("ComposeEmail", "SendEmail")
    builder.add_edge("SendEmail", "LogAction")
    builder.add_edge("LogAction", END)
    graph = builder.compile()
    result = graph.invoke({})
    return result.get("final_status", "Graph completed with no status.")
