# Deeptrace

[English](README.md) | [中文](README.zh-CN.md)

Deeptrace is a multimodal sensitive-data leak simulation engine that generates realistic synthetic leak artifacts across image, video, audio, and document channels.

The project is designed for security testing, DLP model training, red-team exercises, and awareness programs where real leaked data is either unavailable or too risky to use.

## Pitch Narrative

### The blind spot
Modern leak incidents are no longer text-only. In practice, secrets leak through screenshots, recordings, meetings, and office documents. Traditional DLP coverage is often insufficient for these channels.

### The solution
Deeptrace simulates realistic leak trajectories end to end. Instead of randomly inserting secret strings, it uses LLM-driven contextual generation to place secrets into coherent host environments, then renders them into multimodal artifacts.

### Practical value
1. DLP cold start: generate large synthetic datasets without exposing production secrets.
2. Red/blue exercises: produce believable honey artifacts for adversary engagement.
3. Security awareness: create immersive leak examples for internal training.

### Vision
Simulating the unseen, to trace the unknown.

## Why Deeptrace Matters

1. Multimodal coverage instead of text-only assumptions.
Traditional DLP workflows mostly focus on text logs. Real incidents often happen through screenshots, recordings, shared slides, and meeting audio. Deeptrace fills that practical gap.

2. Safe synthetic data for model training.
High-quality leak datasets are hard to collect because real secrets are regulated and dangerous to circulate. Deeptrace produces high-fidelity synthetic samples without exposing production credentials.

3. Better realism for offensive and defensive drills.
Security exercises become more actionable when bait files and leak traces look operationally authentic.

## Core Innovations

1. LLM-based contextual generation.
Deeptrace does not only paste a secret string into random text. It generates semantically coherent host context such as code snippets, config fragments, chat logs, and business documents.

2. Adaptive scene routing.
For visual modalities, the system can infer where a secret is most likely to appear (IDE, CLI, chat, config, UI), reducing manual rule authoring.

3. End-to-end multimodal rendering pipeline.
The same scenario can be rendered into static images, scrolling videos, speech, PDF, Word, and PPT outputs to emulate real-world leakage surfaces.

4. Robustness-oriented augmentation.
Optional noise and compression-like perturbations help evaluate OCR and vision models under imperfect capture conditions.

## Incremental Development Story

Deeptrace is intentionally built in layers, and this evolution is important to understand the current architecture:

1. Phase 1: Scenario generation and visual rendering.
The initial version focused on LLM-driven scene synthesis and image/video outputs.

2. Phase 2: Audio and document modalities.
Audio, PDF, Word, and PPT generators were added to cover broader enterprise leakage channels.

3. Phase 3: Secret generator module (added later).
The key and network-string generator was introduced as a later enhancement to support scalable synthetic secret creation. This module is an incremental extension, not the original core, and is now integrated as an optional upstream source for scenario payloads.

This staged growth explains why some modules look more mature than others and why interfaces evolved over time.

## Supported Modalities

1. Image: IDE/CLI/chat/config/UI screenshots.
2. Video: Pan/scroll videos generated from visual scenes.
3. Audio: Secret mention simulation via TTS.
4. PDF: Formal leak-like document artifacts.
5. Word: Internal memo and handoff style documents.
6. PPT: Presentation-style sensitive content artifacts.

## Project Structure

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

## Quick Start

### 1. Environment

- Python 3.8+
- Node.js 18+
- LLM API key

### 2. Install dependencies

```bash
pip install -r requirements.txt
sudo apt-get install -y espeak-ng
```

### 3. Configure runtime

Create or edit `config/config.json` based on `config/config_sample.json`.

Key fields:
- `api_key`: LLM API key
- `base_url`: LLM API endpoint
- `output_dir`: output folder
- `add_noise`: whether to add visual noise
- `items`: generation list (`secret`, `secret_type`, `modality`, optional `scene`)

### 4. Run generator

```bash
python main.py
python main.py --config config/config_sample.json
```

### 5. Run backend (optional web workflow)

```bash
cd backend
pip install -r requirements.txt
python main.py
```

Backend endpoints:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 6. Run frontend (optional web workflow)

```bash
cd frontend
npm install
npm run dev
```

Frontend: http://localhost:3000

Typical web flow:
1. Register and log in.
2. Create a task from dashboard.
3. Configure secret type, modality, and scene.
4. Submit task and review outputs.

## Generation Flow

1. Analyze `secret_type` and modality.
2. Select or infer scene for image/video tasks.
3. Generate context-rich content with embedded secret.
4. Render with the modality-specific generator.

## Secret Generator (Incremental Module)

The secret generator was added after the initial multimodal pipeline and is now available as a reusable component.

- Key generator APIs:
    - `Keygen(modeset: int) -> str`
    - `RandKeygen() -> str`
- Network string APIs:
    - `Strgen(modeset: int) -> str`
    - `RandStrgen() -> str`
- Unified wrapper:
    - `AllRandgen() -> str`

See source files under `generators/secret_generators/` for supported enum types and format constraints.

## Documentation Note

To keep docs maintainable, previous standalone pitch and usage docs are merged into this README.