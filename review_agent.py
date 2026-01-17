from langchain_openai import ChatOpenAI
import os

api_key = os.getenv("DEEPSEEK_API_KEY", "sk-83241d57cc334cd19a4b817b9a68c511")
if not api_key:
    raise ValueError("DEEPSEEK_API_KEY is not set")

llm = ChatOpenAI(model="deepseek-chat", api_key=api_key, temperature=0, base_url="https://api.deepseek.com")

class ReviewAgent:
    def __init__(self):
        self.llm = llm