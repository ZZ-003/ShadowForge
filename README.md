# Universe Gen Scripts (Multimodal Secret Leak Generator)

这是一个多模态秘密泄露场景生成工具，旨在生成包含敏感信息（如 API Key、数据库连接串等）的各种格式文件，用于安全测试、数据集构建或演示。

该工具利用大语言模型（LLM）辅助生成逼真的场景内容，并将其渲染为图片、视频、音频、PDF、Word 或 PPT 等多种模态。

## 项目意义与创新点

### 1. 核心价值 (Significance)
*   **填补多模态安全测试空白**: 传统的敏感信息检测（DLP）工具主要针对文本扫描。本项目扩展到了图片（截图）、视频（录屏）、音频（会议录音）及各类办公文档，覆盖了现代企业中更隐蔽的泄露渠道。
*   **构建高质量训练数据**: 为训练基于视觉或多模态的泄密检测模型提供大规模、高逼真度的合成数据，解决了真实泄露样本稀缺且难以收集的问题。
*   **提升红蓝对抗真实性**: 在红队演练或安全意识培训中，能够生成高度可信的“伪造”泄露场景（如误发群的密钥截图、演示视频中的 Token），显著提升演练的实战价值。

### 2. 技术创新 (Innovations)
*   **LLM 驱动的上下文感知生成**:
    *   利用大模型理解秘密类型（如 `AWS Access Key`），自动生成符合逻辑的代码片段、配置文件或对话上下文，而非简单的字符串拼接，使得泄露场景在语义上连贯、逼真。
*   **智能场景路由与自适应**:
    *   内置场景分析模块，自动判断某类秘密最可能出现的场景（例如：数据库连接串 -> 配置文件截图；临时 Token -> 聊天记录截图），无需人工指定。
*   **全模态渲染管线**:
    *   支持从文本到 IDE 截图、CLI 录屏、语音合成、PDF/Word/PPT 文档的自动化渲染，并支持为图像注入噪声以模拟真实截图的压缩损伤，用于评估 OCR 及视觉模型的鲁棒性。

## 项目结构

```
universe_gen_scripts/
├── main.py              # 主入口脚本，负责调度和流程控制
├── llm_utils.py         # LLM 交互模块，负责场景分析 (Scenario Analysis) 和内容生成 (Content Generation)
├── config/
│   ├── config.json      # 实际运行配置（脚本读取此文件）
│   └── config_sample.json # 配置模板
├── generators/          # 各模态的具体生成器模块
│   ├── secret_generators
│       ├── Key_gen.py   #生成伪造的平台连接密钥 
│       ├── secret_gen.py #生成器封装部分，为两类生成提供简单外部接口
│       └── NetworkStr_Gen.py #生成数据库等访问链接
│   ├── __init__.py
│   ├── vscode_gen.py    # 生成 IDE 代码截图 (Python/JS/Java)
│   ├── cli_gen.py       # 生成终端命令行截图
│   ├── chat_gen.py      # 生成团队聊天记录截图
│   ├── config_gen.py    # 生成配置文件截图 (YAML/INI/.env)
│   ├── ui_gen.py        # 生成 Web UI 截图 (Dashboard/Console/JSON)
│   ├── video_utils.py   # 视频生成工具，用于将图片转换为平移/滚动的视频
│   ├── audio_gen.py     # 生成音频文件 (MP3/WAV)，支持在线(gTTS)和离线(espeak)
│   ├── pdf_gen.py       # 生成 PDF 文档
│   ├── word_gen.py      # 生成 Word (.docx) 文档
│   └── ppt_gen.py       # 生成 PPT (.pptx) 演示文稿
├── output_sample/     # 样例输出目录
└── output/     # 默认输出目录

```

## 功能特性

支持以下 6 种模态生成：

1.  **Image (图片)**:
    *   自动根据秘密类型选择最合适的场景（IDE 代码、CLI 终端、Chat 聊天、Config 配置、Web UI）。
    *   生成高分辨率 PNG 图片。
