from agents.inventory_agent import run_inventory_agent

answer = run_inventory_agent(
    '''
    check our inventory and tell me what we have and the threshold.
    search the web and find potential suppliers for inventory.
    '''
    )

print(answer)