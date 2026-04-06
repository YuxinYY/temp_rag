# Analytics Assistant

A conversational data analytics agent that lets users ask plain-English questions about transaction data and receive Python-generated analysis and visualizations.

---

## What It Does

1. **Ingest data** — Load an Excel or CSV file of transaction data at startup. Parse it with pandas and store basic metadata (column names, dtypes, sample rows, row count).
2. **Build a schema context** — Summarize the dataset structure into a compact text block that is injected into every LLM prompt, acting as the agent's "database awareness."
3. **Retrieve relevant knowledge** — The question is embedded and matched against a vector store of company knowledge documents (metrics definitions, product hierarchy, channel strategy, etc.). The top-5 most relevant chunks are retrieved and injected into the prompt.
4. **Understand user intent** — Accept a natural-language question (e.g., "What are the top 5 categories by total spend?" or "Tell me about this dataset.").
5. **Decide response type** — The LLM decides whether to reply in plain text (conversational questions) or generate a Python code snippet (analytical questions requiring computation).
6. **Execute and return results** — If code was generated, run it in a sandboxed Python environment, capture the output (text table, scalar, or chart), and return it to the user. Conversational replies are displayed directly.
7. **Interpret the results** — A second LLM call takes the raw execution output and writes a 2–4 sentence plain-English interpretation for non-technical stakeholders.
8. **Iterate** — Support follow-up questions within the same session, with conversation history kept in the prompt context.

---

## Architecture

```
User question
      │
      ├──────────────────────────────┐
      ▼                              ▼
┌─────────────────────────┐  ┌──────────────────────────┐
│  Context Builder        │  │  RAG Retriever           │
│  (schema summary)       │  │  (sentence-transformers  │
└──────────┬──────────────┘  │   + ChromaDB)            │
           │                 └──────────┬───────────────┘
           │                            │ top-5 knowledge chunks
           └──────────┬─────────────────┘
                      │  schema + knowledge + history
                      ▼
           ┌─────────────────────────┐
           │  LLM (Groq API)         │  ← decides: code or plain text?
           └──────────┬──────────────┘
                      │
                ┌─────┴──────┐
                │            │
             code          text
                │            │
                ▼            ▼
          ┌─────────┐  displayed
          │ Executor│  directly
          │ exec()  │
          └────┬────┘
               │  raw output (text + chart)
               ▼
    ┌─────────────────────────┐
    │  LLM (interpretation)   │  ← second Groq call, plain-English summary
    └──────────┬──────────────┘
               │
          User output
```

The dataset schema is always injected in full (typically fits within a few hundred tokens). Company knowledge documents are retrieved selectively via RAG — only the top-5 most relevant chunks per query are included, keeping the prompt focused as the knowledge base scales.

---

## Tech Stack

| Layer | Tool |
|---|---|
| LLM | Groq API (`llama-3.3-70b-versatile`) via `groq` Python SDK |
| Embeddings | `sentence-transformers` (`all-MiniLM-L6-v2`) — runs locally, no API key |
| Vector store | `ChromaDB` — persisted to disk, no re-embedding on restart |
| Data I/O | `pandas` — reads `.csv` and `.xlsx` via `read_csv` / `read_excel` |
| Code execution | Python `exec()` in a restricted local scope; `io.StringIO` to capture stdout |
| Visualization | `matplotlib` / `seaborn` — figures saved to a buffer and displayed inline |
| UI | Streamlit (simple chat interface with file uploader) |
| Environment | Python 3.11+, managed with `uv` or `pip` + `requirements.txt` |

---

## Supported Analysis Tasks

- Aggregations: sum, mean, count, min/max by one or more grouping columns
- Time-series trends: resample by day/week/month, rolling averages
- Filtering and segmentation: top-N, bottom-N, condition-based subsets
- Distribution summaries: value counts, histograms, box plots
- Correlation: heatmaps, scatter plots between numeric columns
- Anomaly spotting: outliers via IQR or z-score

---

## Project Structure

```
analytics-assistant/
├── app.py                  # Streamlit entry point
├── agent/
│   ├── context_builder.py  # builds schema summary string from DataFrame
│   ├── llm_client.py       # wraps Groq API calls, manages message history
│   ├── executor.py         # safely executes generated code, captures output
│   └── rag.py              # chunks, embeds, and retrieves knowledge documents
├── knowledge/              # .md files (metrics, product hierarchy, etc.)
├── .chromadb/              # persisted ChromaDB vector store (auto-generated, not committed)
├── requirements.txt
└── readme.md
```

---

## Prompt Design

There are two distinct LLM calls per analytical question:

**Call 1 — Code generation** (`get_response()` in `llm_client.py`):
1. **Role instruction** — "You are a data analyst assistant helping users explore a transaction dataset."
2. **Schema block** — column names, dtypes, shape, and 3 sample rows from the loaded file.
3. **Knowledge context** — top-5 chunks retrieved from the RAG vector store for the current query.
4. **Response type guidance** — reply in plain text for conversational questions, or a `python` code block for analytical ones.
5. **Code contract** (when generating code) — assign the final result to `result` and call `print(result)` for tabular output; create a matplotlib/seaborn figure for charts without calling `plt.show()`.
6. **Conversation history** — prior turns so follow-up questions resolve correctly.

**Call 2 — Interpretation** (`interpret_result()` in `llm_client.py`):
- Triggered only after successful code execution.
- Receives the original question and the raw execution output.
- Returns 2–4 sentences summarising key findings in plain English for non-technical stakeholders.
- No conversation history — stateless, focused solely on the current result.

---

## Key Constraints and Guardrails

- Generated code runs in an isolated scope (`exec(code, {"df": df, ...})`); no file system or network access is granted.
- If code execution raises an exception, the error is fed back to the LLM for a single retry with the traceback included.
- The DataFrame passed to `exec` is a read-only copy to prevent accidental mutation between turns.

---

## Getting Started

```bash
pip install -r requirements.txt
streamlit run app.py
```

Upload a CSV or Excel file via the sidebar, put YOUR OWN Groq API key into the sidebar, and then type a question in the chat input.




<!-- ## Other: the agent doesn't have function calling or MCP
Function calling means you define tools with a schema (e.g. get_top_n_by_column(column, n)) and the LLM decides when to call them, passing structured arguments. Your project doesn't do this — the LLM just writes free-form Python code as text, and you run it with exec(). It's a "code generation" pattern, not tool/function calling.

MCP (Model Context Protocol) is a standard for connecting LLMs to external data sources or tools via a server. Your project has no MCP server or client — the dataset is loaded directly into memory in app.py and passed to exec() as a local variable.

What you have is simpler than both: the schema is injected into the prompt as plain text, the LLM writes pandas code, and you execute it locally. This works well for your use case and is easier to debug than function calling would be.

If you wanted to evolve toward function calling, you'd define discrete tools like aggregate(group_by, metric, agg_fn) and plot_bar(x, y) — the LLM would pick and parameterize them instead of writing arbitrary code. The tradeoff is less flexibility but more predictable, safer execution. -->

