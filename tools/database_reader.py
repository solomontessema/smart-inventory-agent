# tools/database_reader.py


def _exec_sql() -> str:
    return (
        "We have the following inventory\n"
        "Item Name|Barcode|Quantity|Threshold\n"
        "Coca Cola|2344330012|200|120\n"
        "Pepsi|450023144|60|110"
    )

def read_database_tool(input: str) -> str:
   return  _exec_sql()
    
