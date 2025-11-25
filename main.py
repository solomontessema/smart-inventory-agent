from agents.inventory_agent import run_inventory_agent

run_inventory_agent(
    '''
    check our inventory, identify low stock items where sum(quantity) below threshold level, 
    search for suppliers for our low stock items if there is any lowstock item.
    '''
)
 