2.  **Video (视频)**:
    *   基于生成的长图，创建平移/滚动的 MP4 视频，模拟用户在屏幕上浏览的效果。
3.  **Audio (音频)**:
    *   生成朗读秘密或在会议中提及秘密的语音文件。
    *   优先使用 Google TTS (在线)，网络不通时自动降级为 System TTS (离线 WAV)。
4.  **PDF (文档)**:
    *   生成包含秘密的正式 PDF 文档（如发票、合同、技术手册）。
5.  **Word (文档)**:
    *   生成包含秘密的 Word 文档（如内部备忘录、交接文档）。
6.  **PPT (演示文稿)**:
    *   生成包含秘密的 PowerPoint 幻灯片。

## 安装依赖

请确保安装了以下 Python 库及系统依赖：

```bash
# Python 依赖
pip install openai pillow opencv-python numpy gtts pyttsx3 reportlab python-docx python-pptx requests sshkey-tools

# 系统依赖 (Linux)
# 用于离线音频生成
sudo apt-get install -y espeak-ng 
```

## 使用方法

### 1. 准备配置文件 (`config/config.json`)

先参考 `config/config_sample.json`，再编辑 `config/config.json`。
配置字段如下：

*   `api_key`：大模型 API Key
*   `base_url`：大模型 API Base URL
*   `output_dir`：输出目录
*   `add_noise`：是否为图片场景加入轻微噪声
*   `items`：待生成样本列表（每项包含 `secret`、`secret_type`、`modality`、`scene`[可选]）

```json
{
  "api_key": "YOUR_LLM_API_KEY",
  "base_url": "YOUR_LLM_BASE_URL",
  "output_dir": "output_universe",
  "add_noise": false,
  "items": [
    {
      "secret": "sk-proj-123456",
      "secret_type": "OpenAI API Key",
      "modality": "image",
      "scene": "chat" 
    },
    {
      "secret": "postgres://user:pass@db:5432",
      "secret_type": "Database Connection String",
      "modality": "video"
    },
    {
      "secret": "ghp_secret_token",
      "secret_type": "GitHub Token",
      "modality": "audio"
    },
    {
      "secret": "AKIAIOSFODNN7EXAMPLE",
      "secret_type": "AWS Access Key",
      "modality": "pdf"
    }
  ]
}
```

### 2. 运行生成脚本

```bash
python main.py

# 或者指定其他配置路径
python main.py --config config/config_sample.json

```

*   `--config`: 配置文件路径，默认为 `config/config.json`。

## 生成逻辑说明

1.  **分析阶段**: 脚本首先将 `secret_type` 发送给 LLM。
    *   如果是 `image` 或 `video` 模态：
        *   若 `config` 中指定了 `scene` (可选值: `ide`, `cli`, `chat`, `config`, `ui`)，则直接使用该场景。
        *   若未指定 `scene`，LLM 会判断该秘密最可能出现在哪种视觉场景。
    *   如果是 `audio`, `pdf`, `word`, `ppt`，则直接使用对应的生成器。
2.  **内容生成**: LLM 生成逼真的填充内容（代码片段、对话记录、文档正文等），并将秘密嵌入其中。
3.  **渲染阶段**: 调用对应的生成器模块将文本内容渲染为最终文件。


## 后续补充
1. 图片噪声可配置
通过 `config/config.json` 中的 `add_noise` 字段控制是否为图片场景添加轻微噪声；
2. LLM 内容生成篇幅限制
在向 LLM 发送生成请求时，增加了对上下文篇幅的严格限制，确保生成的内容长度维持在密钥（Secret）长度的 2-3 倍 左右。


## 关于秘密生成器
接口请使用/generator/secret_generator/secret_gen.py中所述
Keygen()为密钥生成器接口
Strgen()为链接串生成器接口
以上两者均使用唯一输入modeset:int指示目标类型
三种Rand接口无输入参数
RandKeygen() ~
RandStrgen() ~
AllRandgen   -生成器类型和目标类型全随机
支持目标类型见/config/key_sample.json
所属生成器类型见secret_generator目录下_Gen后缀python文件内枚举类