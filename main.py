from agents.inventory_graph import run_inventory_graph


def main():
    print("🔄 Running Smart Inventory Agent (LangGraph version)...")
    result = run_inventory_graph()
    print(f"✅ Final Status: {result}")

if __name__ == "__main__":
    main()