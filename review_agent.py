import os
from typing import Optional, List, Union
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from file_handler import FileHandler

# 加载环境变量
load_dotenv()
api_key = os.getenv("DEEPSEEK_API_KEY")
if not api_key:
    raise ValueError("DEEPSEEK_API_KEY 环境变量未设置，请在 .env 文件中配置")

BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")

class ReviewAgent:
    """知识复习 Agent"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model="deepseek-reasoner", 
            api_key=api_key, 
            temperature=0.15, 
            base_url=BASE_URL,
            streaming=True
        )
        
        # 文件处理器
        self.file_handler = FileHandler(max_content_length=120000)
        
        # Prompt 模板
        self.template = ChatPromptTemplate.from_messages([
            ("system", """你是知识复习助手，帮助用户复习和学习知识。

{document_info}

请基于上述文档内容（如有）回答用户的问题或者根据用户的需求向ta提出问题。
如果没有提供文档，请基于你的知识回答。
回答要清晰、有条理，重点突出。
"""),
            ("user", "{input}")
        ])
        
        self.parser = StrOutputParser()
        self.chain = self.template | self.llm | self.parser
    
    def invoke(self, message: str, file_paths: Optional[Union[str, List[str]]] = None) -> str:
        """
        处理用户输入
        
        Args:
            message: 用户的问题或指令（文字行）
            file_paths: 文件路径（文件行），可选
                       可以是单个文件路径 str，或多个文件路径 List[str]
            
        Returns:
            str: Agent 的回答
            
        Example:
            # 无文件
            agent.invoke("什么是二叉树？")
            
            # 单个文件
            agent.invoke("总结这个文档", file_paths="./notes.pdf")
            
            # 多个文件
            agent.invoke("对比这两个文档", file_paths=["./doc1.pdf", "./doc2.docx"])
        """
        document_info = "无文档提供。"
        
        # 处理文件（如果有）
        if file_paths:
            try:
                # 加载所有文件
                files_data = self.file_handler.load_files(file_paths)
                
                # 格式化为 prompt 文本
                document_info = self.file_handler.format_for_prompt(files_data)
                
                # 统计成功/失败数量
                success_count = sum(1 for f in files_data if f["content"] is not None)
                total_count = len(files_data)
                
                if success_count > 0:
                    print(f"已加载 {success_count}/{total_count} 个文件")
                else:
                    print(f"所有文件加载失败")
                    
            except Exception as e:
                print(f"文件处理出错: {e}")
                document_info = f"文件处理失败: {e}"
        
        # 调用 LLM
        try:
            response = self.chain.invoke({
                "input": message,
                "document_info": document_info
            })
            return response
        except Exception as e:
            return f"处理失败: {e}"
    def stream(self, message: str, file_paths: Optional[Union[str, List[str]]] = None) -> str:
        """
        流式处理用户输入
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
        try:
            for chunk in self.chain.stream({"input": message, "document_info": document_info}):
                yield chunk
        except Exception as e:
            yield f"处理失败: {e}"

if __name__ == "__main__":
    agent = ReviewAgent()
    
    # 测试1: 无文件
    print("=== 测试1: 无文件 ===")
    result = agent.invoke("什么是快速排序？")
    print(result)
    print()
    
    # 测试2: 有文件（需要你创建测试文件）
    # print("=== 测试2: 有文件 ===")
    # result = agent.invoke("总结这个文档的主要内容", file_paths=["./test.txt"])
    # print(result)
