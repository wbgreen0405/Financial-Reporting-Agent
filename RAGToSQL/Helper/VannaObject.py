import openai
from vanna.openai.openai_chat import OpenAI_Chat
from vanna.chromadb.chromadb_vector import ChromaDB_VectorStore

class MyVanna(ChromaDB_VectorStore, OpenAI_Chat):
    def __init__(self, config=None):
        ChromaDB_VectorStore.__init__(self, config=config)
        OpenAI_Chat.__init__(self, config=config)
        # Store your custom prompt text here—do NOT override the method name
        self._system_prompt_text = ""

    def set_system_message(self, prompt: str):
        # Save the text into a private var
        self._system_prompt_text = prompt

    def system_message(self, initial_prompt: str) -> dict:
        """
        Called internally by VannaBase.generate_sql().
        Must return a dict: {role:"system", content:"..."}.
        """
        text = self._system_prompt_text or initial_prompt
        return {"role": "system", "content": text}
