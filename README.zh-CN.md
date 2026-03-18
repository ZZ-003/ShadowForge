# Deeptrace

[English](README.md) | [中文](README.zh-CN.md)

Deeptrace 是一个多模态敏感数据泄露仿真引擎，用于在图像、视频、音频和文档等渠道中生成高逼真合成泄露样本。

它面向安全测试、DLP 模型训练、红蓝对抗与安全培训等场景，在真实敏感数据难以获取或不适合流转时，提供可控且可扩展的替代方案。

## 项目叙事（Pitch 融合）

### 防御盲区
现实中的泄露并不只发生在文本日志中，截图、录屏、会议语音和办公文档已经成为高频泄露路径。仅依赖文本扫描的传统 DLP 难以覆盖这些通道。

### 解决方案
Deeptrace 不是简单把密钥字符串塞进文本，而是通过 LLM 进行上下文生成，把秘密放入语义连贯的宿主环境，再渲染成多模态样本。

### 实战价值
1. DLP 冷启动：在不暴露生产敏感信息的前提下批量生成训练样本。
2. 红蓝对抗：构造高可信诱饵样本，提高攻防演练真实度。
3. 安全教育：用沉浸式泄露样本强化内部培训效果。

### 愿景
模拟未见，以追踪未知。

## 为什么需要 Deeptrace

1. 覆盖多模态泄露面，而不仅是文本。
传统 DLP 更偏向文本扫描，但真实泄露经常发生在截图、录屏、会议语音和演示文档中。Deeptrace 补齐了这一实际缺口。

2. 提供安全可用的训练数据。
真实泄露样本稀缺且合规风险高。Deeptrace 可批量生成高质量合成样本，降低数据采集与共享风险。

3. 提升攻防演练真实性。
在红队诱饵和蓝队检测演练中，越贴近业务语境的样本越有价值。Deeptrace 强调“可用性真实”而不仅是“格式正确”。

## 核心创新点

1. 基于 LLM 的上下文生成。
不是简单拼接密钥字符串，而是按秘密类型生成语义连贯的宿主内容，如代码片段、配置文件、聊天记录和业务文档。

2. 自适应场景路由。
对图像和视频任务，系统可自动判断秘密更可能出现在哪类场景（IDE、CLI、聊天、配置、Web UI），减少人工规则编写。

3. 全模态端到端渲染。
同一类泄露语义可落地为图片、滚动视频、语音、PDF、Word、PPT，贴近企业真实传播路径。

4. 面向鲁棒性的增强策略。
可选噪声与压缩扰动用于模拟真实采集损伤，帮助评估 OCR 与视觉模型在复杂输入下的表现。

## 增量开发脉络

Deeptrace 是分阶段演进的，这一点对理解当前模块关系很关键：

1. 第一阶段：场景生成与视觉渲染。
早期能力集中在 LLM 场景构造和图像/视频输出。

2. 第二阶段：音频与文档扩展。
后续补齐音频、PDF、Word、PPT，覆盖更完整的企业泄露介质。

3. 第三阶段：密钥生成器后置接入。
密钥类与网络串类生成器是后续新增模块，作为上游秘密来源增强批量化能力。它不是最初主干，而是在原有管线上增量集成。

这也解释了为什么不同模块在接口成熟度上存在阶段性差异。

## 支持模态

1. Image：IDE/CLI/聊天/配置/UI 截图。
2. Video：基于视觉场景的平移或滚动视频。
3. Audio：包含秘密提及的语音样本。
4. PDF：正式文档风格泄露样本。
5. Word：备忘录与交接文档风格样本。
6. PPT：演示文稿风格样本。

## 项目结构

```text
.
├── main.py
├── llm_utils.py
├── config/
│   ├── config.json
│   └── config_sample.json
├── generators/
│   ├── secret_generators/
│   │   ├── Key_Gen.py
│   │   ├── NetworkStr_Gen.py
│   │   └── secret_gen.py
│   ├── audio_gen.py
│   ├── chat_gen.py
│   ├── cli_gen.py
│   ├── config_gen.py
│   ├── pdf_gen.py
│   ├── ppt_gen.py
│   ├── ui_gen.py
│   ├── video_utils.py
│   ├── vscode_gen.py
│   └── word_gen.py
├── output/
└── output_sample/
```

## 快速开始

### 1. 环境准备

- Python 3.8+
- Node.js 18+
- 可用的 LLM API Key

### 2. 安装依赖

```bash
pip install -r requirements.txt
sudo apt-get install -y espeak-ng
```

### 3. 配置运行参数

参考 `config/config_sample.json` 创建或编辑 `config/config.json`。

关键字段：
- `api_key`：LLM API 密钥
- `base_url`：LLM API 地址
- `output_dir`：输出目录
- `add_noise`：是否加入图像噪声
- `items`：任务列表（`secret`、`secret_type`、`modality`、可选 `scene`）

### 4. 运行生成器

```bash
python main.py
python main.py --config config/config_sample.json
```

### 5. 启动后端（可选 Web 流程）

```bash
cd backend
pip install -r requirements.txt
python main.py
```

后端接口：
- Swagger UI：http://localhost:8000/docs
- ReDoc：http://localhost:8000/redoc

### 6. 启动前端（可选 Web 流程）

```bash
cd frontend
npm install
npm run dev
```

前端地址：http://localhost:3000

常见 Web 使用流程：
1. 注册并登录。
2. 在仪表板创建任务。
3. 配置密钥类型、模态与场景。
4. 提交任务并查看输出结果。

## 生成流程

1. 分析 `secret_type` 与 `modality`。
2. 对图像/视频任务选择或推断场景。
3. 生成包含秘密的上下文内容。
4. 由对应模态生成器完成渲染。

## 密钥生成器（增量模块）

密钥生成器在项目后期接入，当前可独立复用。

- 密钥类接口：
  - `Keygen(modeset: int) -> str`
  - `RandKeygen() -> str`
- 网络串接口：
  - `Strgen(modeset: int) -> str`
  - `RandStrgen() -> str`
- 外层封装：
  - `AllRandgen() -> str`

支持的枚举类型与格式细节请查看 `generators/secret_generators/` 下源码。

## 文档说明

为减少文档分散，原独立的 Pitch 与 Use 文档已融合到本 README。