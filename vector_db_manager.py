"""
向量数据库管理器
负责知识库的索引、删除、查询等操作
独立于 Agent，专注于向量数据库的管理
"""

import os
from pathlib import Path
from typing import List, Optional, Dict
from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.docstore.document import Document
from file_handler import FileHandler

load_dotenv()


class VectorDBManager:
    """向量数据库管理器"""
    
    def __init__(
        self,
        persist_directory: str = "./chroma_db",
        use_unstructured: bool = False,
        embedding_model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    ):
        """
        Args:
            persist_directory: 向量库存储目录
            use_unstructured: 是否使用 unstructured 进行高级分块
            embedding_model: 嵌入模型名称
        """
        self.persist_directory = persist_directory
        self.file_handler = FileHandler(use_unstructured=use_unstructured)
        
        print(f"[INFO] 初始化嵌入模型: {embedding_model}")
        self.embeddings = HuggingFaceEmbeddings(
            model_name=embedding_model,
            model_kwargs={'device': 'cpu'}
        )
        
        self.vectorstore = None
        self.current_collection = None
    
    # ==================== 文件扫描 ====================
    
    def scan_directory(self, directory: str, recursive: bool = True) -> List[str]:
        """
        扫描文件夹中所有支持的文件
        
        Args:
            directory: 目录路径
            recursive: 是否递归扫描子目录
            
        Returns:
            list: 文件路径列表
        """
        dir_path = Path(directory)
        
        if not dir_path.exists():
            raise FileNotFoundError(f"目录不存在: {directory}")
        
        if not dir_path.is_dir():
            raise ValueError(f"不是有效的目录: {directory}")
        
        print(f"[INFO] 扫描目录: {directory}")
        
        files = []
        
        if recursive:
            # 递归扫描
            for ext in self.file_handler.SUPPORTED_EXTENSIONS:
                pattern = f"**/*{ext}"
                matched = list(dir_path.glob(pattern))
                files.extend(matched)
        else:
            # 只扫描当前目录
            for ext in self.file_handler.SUPPORTED_EXTENSIONS:
                pattern = f"*{ext}"
                matched = list(dir_path.glob(pattern))
                files.extend(matched)
        
        # 转为字符串路径
        file_paths = [str(f) for f in files]
        
        print(f"[INFO] 找到 {len(file_paths)} 个支持的文件:")
        for f in file_paths:
            print(f"  - {Path(f).name}")
        
        return file_paths
    
    # ==================== 索引管理（添加文档） ====================
    
    def index_documents(
        self,
        file_paths,
        collection_name: str = "default",
        chunk_strategy: str = "simple",
        max_chars: int = 1000,
        metadata: Optional[Dict] = None
    ) -> int:
        """
        索引文档到向量库（支持文件或文件夹）
        
        Args:
            file_paths: 文件/文件夹路径，str 或 List[str]
            collection_name: 集合名称（如 "review_docs", "interview_qa"）
            chunk_strategy: 分块策略 "simple" 或 "by_title"
            max_chars: 每块最大字符数
            metadata: 额外的元数据（如标签、分类等）
            
        Returns:
            int: 索引的文档块数量
        """
        print(f"\n{'='*60}")
        print(f"开始索引文档到集合: {collection_name}")
        print(f"{'='*60}")
        
        # 0. 处理路径（文件或文件夹）
        if isinstance(file_paths, str):
            file_paths = [file_paths]
        
        all_files = []
        for path in file_paths:
            path_obj = Path(path)
            
            if path_obj.is_file():
                all_files.append(path)
            elif path_obj.is_dir():
                print(f"\n[INFO] 扫描文件夹: {path}")
                folder_files = self.scan_directory(path, recursive=True)
                all_files.extend(folder_files)
            else:
                print(f"[WARNING] 路径不存在: {path}")
        
        if not all_files:
            print("[ERROR] 没有找到任何文件")
            return 0
        
        print(f"\n[INFO] 共找到 {len(all_files)} 个文件待处理")
        
        # 1. 加载并分块
        chunks = self.file_handler.load_for_rag(
            all_files,
            chunk_strategy=chunk_strategy,
            max_chars=max_chars
        )
        
        if not chunks:
            print("[ERROR] 没有生成任何文档块")
            return 0
        
        # 2. 转换为 LangChain Document
        documents = []
        for chunk in chunks:
            chunk_metadata = chunk["metadata"].copy()
            
            # 添加额外元数据
            if metadata:
                chunk_metadata.update(metadata)
            
            documents.append(
                Document(
                    page_content=chunk["content"],
                    metadata=chunk_metadata
                )
            )
        
        print(f"[INFO] 准备向量化 {len(documents)} 个文档块...")
        
        # 3. 加载或创建向量库
        collection_path = f"{self.persist_directory}/{collection_name}"
        
        if Path(collection_path).exists():
            # 已存在，追加
            print(f"[INFO] 集合已存在，追加新文档...")
            self.vectorstore = Chroma(
                collection_name=collection_name,
                embedding_function=self.embeddings,
                persist_directory=collection_path
            )
            self.vectorstore.add_documents(documents)
        else:
            # 不存在，创建新的
            print(f"[INFO] 创建新集合...")
            self.vectorstore = Chroma.from_documents(
                documents=documents,
                embedding=self.embeddings,
                collection_name=collection_name,
                persist_directory=collection_path
            )
        
        self.current_collection = collection_name
        
        print(f"[SUCCESS] ✅ 已索引 {len(documents)} 个块")
        print(f"[INFO] 存储位置: {collection_path}\n")
        
        return len(documents)
    
    # ==================== 删除管理 ====================
    
    def delete_by_source(self, collection_name: str, source_filename: str) -> int:
        """
        从向量库中删除指定文件的所有块
        
        Args:
            collection_name: 集合名称
            source_filename: 源文件名（如 "notes.pdf"）
            
        Returns:
            int: 删除的文档块数量
        """
        print(f"\n[INFO] 从集合 '{collection_name}' 删除文件: {source_filename}")
        
        # 加载向量库
        self.load_collection(collection_name)
        
        if not self.vectorstore:
            print("[ERROR] 集合不存在")
            return 0
        
        # 查询该文件的所有块
        results = self.vectorstore.get(
            where={"source": source_filename}
        )
        
        if not results['ids']:
            print(f"[WARNING] 未找到文件 '{source_filename}' 的记录")
            return 0
        
        # 删除
        self.vectorstore.delete(ids=results['ids'])
        
        print(f"[SUCCESS] ✅ 已删除 {len(results['ids'])} 个块")
        return len(results['ids'])
    
    def delete_collection(self, collection_name: str):
        """
        删除整个集合
        
        Args:
            collection_name: 集合名称
        """
        collection_path = Path(f"{self.persist_directory}/{collection_name}")
        
        if not collection_path.exists():
            print(f"[WARNING] 集合不存在: {collection_name}")
            return
        
        print(f"[INFO] 删除集合: {collection_name}")
        
        # 删除目录
        import shutil
        shutil.rmtree(collection_path)
        
        print(f"[SUCCESS] ✅ 集合已删除")
        
        if self.current_collection == collection_name:
            self.vectorstore = None
            self.current_collection = None
    
    def clear_collection(self, collection_name: str):
        """
        清空集合（保留集合，删除所有文档）
        
        Args:
            collection_name: 集合名称
        """
        print(f"[INFO] 清空集合: {collection_name}")
        
        self.load_collection(collection_name)
        
        if not self.vectorstore:
            print("[ERROR] 集合不存在")
            return
        
        # 获取所有 ID
        all_data = self.vectorstore.get()
        
        if all_data['ids']:
            self.vectorstore.delete(ids=all_data['ids'])
            print(f"[SUCCESS] ✅ 已清空 {len(all_data['ids'])} 个块")
        else:
            print("[INFO] 集合已经是空的")
    
    # ==================== 查询管理 ====================
    
    def load_collection(self, collection_name: str):
        """
        加载现有集合
        
        Args:
            collection_name: 集合名称
        """
        collection_path = f"{self.persist_directory}/{collection_name}"
        
        if not Path(collection_path).exists():
            print(f"[ERROR] 集合不存在: {collection_name}")
            return False
        
        print(f"[INFO] 加载集合: {collection_name}")
        
        self.vectorstore = Chroma(
            collection_name=collection_name,
            embedding_function=self.embeddings,
            persist_directory=collection_path
        )
        
        self.current_collection = collection_name
        print(f"[SUCCESS] ✅ 集合加载成功")
        return True
    
    def list_collections(self) -> List[str]:
        """
        列出所有集合
        
        Returns:
            list: 集合名称列表
        """
        db_path = Path(self.persist_directory)
        
        if not db_path.exists():
            print("[INFO] 向量库目录不存在")
            return []
        
        collections = [d.name for d in db_path.iterdir() if d.is_dir()]
        
        print(f"\n[INFO] 找到 {len(collections)} 个集合:")
        for col in collections:
            print(f"  - {col}")
        
        return collections
    
    def get_collection_info(self, collection_name: str) -> Dict:
        """
        获取集合信息
        
        Args:
            collection_name: 集合名称
            
        Returns:
            dict: 集合统计信息
        """
        if not self.load_collection(collection_name):
            return {}
        
        # 获取所有数据
        data = self.vectorstore.get()
        
        # 统计来源文件
        sources = {}
        for metadata in data['metadatas']:
            source = metadata.get('source', 'unknown')
            sources[source] = sources.get(source, 0) + 1
        
        info = {
            "collection_name": collection_name,
            "total_chunks": len(data['ids']),
            "source_files": sources,
            "file_count": len(sources)
        }
        
        print(f"\n[INFO] 集合信息: {collection_name}")
        print(f"  总块数: {info['total_chunks']}")
        print(f"  文件数: {info['file_count']}")
        print(f"  来源文件:")
        for source, count in sources.items():
            print(f"    - {source}: {count} 块")
        
        return info
    
    def search(
        self,
        collection_name: str,
        query: str,
        k: int = 3,
        filter_metadata: Optional[Dict] = None
    ) -> List[Dict]:
        """
        在集合中搜索
        
        Args:
            collection_name: 集合名称
            query: 查询文本
            k: 返回结果数
            filter_metadata: 元数据过滤
            
        Returns:
            list: 搜索结果
        """
        if not self.load_collection(collection_name):
            return []
        
        print(f"\n[INFO] 搜索: '{query[:50]}...'")
        
        search_kwargs = {"k": k}
        if filter_metadata:
            search_kwargs["filter"] = filter_metadata
        
        results = self.vectorstore.similarity_search_with_score(query, **search_kwargs)
        
        print(f"[SUCCESS] 找到 {len(results)} 个相关结果:")
        
        search_results = []
        for i, (doc, score) in enumerate(results, 1):
            print(f"\n  [{i}] 相似度: {score:.4f}")
            print(f"      来源: {doc.metadata.get('source', 'N/A')}")
            print(f"      内容: {doc.page_content[:100]}...")
            
            search_results.append({
                "content": doc.page_content,
                "metadata": doc.metadata,
                "score": score
            })
        
        return search_results


