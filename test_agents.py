"""
测试 Agent 的使用示例
演示如何传递文件和文字
"""

from review_agent import ReviewAgent
from chat_agent import ChatAgent

def test_review_agent():
    """测试复习 Agent"""
    agent = ReviewAgent()
    
    # print("=" * 60)
    # print("测试 1: 无文件，直接提问")
    # print("=" * 60)
    # for chunk in agent.stream("什么是快速排序算法？请简要说明。"):
    #     print(chunk, end="", flush=True)
    # print()
    
    print("=" * 60)
    print("测试 2: 有文件（需要创建 test.txt）")
    print("=" * 60)
    
#     # 创建测试文件
#     test_content = """安史之乱（755年12月16日－763年2月17日）是中国唐朝中期爆发的一场大规模内战，
# 历时七年余。这场叛乱最初由三镇节度使安禄山及其部将史思明发动，
# 以讨伐外戚杨国忠为名率兵入朝，
# 叛乱最终因内部分裂以及唐朝及其盟友的反攻而失败。
# 这场叛乱横跨了唐玄宗、唐肃宗和唐代宗三位皇帝的统治，
# 事件对唐朝国力造成毁灭性打击，被视为唐朝由盛转衰的关键事件。
# """
#     with open("test.txt", "w", encoding="utf-8") as f:
#         f.write(test_content)
    
    # 单个文件可以直接传字符串，不用列表
    for chunk in agent.stream(
        "根据文档给我出十道选择题",
        file_paths="bagu.pdf"
    ):
        print(chunk, end="", flush=True)
    print()
    
    # print("=" * 60)
    # print("测试 3: 多个文件")
    # print("=" * 60)
    
#     # 创建第二个测试文件
#     test_content2 = """唐朝历唐太宗“贞观之治”、唐高宗“永徽之治”、武则天“贞观遗风”及唐玄宗的“开元盛世”后，
# 国势持续增加，文治武功在唐玄宗开元天宝年间达至鼎盛状态。
# 为了炫耀武力，大开边功，从唐睿宗景云二年开始，到开元末年，边境上先后设立了十个节度使。
# 到天宝时期，这些节度使集军政财权于一身，成为地方上最高的军政长官，改变了唐朝初年内重外轻的局面，加剧了唐中央和地方藩镇的矛盾。
# 安史之乱发生并席卷北方后，对唐朝乃至中原后世的发展产生重大影响。
#     """
    
#     with open("test2.txt", "w", encoding="utf-8") as f:
#         f.write(test_content2)
    
    # result = agent.invoke(
    #     "对比这两个文档，找出共同点和区别",
    #     file_paths=["test.txt", "test2.txt"]
    # )
    # print(result)
    # print()

def test_chat_agent():
    """测试聊天 Agent"""
    agent = ChatAgent()
    
    print("=" * 60)
    print("测试聊天 Agent")
    print("=" * 60)
    
    # 聊天 agent 不需要文件，只需要消息
    for chunk in agent.stream("今天天气不错啊"):
        print(chunk, end="", flush=True)
    print()

if __name__ == "__main__":
    print("\n" + "开始测试 Agents" + "\n")
    
    test_review_agent()
    # test_chat_agent()
    
    print("\n" + "测试完成" + "\n")
