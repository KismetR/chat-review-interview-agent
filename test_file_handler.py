"""
测试 FileHandler 的两种使用方式
"""

from file_handler import FileHandler

# def test_normal_load():
#     """测试1: 普通加载（不需要 RAG）"""
#     print("=" * 60)
#     print("测试 1: 普通文件加载（完整内容）")
#     print("=" * 60)
    
#     handler = FileHandler()
    
#     # 加载文件
#     results = handler.load_files("test.txt")
    
#     # 显示结果
#     if results[0]["content"]:
#         print(f"\n✅ 加载成功!")
#         print(f"文件名: {results[0]['metadata']['filename']}")
#         print(f"字符数: {results[0]['metadata']['char_count']}")
#         print(f"\n内容预览:\n{results[0]['content'][:200]}...")
#     else:
#         print(f"\n❌ 加载失败: {results[0]['metadata']['error']}")

# def test_formatted_output():
#     """测试2: 格式化输出（用于 Agent Prompt）"""
#     print("\n" + "=" * 60)
#     print("测试 2: 格式化输出（用于 Prompt）")
#     print("=" * 60)
    
#     handler = FileHandler()
#     results = handler.load_files("test.txt")
#     formatted = handler.format_for_prompt(results)
    
#     print(formatted)

# def test_rag_simple_chunks():
#     """测试3: RAG 简单分块"""
#     print("\n" + "=" * 60)
#     print("测试 3: RAG 简单分块（不使用 unstructured）")
#     print("=" * 60)
    
#     handler = FileHandler(use_unstructured=False)
    
#     # 分块加载
#     chunks = handler.load_for_rag("test.txt", max_chars=500)
    
#     print(f"\n✅ 生成了 {len(chunks)} 个块")
#     print(f"\n第一个块示例:")
#     print(f"内容: {chunks[0]['content'][:200]}...")
#     print(f"元数据: {chunks[0]['metadata']}")

def test_rag_with_unstructured():
    """测试4: RAG 使用 unstructured（如果已安装）"""
    print("\n" + "=" * 60)
    print("测试 4: RAG 使用 unstructured 库")
    print("=" * 60)
    
    try:
        handler = FileHandler(use_unstructured=True)
        chunks = handler.load_for_rag("bagu.pdf", chunk_strategy="by_title", max_chars=1000)
        
        print(f"\n✅ 生成了 {len(chunks)} 个结构化块")
        if chunks:
            print(f"\n第一个块:")
            print(f"类型: {chunks[0]['metadata'].get('element_type', 'N/A')}")
            print(f"内容: {chunks[0]['content'][:200]}...")
    
    except ImportError as e:
        print(f"\n⚠️ unstructured 未安装: {e}")
        print("使用 'pip install unstructured' 安装后可以使用高级功能")

if __name__ == "__main__":
    print("\n🚀 开始测试 FileHandler\n")
    
    # test_normal_load()
    # test_formatted_output()
    # test_rag_simple_chunks()
    test_rag_with_unstructured()
    
    print("\n✅ 测试完成\n")
