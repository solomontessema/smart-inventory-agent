import streamlit as st
from agents.inventory_agent import inventory_agent

st.set_page_config(page_title="Chat with Inventory Agent", layout="centered")
st.title("📦 Chat with Inventory Agent")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User input
user_input = st.chat_input("Ask the inventory agent...")

if user_input:
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Invoke the agent
    result = inventory_agent.invoke({"messages": st.session_state.messages})
    agent_msg = result["messages"][-1]      
    agent_text = agent_msg.content          

    st.session_state.messages.append({"role": "assistant", "content": agent_text})
    with st.chat_message("assistant"):
        st.markdown(agent_text)
