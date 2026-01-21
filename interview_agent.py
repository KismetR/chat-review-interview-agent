import os
from typing import Optional, List, Union
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from file_handler import FileHandler

load_dotenv()
api_key = os.getenv("DEEPSEEK_API_KEY")
if not api_key:
    raise ValueError("DEEPSEEK_API_KEY 环境变量未设置，请在 .env 文件中配置")

BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")

class InterviewAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="deepseek-reasoner",
            api_key=api_key,
            temperature=0.7,
            base_url=BASE_URL,
        )
        self.file_handler = FileHandler(max_content_length=120000)
        self.template = ChatPromptTemplate.from_messages([
            ("system", """你是面试官，负责与用户进行面试。
            按照用户指定类型的面试官角色对用户进行面试
            {document_info}
            """),
            ("user", "{input}")
        ])
        self.parser = StrOutputParser()
        self.chain = self.template | self.llm | self.parser

    def invoke(self, message: str, file_paths: Optional[Union[str, List[str]]] = None) -> str:
        """
        """
        document_info = "无文档提供。"
        if file_paths:
            try:
                files_data = self.file_handler.load_files(file_paths)
                document_info = self.file_handler.format_for_prompt(files_data)
            except Exception as e:
                print(f"文件处理失败: {e}")
                document_info = f"文件处理失败: {e}"
        try:
            response = self.chain.invoke({"input": message, "document_info": document_info})
            return response
        except Exception as e:
            return f"处理失败: {e}"
    def stream(self, message: str, file_paths: Optional[Union[str, List[str]]] = None) -> str:
        """
        """
        document_info = "无文档提供。"
        if file_paths:
            try:
                files_data = self.file_handler.load_files(file_paths)
                document_info = self.file_handler.format_for_prompt(files_data)
                success_count = sum(1 for f in files_data if f["content"] is not None)
                total_count = len(files_data)
                if success_count > 0:
                    print(f"已加载 {success_count}/{total_count} 个文件")
                else:
                    print("所有文件加载失败")
            except Exception as e:
                print(f"文件处理失败: {e}")
                document_info = f"文件处理失败: {e}"
        try:
            for chunk in self.chain.stream({"input": message, "document_info": document_info}):
                yield chunk
        except Exception as e:
            yield f"处理失败: {e}"

if __name__ == "__main__":
    agent = InterviewAgent()
    for chunk in agent.stream("请根据材料对用户进行面试", file_paths="bagu.pdf"):
        print(chunk, end="", flush=True)
    print()