import streamlit as st
from agents.inventory_agent import run_inventory_agent

st.set_page_config(page_title="Inventory Agent", layout="centered")
st.title("Smart Inventory Agent")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if user_input := st.chat_input("Ask me about inventory, suppliers, or thresholds..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    answer = run_inventory_agent(user_input)
    st.session_state.messages.append({"role": "assistant", "content": answer})
    with st.chat_message("assistant"):
        st.markdown(answer)
