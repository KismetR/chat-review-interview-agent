import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# 加载环境变量
load_dotenv()

api_key = os.getenv("DEEPSEEK_API_KEY")
if not api_key:
    raise ValueError("DEEPSEEK_API_KEY 环境变量未设置，请在 .env 文件中配置")

llm = ChatOpenAI(model="deepseek-chat", api_key=api_key, temperature=0, base_url="https://api.deepseek.com")

class ReviewAgent:
    def __init__(self):
        self.llm = llm