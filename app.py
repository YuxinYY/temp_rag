import os

import pandas as pd
import streamlit as st

from agent.context_builder import build_schema_summary
from agent.executor import execute_code
from agent.llm_client import LLMClient
from agent.rag import build_vector_store, retrieve

# ── Page config (UI set up) ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="Analytics Assistant", layout="wide")
st.title("Analytics Assistant")

# ── Build RAG vector store once per session ───────────────────────────────────
# Embeddings are persisted to disk so re-runs don't re-embed the knowledge base
KNOWLEDGE_DIR = os.path.join(os.path.dirname(__file__), "knowledge")
PERSIST_DIR = os.path.join(os.path.dirname(__file__), ".chromadb")

if "rag_collection" not in st.session_state:
    with st.spinner("Loading knowledge base…"):
        st.session_state.rag_collection = build_vector_store(KNOWLEDGE_DIR, PERSIST_DIR)

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

    if st.button("Clear conversation"): #clear conversation button
        if "llm_client" in st.session_state:
            st.session_state.llm_client.reset()
        st.session_state.chat = []
        st.rerun()

# ── Load data ─────────────────────────────────────────────────────────────────
if uploaded_file:
    file_key = uploaded_file.name + str(uploaded_file.size) #file key is a combination of filename + filesize

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
    # every mesasge in st.session_state.chat is a dict with role, kind, and content. EACH KIND gets a different display treatment.
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
        if not active_key: #reminding the user to put in an API key for the LLM
            st.error("Add your Groq API key in the sidebar first.")
            st.stop()

        # User bubble
        with st.chat_message("user"):
            st.markdown(question)
        st.session_state.chat.append({"role": "user", "kind": "text", "content": question})

        # Assistant response
        with st.chat_message("assistant"):
            # 1. Retrieve relevant knowledge chunks for this question
            knowledge = retrieve(st.session_state.rag_collection, question)
            st.sidebar.text_area("Retrieved context", knowledge, height=200)

            # 2. Get response from LLM (code or plain text), with knowledge injected
            with st.spinner("Thinking…"):
                response = st.session_state.llm_client.get_response(question, knowledge=knowledge)

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

                    # 5. Second LLM call: interpret the result in plain English for stakeholders
                    if result["text"] or result["figure"]:
                        with st.spinner("Interpreting…"):
                            interpretation = st.session_state.llm_client.interpret_result(
                                question, result["text"]
                            )
                        st.markdown(interpretation)
                        st.session_state.chat.append(
                            {"role": "assistant", "kind": "text", "content": interpretation}
                        )
                else:
                    msg = f"Failed after retry:\n\n```\n{result['traceback']}\n```"
                    st.error(msg)
                    st.session_state.chat.append(
                        {"role": "assistant", "kind": "error", "content": msg}
                    )

else:
    st.info("Upload a CSV or Excel file in the sidebar to get started.")
