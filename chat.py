from agents.inventory_agent import run_inventory_agent

 
print("What can I help you today. (Type 'exit' to exit.)")
while True:
    user_input = input("You: ").strip()
    if user_input.lower() in {"exit", "quit"}:
        print("Inventory Agent: Bye!")
        break
    answer = run_inventory_agent(user_input)
    print(f"Inventory Agent: {answer}")
 