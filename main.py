from agents.inventory_agent import  inventory_agent

result = inventory_agent.invoke({"messages": [{"role": "user", 
                                               "content": """How many distinct products are there in inventory? 
                                               List their barcode and name. 
                                               Search online for bulk suppliers for those products and send me well formatted email. """} ]})

agent_answer = result["messages"][-1]
print(agent_answer.content)

