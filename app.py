# app.py

import streamlit as st
from pipeline import run_pipeline

# ── Page Config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Text-to-SQL AI",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖 Text-to-SQL AI Assistant")
st.caption("Ask questions about employees in plain English — powered by Gemini + Snowflake")

# ── Session State (persists across interactions) ─────────────────────────────
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []

if "messages" not in st.session_state:
    st.session_state.messages = []  # Chat display history

# ── Render Past Messages ─────────────────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

        # Show SQL expander if present
        if "sql" in msg:
            with st.expander("🔍 View SQL Query"):
                st.code(msg["sql"], language="sql")

        # Show data table if present
        if "rows" in msg and msg["rows"]:
            with st.expander("📊 View Raw Results"):
                st.dataframe(
                    [dict(zip(msg["columns"], row)) for row in msg["rows"]]
                )

# ── Chat Input ───────────────────────────────────────────────────────────────
if user_input := st.chat_input("e.g. Who are the top 3 highest paid employees?"):

    # Show user message
    with st.chat_message("user"):
        st.markdown(user_input)

    st.session_state.messages.append({"role": "user", "content": user_input})

    # Run pipeline
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            result = run_pipeline(user_input, st.session_state.conversation_history)

        # Show answer
        st.markdown(result["answer"])

        # Show SQL in expander
        if result["sql"] and result["sql"] != "INVALID":
            with st.expander("🔍 View SQL Query"):
                st.code(result["sql"], language="sql")

        # Show table in expander
        if result["rows"] and result["columns"]:
            with st.expander("📊 View Raw Results"):
                st.dataframe(
                    [dict(zip(result["columns"], row)) for row in result["rows"]]
                )

    # Save to display history
    st.session_state.messages.append({
        "role":    "assistant",
        "content": result["answer"],
        "sql":     result.get("sql"),
        "columns": result.get("columns"),
        "rows":    result.get("rows")
    })

    # Save to conversation history for follow-up support
    if result["status"] == "success":
        st.session_state.conversation_history.append({
            "question": user_input,
            "sql":      result["sql"],
            "answer":   result["answer"]
        })