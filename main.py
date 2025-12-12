from agents.inventory_agent import run_chat

while True:
    user_question = input("Enter your message: ")
    if user_question.lower() == "exit":
        break
    response = run_chat(user_question)
    print(response)