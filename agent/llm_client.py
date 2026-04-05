'''
This file manages all communication with the LLM api
'''

import re
from groq import Groq

SYSTEM_PROMPT_TEMPLATE = """You are a data analyst assistant. Your job is to write Python (pandas) \
code to answer the user's questions about a transaction dataset.

DATASET SCHEMA:
{schema}

RULES:
1. The DataFrame is already loaded as `df`. Do NOT load any files or re-import libraries.
2. Available names in scope: `pd` (pandas), `plt` (matplotlib.pyplot), `sns` (seaborn).
3. For tabular or scalar output, assign the final answer to a variable named `result` \
and call `print(result)`.
4. For visualisations, create a matplotlib/seaborn figure with a descriptive title. \
Do NOT call `plt.show()` or `plt.savefig()`.
5. You may do both: print a summary AND produce a chart in the same code block.
6. Respond with ONLY a ```python ... ``` code block — no explanation text outside it.
7. Keep code concise and efficient. Prefer vectorised pandas operations over loops."""


class LLMClient:
    def __init__(self, schema: str, model: str = "llama-3.3-70b-versatile"):
        self.model = model
        self.system_prompt = SYSTEM_PROMPT_TEMPLATE.format(schema=schema)
        #when the client is created, it fills in the {schema} placeholder with the actual output from context_builder.py. 
        #self.history is an empty list that will accumulate the conversation turns as {"role": ..., "content":...} dicts. 
        self.history: list[dict] = []

    def get_code(self, user_question: str) -> str:
        self.history.append({"role": "user", "content": user_question}) #appends the user question to history
        raw = self._call_api() #calls the API with the full history
        self.history.append({"role": "assistant", "content": raw}) #appends the LLM's raw response to history
        return self._extract_code(raw) #extracts and returns JUST THE CODE from the response

    def retry_with_error(self, traceback_str: str) -> str: #only a single retry
        error_msg = (
            "The code raised an exception. Fix it and return only the corrected "
            f"```python ... ``` block.\n\nTraceback:\n{traceback_str}"
        ) #the LLM sees its own mistaken code and could try to fix it
        self.history.append({"role": "user", "content": error_msg})
        raw = self._call_api()
        self.history.append({"role": "assistant", "content": raw})
        return self._extract_code(raw)

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
    def _extract_code(text: str) -> str:
        match = re.search(r"```python\s*(.*?)```", text, re.DOTALL)
        if match:
            return match.group(1).strip()
        # Fallback: strip surrounding whitespace and return as-is
        return text.strip()
