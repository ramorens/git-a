# AI智能简历分析系统

基于阿里云Serverless + Python的智能简历分析RESTful API服务。

## 功能特性

- PDF简历上传与解析（支持多页）
- AI自动提取关键信息（姓名、电话、邮箱、技能、工作经历等）
- 简历与岗位需求智能匹配评分
- Redis缓存加速（可选）

## 项目结构

```
├── app.py              # Flask主应用
├── pdf_parser.py       # PDF解析模块
├── ai_extractor.py     # AI信息提取模块
├── cache_manager.py    # Redis缓存管理
├── index.py            # 阿里云FC入口
├── s.yaml              # Serverless Devs配置
├── requirements.txt    # Python依赖
└── static/index.html   # 前端页面
```

## API接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/upload-resume` | POST | 上传并解析简历 |
| `/api/match-resume` | POST | 简历与岗位匹配 |
| `/api/analyze-resume` | POST | 一站式分析（上传+匹配） |
| `/health` | GET | 健康检查 |

## 本地运行

```bash
# 安装依赖
pip install -r requirements.txt

# 设置环境变量
set DASHSCOPE_API_KEY=your_api_key

# 启动服务
python app.py
```

访问 http://localhost:5000

## 阿里云部署

1. 安装Serverless Devs CLI：
```bash
npm install -g @serverless-devs/s
```

2. 配置阿里云账号：
```bash
s config add
```

3. 设置环境变量后部署：
```bash
set DASHSCOPE_API_KEY=your_api_key
s deploy
```

## 环境变量

| 变量名 | 说明 | 必填 |
|--------|------|------|
| DASHSCOPE_API_KEY | 阿里云通义千问API Key | 是 |
| REDIS_HOST | Redis地址 | 否 |
| REDIS_PORT | Redis端口 | 否 |
| REDIS_PASSWORD | Redis密码 | 否 |
