import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))
import streamlit as st
from src.generate import generate_answer

st.set_page_config(page_title="RAG Chatbot", page_icon="🤖")
st.title("🤖 Local RAG Chatbot")
st.caption("Ask questions about your PDFs — powered by local Ollama + pgvector")

# Keep chat history across interactions
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display past messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input box at the bottom
if question := st.chat_input("Ask something about your PDFs..."):
    # Show user's message
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    # Generate and show bot's answer
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            answer = generate_answer(question)
        st.markdown(answer)
    st.session_state.messages.append({"role": "assistant", "content": answer})