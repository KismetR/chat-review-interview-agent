import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

api_key = os.getenv("DEEPSEEK_API_KEY", "sk-83241d57cc334cd19a4b817b9a68c511")
if not api_key:
    raise ValueError("DEEPSEEK_API_KEY is not set")

llm = ChatOpenAI(model="deepseek-chat", api_key=api_key, temperature=0.2, base_url="https://api.deepseek.com")

class ChatAgent:
    def __init__(self):
        self.llm = llm
        self.template = ChatPromptTemplate.from_messages([
            ("system", """你是一位善于闲聊的AI助手，负责与用户进行聊天。
            """),
            ("user", "{input}")  
        ])
        self.parser = StrOutputParser()
        self.chain = self.template | self.llm | self.parser

    def invoke(self, input: str) -> str:
        return self.chain.invoke({"input": input})