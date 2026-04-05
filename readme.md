# Analytics Assistant

A conversational data analytics agent that lets users ask plain-English questions about transaction data and receive Python-generated analysis and visualizations.

---

## What It Does

1. **Ingest data** — Load an Excel or CSV file of transaction data at startup. Parse it with pandas and store basic metadata (column names, dtypes, sample rows, row count).
2. **Build a schema context** — Summarize the dataset structure into a compact text block that is injected into every LLM prompt, acting as the agent's "database awareness."
3. **Understand user intent** — Accept a natural-language question (e.g., "What are the top 5 categories by total spend?").
4. **Generate pandas code** — The LLM produces a Python code snippet that answers the question using the loaded DataFrame.
5. **Execute and return results** — Run the generated code in a sandboxed Python environment, capture the output (text table, scalar, or chart), and return it to the user.
6. **Iterate** — Support follow-up questions within the same session, with conversation history kept in the prompt context.

---

## Architecture

```
User question
      │
      ▼
┌─────────────────────────┐
│  Context Builder        │  ← schema summary + conversation history
│  (RAG-lite injection)   │
└──────────┬──────────────┘
           │  enriched prompt
           ▼
┌─────────────────────────┐
│  LLM (Claude API)       │  ← generates pandas code
└──────────┬──────────────┘
           │  code string
           ▼
┌─────────────────────────┐
│  Code Executor          │  ← runs code, captures stdout / matplotlib fig
└──────────┬──────────────┘
           │  result
           ▼
      User output
```

The schema summary replaces a traditional vector database. Because transaction datasets are typically narrow (10–30 columns), the full column list, dtypes, and a few sample rows fit comfortably within a single LLM context window. No embedding or retrieval step is needed.

---

## Tech Stack

| Layer | Tool |
|---|---|
| LLM | Claude API (`claude-sonnet-4-6`) via `anthropic` Python SDK |
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
│   ├── llm_client.py       # wraps Claude API calls, manages message history
│   └── executor.py         # safely executes generated code, captures output
├── requirements.txt
└── readme.md
```

---

## Prompt Design

Each LLM call receives a system prompt containing:

1. **Role instruction** — "You are a data analyst. Write pandas code to answer the user's question."
2. **Schema block** — column names, dtypes, shape, and 3 sample rows from the loaded file.
3. **Output contract** — instructions to always assign the final result to a variable named `result` and use `print(result)` for tabular output, or `plt.savefig(buf)` for charts.
4. **Conversation history** — prior turns so follow-up questions resolve correctly.

---

## Key Constraints and Guardrails

- Generated code runs in an isolated scope (`exec(code, {"df": df, ...})`); no file system or network access is granted.
- If code execution raises an exception, the error is fed back to the LLM for a single retry with the traceback included.
- The DataFrame passed to `exec` is a read-only copy to prevent accidental mutation between turns.

---

## Getting Started (Planned)

```bash
pip install -r requirements.txt
streamlit run app.py
```

Upload a CSV or Excel file via the sidebar, then type a question in the chat input.
