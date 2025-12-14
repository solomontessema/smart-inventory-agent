from agents.inventory_agent import  inventory_agent


result = inventory_agent.invoke({"messages": [{"role": "user", "content": "Find suppliers for coca cola in bulk."}]})

agent_answer = result["messages"][-1]
print(agent_answer.content)

