# ShadowForge 使用说明

## 项目简介
ShadowForge 是一个多模态敏感数据深度仿真引擎，用于生成数据泄漏的仿真数据集。

## 环境准备
- Python 3.8+
- Node.js 18+
- 配置 LLM API 密钥

## 快速开始

### 1. 后端启动
```bash
cd backend
pip install -r requirements.txt
python main.py
```
后端服务将在 http://localhost:8000 启动。
- Swagger UI：http://localhost:8000/docs
- ReDoc：http://localhost:8000/redoc

### 2. 前端启动
```bash
cd frontend
npm install
npm run dev
```
前端服务将在 http://localhost:3000 启动。

## 功能使用
1. 访问 http://localhost:3000 进入前端界面
2. 注册账户并登录
3. 在仪表板创建新任务
4. 配置生成参数（密钥类型、场景、模态等）
5. 提交任务并查看生成结果

## 配置说明
- 通过环境变量或配置文件设置 LLM API 密钥
- 输出文件保存在指定目录中
- 支持多种数据模态：文本、图像、音频、视频、PDF等