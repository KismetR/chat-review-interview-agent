import os
from typing import Optional, List, Union
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# 加载环境变量
load_dotenv()

api_key = os.getenv("DEEPSEEK_API_KEY")
if not api_key:
    raise ValueError("DEEPSEEK_API_KEY 环境变量未设置，请在 .env 文件中配置")

BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")

class ChatAgent:
    """日常聊天 Agent"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model="deepseek-chat",
            api_key=api_key,
            temperature=0.7,  # 聊天可以更随机一些
            base_url=BASE_URL,
            streaming=True
        )
        self.template = ChatPromptTemplate.from_messages([
            ("system", """你是一位善于闲聊的AI助手，负责与用户进行愉快的对话。
            保持友好、幽默、有趣的风格。
            """),
            ("user", "{input}")  
        ])
        self.parser = StrOutputParser()
        self.chain = self.template | self.llm | self.parser

    def invoke(self, message: str, file_paths: Optional[Union[str, List[str]]] = None) -> str:
        """
        处理用户输入
        
        Args:
            message: 用户的消息
            file_paths: 文件路径（聊天一般不需要，保留接口统一）
            
        Returns:
            str: Agent 的回复
        """
        # 聊天 agent 通常不处理文件，但保留参数以保持接口统一
        if file_paths:
            print("⚠️ 聊天模式暂不支持文件处理")
        
        try:
            return self.chain.invoke({"input": message})
        except Exception as e:
            return f"聊天失败: {e}"
    def stream(self, message: str) -> str:
        """
        流式处理用户输入
        """
        try:
            for chunk in self.chain.stream({"input": message}):
                yield chunk
        except Exception as e:
            yield f"处理失败: {e}"