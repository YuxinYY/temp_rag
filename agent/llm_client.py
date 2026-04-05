'''
This file manages all communication with the LLM api
'''

import re
from groq import Groq

SYSTEM_PROMPT_TEMPLATE = """You are a data analyst assistant helping users explore a transaction dataset.

DATASET SCHEMA:
{schema}

Decide how to respond based on the nature of the question:

CONVERSATIONAL questions (e.g. "what columns are there?", "tell me about the dataset", \
"what does X column mean?") → reply in plain text. No code block.

ANALYTICAL questions that require computation (e.g. "what are the top 5 territories by sales?", \
"show me a trend chart") → respond with ONLY a ```python ... ``` code block following these rules:
1. The DataFrame is already loaded as `df`. Do NOT load any files or re-import libraries.
2. Available names in scope: `pd` (pandas), `plt` (matplotlib.pyplot), `sns` (seaborn).
3. For tabular or scalar output, assign the final answer to a variable named `result` \
and call `print(result)`.
4. For visualisations, create a matplotlib/seaborn figure with a descriptive title. \
Do NOT call `plt.show()` or `plt.savefig()`.
5. You may do both: print a summary AND produce a chart in the same code block.
6. Keep code concise and efficient. Prefer vectorised pandas operations over loops."""


class LLMClient:
    def __init__(self, schema: str, model: str = "llama-3.3-70b-versatile"):
        self.model = model
        self.system_prompt = SYSTEM_PROMPT_TEMPLATE.format(schema=schema)
        #when the client is created, it fills in the {schema} placeholder with the actual output from context_builder.py. 
        #self.history is an empty list that will accumulate the conversation turns as {"role": ..., "content":...} dicts. 
        self.history: list[dict] = []

    def get_response(self, user_question: str) -> dict:
        # Returns {"type": "code", "content": <code string>}
        #      or {"type": "text", "content": <plain text reply>}
        self.history.append({"role": "user", "content": user_question}) #appends the user question to history
        raw = self._call_api() #calls the API with the full history
        self.history.append({"role": "assistant", "content": raw}) #appends the LLM's raw response to history
        code = self._extract_code(raw) #returns the code block if present, else None
        if code is not None:
            return {"type": "code", "content": code}
        return {"type": "text", "content": raw.strip()}

    def retry_with_error(self, traceback_str: str) -> str: #only a single retry
        error_msg = (
            "The code raised an exception. Fix it and return only the corrected "
            f"```python ... ``` block.\n\nTraceback:\n{traceback_str}"
        ) #the LLM sees its own mistaken code and could try to fix it
        self.history.append({"role": "user", "content": error_msg})
        raw = self._call_api()
        self.history.append({"role": "assistant", "content": raw})
        return self._extract_code(raw)

    def interpret_result(self, question: str, execution_output: str) -> str:
        # Second LLM call: takes the raw execution output and writes a short
        # plain-English interpretation for non-technical stakeholders.
        prompt = (
            f"The user asked: {question}\n\n"
            f"The analysis produced this output:\n{execution_output}\n\n"
            "Write 2-4 sentences interpreting the key findings in plain English "
            "for a non-technical stakeholder. Be concise and highlight what matters most. "
            "Do not repeat the raw numbers verbatim — summarise and give context."
        )
        client = Groq()
        response = client.chat.completions.create(
            model=self.model,
            max_tokens=512,
            messages=[
                {"role": "system", "content": "You are a data analyst who explains findings clearly to non-technical stakeholders."},
                {"role": "user", "content": prompt},
            ],
        )
        return response.choices[0].message.content.strip()

    def reset(self):
        self.history = []

    # ------------------------------------------------------------------
    def _call_api(self) -> str:
        # Instantiate fresh each call so it picks up the API key
        # from the environment even if it was set after __init__.
        client = Groq() #Groq uses OpenAI-compatible API format.
        response = client.chat.completions.create(
            model=self.model,
            max_tokens=2048,
            messages=[{"role": "system", "content": self.system_prompt}] + self.history,
        )
        return response.choices[0].message.content

    @staticmethod
    def _extract_code(text: str) -> str | None:
        match = re.search(r"```python\s*(.*?)```", text, re.DOTALL)
        if match:
            return match.group(1).strip()
        # No code block found — treat as a conversational text response
        return None
