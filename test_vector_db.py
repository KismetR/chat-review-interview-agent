"""
测试向量数据库管理器
演示文件夹索引功能
"""

from vector_db_manager import VectorDBManager
from pathlib import Path

def create_test_docs():
    """创建一些测试文档"""
    test_dir = Path("./test_knowledge")
    test_dir.mkdir(exist_ok=True)
    
    # 创建几个测试文件
    (test_dir / "python_basics.txt").write_text("""
Python 基础知识

1. 数据类型
Python 有多种内置数据类型，包括整数、浮点数、字符串、列表、字典等。

2. 控制流
Python 使用 if-elif-else 进行条件判断，使用 for 和 while 进行循环。

3. 函数
使用 def 关键字定义函数，支持默认参数、可变参数等。
    """, encoding="utf-8")
    
    (test_dir / "algorithms.txt").write_text("""
算法知识

1. 排序算法
常见的排序算法包括冒泡排序、快速排序、归并排序等。

2. 查找算法
二分查找是一种高效的查找方法，时间复杂度为 O(log n)。

3. 数据结构
栈、队列、链表、树、图等是基础数据结构。
    """, encoding="utf-8")
    
    # 创建子目录
    sub_dir = test_dir / "advanced"
    sub_dir.mkdir(exist_ok=True)
    
    (sub_dir / "design_patterns.txt").write_text("""
设计模式

1. 单例模式
确保一个类只有一个实例，并提供全局访问点。

2. 工厂模式
定义一个创建对象的接口，让子类决定实例化哪一个类。

3. 观察者模式
定义对象间的一对多依赖，当一个对象状态改变时，所有依赖者都得到通知。
    """, encoding="utf-8")
    
    print(f"✅ 测试文档已创建在: {test_dir}")
    return str(test_dir)


def test_folder_indexing():
    """测试文件夹索引"""
    print("=" * 60)
    print("测试：索引整个文件夹")
    print("=" * 60)
    
    # 创建测试文档
    test_dir = create_test_docs()
    
    # 初始化管理器
    manager = VectorDBManager(use_unstructured=False)
    
    # 索引整个文件夹（包括子目录）
    print(f"\n开始索引文件夹: {test_dir}")
    
    count = manager.index_documents(
        file_paths=test_dir,  # 直接传文件夹路径
        collection_name="test_collection",
        chunk_strategy="simple",
        max_chars=500
    )
    
    print(f"\n✅ 索引完成，共 {count} 个块")
    
    # 查看集合信息
    print("\n" + "=" * 60)
    print("查看集合信息")
    print("=" * 60)
    manager.get_collection_info("test_collection")
    
    # 测试搜索
    print("\n" + "=" * 60)
    print("测试搜索")
    print("=" * 60)
    
    results = manager.search("test_collection", "什么是快速排序", k=2)
    
    if results:
        print(f"\n搜索到 {len(results)} 个相关结果")


def test_mixed_paths():
    """测试混合路径（文件+文件夹）"""
    print("\n" + "=" * 60)
    print("测试：混合索引（文件 + 文件夹）")
    print("=" * 60)
    
    manager = VectorDBManager(use_unstructured=False)
    
    # 混合：单个文件 + 整个文件夹
    paths = [
        "test.txt",              # 单个文件
        "./test_knowledge"       # 整个文件夹
    ]
    
    count = manager.index_documents(
        file_paths=paths,
        collection_name="mixed_collection",
        max_chars=500
    )
    
    print(f"\n✅ 混合索引完成，共 {count} 个块")
    manager.get_collection_info("mixed_collection")


if __name__ == "__main__":
    print("\n🚀 开始测试向量数据库管理器\n")
    
    test_folder_indexing()
    test_mixed_paths()
    
    print("\n✅ 测试完成\n")
    
    print("清理测试数据:")
    print("  python vector_db_manager.py drop test_collection")
    print("  python vector_db_manager.py drop mixed_collection")
    print("  rm -rf test_knowledge")