def main():
    """命令行界面"""
    import sys
    
    manager = VectorDBManager(use_unstructured=False)
    
    if len(sys.argv) < 2:
        print("""
向量数据库管理器 - 使用说明

命令:
  python vector_db_manager.py index <集合名> <路径...>         # 索引文档（文件或文件夹）
  python vector_db_manager.py delete <集合名> <文件名>         # 删除文件
  python vector_db_manager.py clear <集合名>                   # 清空集合
  python vector_db_manager.py drop <集合名>                    # 删除集合
  python vector_db_manager.py list                             # 列出所有集合
  python vector_db_manager.py info <集合名>                    # 查看集合信息
  python vector_db_manager.py search <集合名> <查询>           # 搜索

示例:
  # 索引单个文件
  python vector_db_manager.py index review_docs notes.pdf
  
  # 索引多个文件
  python vector_db_manager.py index review_docs notes.pdf algorithms.md
  
  # 索引整个文件夹（自动扫描所有支持的文件）
  python vector_db_manager.py index review_docs ./knowledge_base/
  
  # 混合使用（文件 + 文件夹）
  python vector_db_manager.py index review_docs notes.pdf ./docs/
  
  # 删除特定文件
  python vector_db_manager.py delete review_docs notes.pdf
  
  # 查看集合信息
  python vector_db_manager.py info review_docs
  
  # 搜索
  python vector_db_manager.py search review_docs "什么是快速排序"
  
  # 列出所有集合
  python vector_db_manager.py list
        """)
        return
    
    command = sys.argv[1].lower()
    
    # 列出所有集合
    if command == "list":
        collections = manager.list_collections()
        if not collections:
            print("\n还没有任何集合")
    
    # 查看集合信息
    elif command == "info":
        if len(sys.argv) < 3:
            print("\n请指定集合名称")
            return
        collection_name = sys.argv[2]
        manager.get_collection_info(collection_name)
    
    # 索引文档
    elif command == "index":
        if len(sys.argv) < 4:
            print("\n用法: index <集合名> <文件路径/文件夹路径...>")
            print("提示: 可以指定文件或文件夹，文件夹会自动扫描所有支持的文件")
            return
        
        collection_name = sys.argv[2]
        paths = sys.argv[3:]
        
        # 处理路径（文件或文件夹）
        all_files = []
        for path in paths:
            path_obj = Path(path)
            
            if path_obj.is_file():
                # 直接添加文件
                all_files.append(path)
            elif path_obj.is_dir():
                # 扫描文件夹
                print(f"\n[INFO] 检测到文件夹: {path}")
                folder_files = manager.scan_directory(path, recursive=True)
                all_files.extend(folder_files)
            else:
                print(f"[WARNING] 路径不存在，跳过: {path}")
        
        if not all_files:
            print("\n没有找到任何支持的文件")
            return
        
        print(f"\n将 {len(all_files)} 个文件索引到集合 '{collection_name}'")
        
        count = manager.index_documents(
            file_paths=all_files,
            collection_name=collection_name,
            chunk_strategy="simple",
            max_chars=1000
        )
        
        print(f"\n成功索引 {count} 个文档块")
    
    # 删除文件
    elif command == "delete":
        if len(sys.argv) < 4:
            print("\n用法: delete <集合名> <文件名>")
            return
        
        collection_name = sys.argv[2]
        source_filename = sys.argv[3]
        
        count = manager.delete_by_source(collection_name, source_filename)
        
        if count > 0:
            print(f"\n✅ 成功删除 {count} 个块")
    
    # 清空集合
    elif command == "clear":
        if len(sys.argv) < 3:
            print("\n请指定集合名称")
            return
        
        collection_name = sys.argv[2]
        
        confirm = input(f"⚠️  确认清空集合 '{collection_name}' 吗？(yes/no): ")
        if confirm.lower() == 'yes':
            manager.clear_collection(collection_name)
        else:
            print("已取消")
    
    # 删除集合
    elif command == "drop":
        if len(sys.argv) < 3:
            print("\n请指定集合名称")
            return
        
        collection_name = sys.argv[2]
        
        confirm = input(f"⚠️  确认删除集合 '{collection_name}' 吗？(yes/no): ")
        if confirm.lower() == 'yes':
            manager.delete_collection(collection_name)
        else:
            print("已取消")
    
    # 搜索
    elif command == "search":
        if len(sys.argv) < 4:
            print("\n用法: search <集合名> <查询文本>")
            return
        
        collection_name = sys.argv[2]
        query = " ".join(sys.argv[3:])
        
        results = manager.search(collection_name, query, k=5)
        
        if not results:
            print("\n没有找到相关结果")
    
    else:
        print(f"❌ 未知命令: {command}")
        print("运行 'python vector_db_manager.py' 查看帮助")


if __name__ == "__main__":
    main()
