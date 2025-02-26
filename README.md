# 本地知识库 AI 问答系统

基于 FastAPI、Milvus 和 Ollama 的本地知识库 AI 问答系统。

## 功能特点

- 支持 Word、TXT 文档上传和解析
- 文档内容自动分块和向量化
- 混合检索（向量检索 + BM25）
- AI 模型问答生成
- 基于 FastAPI 的 RESTful API

## 系统要求

- Python 3.10
- Docker (用于运行 Milvus 和 Ollama)
- Windows 10/11

## 安装步骤

1. 克隆项目并安装依赖：
```bash
pip install -r requirements.txt
```

2. 启动 Milvus：
```bash
docker run -d --name milvus-standalone -p 19530:19530 -p 9091:9091 milvusdb/milvus:latest standalone
```

3. 启动 Ollama 并下载必要的模型：
```bash
docker run -d --name ollama -p 11434:11434 ollama/ollama
docker exec -it ollama ollama pull bge-m3
docker exec -it ollama ollama pull bge-reranker-v2-m3
docker exec -it ollama ollama pull deepseek-coder:7b
```

4. 启动应用：
```bash
uvicorn app.main:app --reload
```

## API 文档

启动应用后访问 http://localhost:8000/docs 查看完整的 API 文档。

## 主要 API 端点

- POST /upload - 上传文档
- POST /ask - 提问接口

## 项目结构

```
local_ai_qa/
├── app/                           # 项目核心应用目录，包含主要的应用代码和逻辑
│   ├── __init__.py                # 包初始化文件，表明该目录为一个Python包
│   ├── main.py                    # 应用入口，初始化FastAPI应用并配置路由
│   ├── config/                    # 配置文件目录，包含应用的全局配置
│   │   ├── __init__.py            # 包初始化文件
│   │   └── settings.py            # 配置文件，存储数据库连接、API密钥等重要配置信息
│   ├── models/                    # 数据模型目录，包含数据结构的定义（例如ORM模型和Pydantic模型）
│   │   ├── __init__.py            # 包初始化文件
│   │   ├── base.py                # 基础模型类，可能包含通用功能
│   │   ├── document_model.py      # 文档模型，定义文档解析、存储的相关字段和方法
│   │   └── schemas.py             # Pydantic模型，定义API请求和响应数据结构
│   ├── routers/                   # 路由处理目录，定义不同业务模块的路由
│   │   ├── __init__.py            # 包初始化文件
│   │   ├── upload_router.py       # 处理文件上传和文档解析的路由
│   │   └── qa_router.py           # 处理问题解答、向量检索、AI服务交互的路由
│   ├── services/                  # 服务层目录，处理具体的业务逻辑
│   │   ├── __init__.py            # 包初始化文件
│   │   ├── document_processing.py # 文档处理服务，负责解析文档、切块
│   │   ├── embedding_service.py   # 文字Embedding向量化服务，利用ollama模型进行文本向量化
│   │   ├── milvus_service.py      # Milvus数据库服务，管理向量存储和检索
│   │   ├── retrieval_service.py   # 向量检索服务，进行BM25检索和相似度匹配
│   │   └── ai_service.py         # AI服务，调用Qwen Chat模型进行问答响应
│   ├── utils/                     # 工具类目录，包含常用的功能函数
│   │   ├── __init__.py            # 包初始化文件
│   │   ├── file_validation.py     # 文件验证工具，检查上传文件的合法性
│   │   └── text_splitter.py       # 文本切块工具，负责将长文档拆分成小块
│   └── database/                  # 数据库相关目录，封装数据库会话管理
│       ├── __init__.py            # 包初始化文件
│       └── session.py             # 数据库会话管理，负责与Milvus数据库的交互
├── requirements.txt               # 项目依赖的Python库列表，包含FastAPI、Milvus SDK、ollama等依赖
└── Dockerfile                     # Docker镜像构建文件，定义如何构建和部署应用环境
``` 