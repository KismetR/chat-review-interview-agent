import json
import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

# 安全地获取 API key
api_key = os.getenv("DEEPSEEK_API_KEY","sk-83241d57cc334cd19a4b817b9a68c511")
if not api_key:
    raise ValueError("DEEPSEEK_API_KEY 环境变量未设置")

# 可选：base_url 也从环境变量读取
BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")

class RouterAgent:
    # 添加常量
    MAX_INPUT_LENGTH = 1000
    VALID_AGENTS = ['review', 'interview', 'chat', 'resume_estimate', 'resume_generate', 'illegal_input']
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model="deepseek-chat", 
            api_key=api_key, 
            temperature=0, 
            base_url=BASE_URL
        )
        self.template = ChatPromptTemplate.from_messages([
            ("system", """你是路由器，负责将用户输入分发给合适的代理。 
            你会收到一个用户输入，你需要决定哪个代理或哪几个代理来协同处理这个请求。
            业务范围：仅限参与关于【日常聊天（你看不懂的那种大概率不属于这个范围）、知识复习、简历生成、面试辅导】的对话。
            你会分配以下代理来处理用户输入：review, interview, chat, resume_estimate, resume_generate, illegal_input
            review: 负责复习知识
            interview: 负责面试
            chat: 负责聊天
            resume_estimate: 负责简历评估
            resume_generate: 负责简历生成
            illegal_input: 负责处理非法输入
            你需要返回代理的名称或名称列表。如果需要多个代理协同处理，请返回名称列表。
            请只返回代理的名称或名称列表，不要返回其他文本。
            格式应该像这样：{{"agents": ["review"]}} 或 {{"agents": ["review", "interview"]}}
            """),
            ("user", "{input}")  
        ])
        self.parser = JsonOutputParser()
        self.chain = self.template | self.llm | self.parser
    
    def rule_input_validation(self, user_input: str) -> bool:
        """验证用户输入"""
        if not user_input or not user_input.strip():
            return False
        if len(user_input) > self.MAX_INPUT_LENGTH:
            return False
        return True
    
    def invoke(self, user_input: str) -> tuple[list[str], str]:
        """
        路由用户输入到合适的代理
        
        Returns:
            tuple: (agents列表, 原始输入)
        """
        # 输入验证
        if not self.rule_input_validation(user_input):
            return ['illegal_input'], user_input
        
        # LLM 调用，添加异常处理
        try:
            response = self.chain.invoke({"input": user_input})
            agents = response.get("agents", [])
            
            # 确保返回的是列表
            if not isinstance(agents, list):
                agents = [agents]
            
            # 验证返回的代理名称是否有效
            agents = [a for a in agents if a in self.VALID_AGENTS]
            
            # 如果没有有效代理，返回 illegal_input
            if not agents:
                return ['illegal_input'], user_input
                
            return agents, user_input
            
        except Exception as e:
            print(f"路由错误: {e}")
            return ['illegal_input'], user_input

if __name__ == "__main__":
    router_agent = RouterAgent()
    user_input = input("请输入: ")
    agents, original_input = router_agent.invoke(user_input)
    
    if 'illegal_input' in agents:
        print("⚠️ 很抱歉，您的请求包含敏感内容或违反了使用规范，无法提供服务。")
    else:
        print(f"回答分发至: {agents}")
        print(f"原始输入: {original_input}")
