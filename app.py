import os

import pandas as pd
import streamlit as st

from agent.context_builder import build_schema_summary
from agent.executor import execute_code
from agent.llm_client import LLMClient

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="Analytics Assistant", layout="wide")
st.title("Analytics Assistant")

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Setup")

    uploaded_file = st.file_uploader(
        "Upload CSV or Excel", type=["csv", "xlsx", "xls"]
    )

    # API key: env var takes priority; sidebar field as fallback
    env_key = os.environ.get("GROQ_API_KEY", "")
    sidebar_key = st.text_input(
        "Groq API Key",
        type="password",
        value=env_key,
        placeholder="gsk_... (or set GROQ_API_KEY env var)",
    )
    active_key = sidebar_key or env_key
    if active_key:
        os.environ["GROQ_API_KEY"] = active_key

    if st.button("Clear conversation"):
        if "llm_client" in st.session_state:
            st.session_state.llm_client.reset()
        st.session_state.chat = []
        st.rerun()

# ── Load data ─────────────────────────────────────────────────────────────────
if uploaded_file:
    file_key = uploaded_file.name + str(uploaded_file.size)

    if st.session_state.get("file_key") != file_key:
        with st.spinner("Loading data…"):
            if uploaded_file.name.lower().endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)

        st.session_state.df = df
        st.session_state.file_key = file_key
        st.session_state.schema = build_schema_summary(df)
        st.session_state.llm_client = LLMClient(schema=st.session_state.schema)
        st.session_state.chat = []

    df: pd.DataFrame = st.session_state.df

    with st.sidebar:
        st.markdown(f"**{df.shape[0]:,} rows × {df.shape[1]} columns**")
        with st.expander("Schema"):
            st.text(st.session_state.schema)

    # ── Render chat history ───────────────────────────────────────────────────
    for entry in st.session_state.get("chat", []):
        with st.chat_message(entry["role"]):
            kind = entry["kind"]
            if kind == "text":
                st.markdown(entry["content"])
            elif kind == "code":
                st.code(entry["content"], language="python")
            elif kind == "figure":
                st.pyplot(entry["content"])
            elif kind == "error":
                st.error(entry["content"])

    # ── Chat input ────────────────────────────────────────────────────────────
    question = st.chat_input("Ask a question about your data…")
    if question:
        if not active_key:
            st.error("Add your Groq API key in the sidebar first.")
            st.stop()

        # User bubble
        with st.chat_message("user"):
            st.markdown(question)
        st.session_state.chat.append({"role": "user", "kind": "text", "content": question})

        # Assistant response
        with st.chat_message("assistant"):
            # 1. Get response from LLM (code or plain text)
            with st.spinner("Thinking…"):
                response = st.session_state.llm_client.get_response(question)

            if response["type"] == "text":
                # Conversational reply — just display it, no execution
                st.markdown(response["content"])
                st.session_state.chat.append(
                    {"role": "assistant", "kind": "text", "content": response["content"]}
                )

            else:
                # Analytical reply — show code, execute, display output
                code = response["content"]
                st.code(code, language="python")
                st.session_state.chat.append({"role": "assistant", "kind": "code", "content": code})

                # 2. Execute
                with st.spinner("Running…"):
                    result = execute_code(code, df)

                # 3. Retry once on failure
                if not result["success"]:
                    with st.spinner("Fixing error…"):
                        code = st.session_state.llm_client.retry_with_error(result["traceback"])
                    st.code(code, language="python")
                    st.session_state.chat.append(
                        {"role": "assistant", "kind": "code", "content": code}
                    )
                    with st.spinner("Re-running…"):
                        result = execute_code(code, df)

                # 4. Display output
                if result["success"]:
                    if result["text"]:
                        st.text(result["text"])
                        st.session_state.chat.append(
                            {"role": "assistant", "kind": "text", "content": result["text"]}
                        )
                    if result["figure"]:
                        st.pyplot(result["figure"])
                        st.session_state.chat.append(
                            {"role": "assistant", "kind": "figure", "content": result["figure"]}
                        )
                else:
                    msg = f"Failed after retry:\n\n```\n{result['traceback']}\n```"
                    st.error(msg)
                    st.session_state.chat.append(
                        {"role": "assistant", "kind": "error", "content": msg}
                    )

else:
    st.info("Upload a CSV or Excel file in the sidebar to get started.")
