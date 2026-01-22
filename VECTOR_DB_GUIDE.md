# 向量数据库管理指南

## 概述

`vector_db_manager.py` 是独立的向量数据库管理工具，负责知识库的索引、删除、查询等操作。

**设计理念**：
- 像 `main.py` 管理 Agent 流程一样，`vector_db_manager.py` 管理向量数据库
- 两者解耦，职责清晰

---

## 快速开始（一分钟上手）

```bash
# 1. 安装依赖
pip install chromadb sentence-transformers

# 2. 索引整个文件夹（自动扫描所有支持的文件）
python vector_db_manager.py index my_knowledge ./我的复习资料/

# 3. 搜索测试
python vector_db_manager.py search my_knowledge "二叉树"

# 完成！
```

---

## 核心功能

### 1. 索引文档（添加到向量库）

#### 索引单个文件
```bash
python vector_db_manager.py index my_collection notes.pdf
```

#### 索引多个文件
```bash
python vector_db_manager.py index my_collection file1.pdf file2.docx file3.txt
```

#### 索引整个文件夹（推荐）
```bash
# 递归扫描文件夹中所有支持的文件
python vector_db_manager.py index my_collection ./docs/

# 支持的格式：.pdf .docx .pptx .txt .md
```

#### 混合使用
```bash
# 同时索引文件和文件夹
python vector_db_manager.py index my_collection notes.pdf ./docs/ algorithms.md
```

### 2. 查看集合

#### 列出所有集合
```bash
python vector_db_manager.py list
```

#### 查看集合详细信息
```bash
python vector_db_manager.py info review_docs

# 输出示例:
# [INFO] 集合信息: review_docs
#   总块数: 150
#   文件数: 5
#   来源文件:
#     - notes.pdf: 45 块
#     - algorithms.md: 30 块
#     - python_basics.txt: 25 块
#     ...
```

### 3. 搜索测试

```bash
python vector_db_manager.py search review_docs "什么是快速排序"

# 输出示例:
# [1] 相似度: 0.2345
#     来源: algorithms.md
#     内容: 快速排序是一种分治算法...
```

### 4. 删除管理

#### 删除特定文件的所有块
```bash
python vector_db_manager.py delete review_docs notes.pdf
```

#### 清空集合（保留集合结构）
```bash
python vector_db_manager.py clear review_docs
# 需要输入 yes 确认
```

#### 删除整个集合
```bash
python vector_db_manager.py drop review_docs
# 需要输入 yes 确认
```

---

## 使用场景

### 场景 1: 初始化知识库

```bash
# 一次性索引所有复习资料
python vector_db_manager.py index review_knowledge ./复习资料/

# 索引面试题库
python vector_db_manager.py index interview_qa ./面试题/
```

### 场景 2: 定期更新

```bash
# 添加新文档
python vector_db_manager.py index review_knowledge ./新资料/

# 删除过时文档
python vector_db_manager.py delete review_knowledge old_notes.pdf
```

### 场景 3: 多个集合管理

```bash
# 创建不同主题的集合
python vector_db_manager.py index python_docs ./python教程/
python vector_db_manager.py index java_docs ./java教程/
python vector_db_manager.py index algorithms ./算法笔记/

# 查看所有集合
python vector_db_manager.py list
```

---

## 目录结构

```
chat-review-interview-agent/
├── vector_db_manager.py      # 向量库管理器（主程序）
├── file_handler.py            # 文件处理（分块）
├── chroma_db/                 # 向量库存储目录
│   ├── review_docs/          # 集合1
│   │   └── chroma.sqlite3
│   ├── interview_qa/         # 集合2
│   │   └── chroma.sqlite3
│   └── algorithms/           # 集合3
│       └── chroma.sqlite3
└── knowledge_base/           # 原始文档（你的资料）
    ├── python/
    ├── algorithms/
    └── interview/
```

---

## Python API 使用

除了命令行，也可以在代码中使用：

```python
from vector_db_manager import VectorDBManager

# 初始化
manager = VectorDBManager(use_unstructured=False)

# 索引文件夹
count = manager.index_documents(
    file_paths="./knowledge_base/",
    collection_name="my_docs",
    max_chars=1000
)

# 搜索
results = manager.search("my_docs", "快速排序是什么", k=3)

# 查看信息
info = manager.get_collection_info("my_docs")

# 删除文件
manager.delete_by_source("my_docs", "old_file.pdf")
```

---

## 与 Agent 集成

向量库管理器是独立的，Agent 只需要调用搜索功能：

```python
# review_agent.py
from vector_db_manager import VectorDBManager

class ReviewAgent:
    def __init__(self):
        # ... 其他初始化
        self.vector_db = VectorDBManager()
        self.vector_db.load_collection("review_knowledge")  # 加载已有的知识库
    
    def invoke_with_rag(self, message):
        # 从向量库检索
        results = self.vector_db.search("review_knowledge", message, k=3)
        
        # 组装上下文
        context = "\n\n".join([r["content"] for r in results])
        
        # 调用 LLM
        return self.chain.invoke({
            "input": message,
            "document_info": context
        })
```

---

## 注意事项

1. **首次运行会下载嵌入模型**（约 400MB），需要联网
2. **文件夹扫描是递归的**，会包含所有子目录
3. **索引是增量的**，重复索引同一文件会添加重复块
4. **删除操作需要确认**，避免误删

---

## 故障排查

### 问题: 找不到集合
```bash
# 检查集合是否存在
python vector_db_manager.py list
```

### 问题: 文件夹索引失败
```bash
# 检查文件夹路径是否正确
ls -la ./knowledge_base/
```

### 问题: 搜索结果为空
```bash
# 检查集合中有多少文档
python vector_db_manager.py info my_collection
```
