# DocFlow

<div align="center">

![DocFlow Logo](docs/images/logo.png)

**High-performance document conversion and intelligent processing engine**

[![PyPI version](https://badge.fury.io/py/docflow.svg)](https://badge.fury.io/py/docflow)
[![Python Support](https://img.shields.io/pypi/pyversions/docflow.svg)](https://pypi.org/project/docflow/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

[English](#english) | [简体中文](#简体中文) | [繁體中文](#繁體中文)

</div>

---

<a name="english"></a>

## 🎉 Introduction

**DocFlow** is a powerful command-line tool for converting various document formats to Markdown. It supports batch processing, OCR, metadata extraction, and AI-powered enhancements.

### ✨ Key Features

- **Multi-format Support**: PDF, Word, PowerPoint, Excel, HTML, Images, CSV, JSON, XML
- **Batch Processing**: Convert entire directories with parallel processing
- **OCR Support**: Extract text from images and scanned PDFs
- **Metadata Extraction**: Preserve document metadata during conversion
- **Image Extraction**: Extract and reference embedded images
- **AI Enhancement**: Optional AI-powered summarization and keyword extraction
- **Table Support**: Convert tables to Markdown format
- **Quality Reports**: Generate conversion quality assessments

### 🚀 Quick Start

#### Installation

```bash
# Using pip
pip install docflow

# With OCR support
pip install docflow[ocr]

# With AI features
pip install docflow[ai]

# Full installation
pip install docflow[all]
```

#### Basic Usage

```bash
# Convert a single file
docflow convert document.pdf

# Convert with custom output
docflow convert document.docx -o output.md

# Batch convert a directory
docflow convert ./documents -o ./markdown

# Enable OCR for scanned documents
docflow convert scan.pdf --enable-ocr --ocr-language eng+chi_sim

# Convert recursively
docflow batch ./docs -r -o ./output
```

### 📖 Detailed Usage Guide

#### Convert Command

```bash
docflow convert <source> [options]
```

| Option | Description |
|--------|-------------|
| `-o, --output` | Output file or directory |
| `--extract-images` | Extract images from documents |
| `--enable-ocr` | Enable OCR for images |
| `--ocr-language` | OCR language (default: eng) |
| `--include-metadata` | Include metadata in output |
| `--overwrite` | Overwrite existing files |

#### Batch Command

```bash
docflow batch <source> [options]
```

| Option | Description |
|--------|-------------|
| `-r, --recursive` | Process directories recursively |
| `-p, --pattern` | File pattern to match (default: *) |
| `-o, --output-dir` | Output directory |
| `-w, --workers` | Number of parallel workers |
| `--enable-ocr` | Enable OCR |
| `--overwrite` | Overwrite existing files |

#### Other Commands

```bash
# List supported formats
docflow formats

# Display document information
docflow info document.pdf
```

### 💡 Design Philosophy

DocFlow is designed with the following principles:

1. **Zero-dependency Core**: Minimal dependencies for basic functionality
2. **Extensible Architecture**: Easy to add new converters
3. **Quality First**: Accurate conversion over speed
4. **Developer Friendly**: Clean API for programmatic use

### 📦 Deployment

#### Docker

```dockerfile
FROM python:3.11-slim
RUN pip install docflow
ENTRYPOINT ["docflow"]
```

```bash
docker build -t docflow .
docker run -v $(pwd)/docs:/docs docflow convert /docs/input.pdf
```

#### PyInstaller (Standalone Executable)

```bash
pip install pyinstaller
pyinstaller --onefile --name docflow docflow/cli/main.py
```

### 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'feat: add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<a name="简体中文"></a>

## 🎉 项目介绍

**DocFlow** 是一个强大的命令行工具，用于将各种文档格式转换为 Markdown。支持批量处理、OCR、元数据提取和 AI 增强功能。

### ✨ 核心特性

- **多格式支持**：PDF、Word、PowerPoint、Excel、HTML、图片、CSV、JSON、XML
- **批量处理**：并行处理整个目录
- **OCR 支持**：从图片和扫描 PDF 中提取文字
- **元数据提取**：保留文档元数据
- **图片提取**：提取并引用嵌入的图片
- **AI 增强**：可选的 AI 摘要和关键词提取
- **表格支持**：将表格转换为 Markdown 格式
- **质量报告**：生成转换质量评估

### 🚀 快速开始

#### 安装

```bash
# 使用 pip
pip install docflow

# 带 OCR 支持
pip install docflow[ocr]

# 带 AI 功能
pip install docflow[ai]

# 完整安装
pip install docflow[all]
```

#### 基本用法

```bash
# 转换单个文件
docflow convert document.pdf

# 指定输出路径
docflow convert document.docx -o output.md

# 批量转换目录
docflow convert ./documents -o ./markdown

# 启用 OCR（扫描文档）
docflow convert scan.pdf --enable-ocr --ocr-language eng+chi_sim

# 递归转换
docflow batch ./docs -r -o ./output
```

### 📖 详细使用指南

#### convert 命令

```bash
docflow convert <source> [options]
```

| 选项 | 说明 |
|------|------|
| `-o, --output` | 输出文件或目录 |
| `--extract-images` | 从文档中提取图片 |
| `--enable-ocr` | 启用图片 OCR |
| `--ocr-language` | OCR 语言（默认：eng）|
| `--include-metadata` | 在输出中包含元数据 |
| `--overwrite` | 覆盖已存在的文件 |

#### batch 命令

```bash
docflow batch <source> [options]
```

| 选项 | 说明 |
|------|------|
| `-r, --recursive` | 递归处理目录 |
| `-p, --pattern` | 文件匹配模式（默认：*）|
| `-o, --output-dir` | 输出目录 |
| `-w, --workers` | 并行工作进程数 |
| `--enable-ocr` | 启用 OCR |
| `--overwrite` | 覆盖已存在的文件 |

#### 其他命令

```bash
# 列出支持的格式
docflow formats

# 显示文档信息
docflow info document.pdf
```

### 💡 设计思路

DocFlow 的设计原则：

1. **核心零依赖**：基本功能无需额外依赖
2. **可扩展架构**：易于添加新的转换器
3. **质量优先**：准确性优于速度
4. **开发者友好**：清晰的 API 便于编程使用

### 📦 打包与部署

#### Docker

```dockerfile
FROM python:3.11-slim
RUN pip install docflow
ENTRYPOINT ["docflow"]
```

```bash
docker build -t docflow .
docker run -v $(pwd)/docs:/docs docflow convert /docs/input.pdf
```

#### PyInstaller（独立可执行文件）

```bash
pip install pyinstaller
pyinstaller --onefile --name docflow docflow/cli/main.py
```

### 🤝 贡献指南

欢迎参与贡献！详情请参阅 [CONTRIBUTING.md](CONTRIBUTING.md)。

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'feat: add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 提交 Pull Request

### 📄 开源协议

本项目采用 MIT 协议开源 - 详见 [LICENSE](LICENSE) 文件。

---

<a name="繁體中文"></a>

## 🎉 專案介紹

**DocFlow** 是一個強大的命令列工具，用於將各種文件格式轉換為 Markdown。支援批次處理、OCR、元資料提取和 AI 增強功能。

### ✨ 核心特性

- **多格式支援**：PDF、Word、PowerPoint、Excel、HTML、圖片、CSV、JSON、XML
- **批次處理**：平行處理整個目錄
- **OCR 支援**：從圖片和掃描 PDF 中提取文字
- **元資料提取**：保留文件元資料
- **圖片提取**：提取並引用嵌入的圖片
- **AI 增強**：可選的 AI 摘要和關鍵字提取
- **表格支援**：將表格轉換為 Markdown 格式
- **品質報告**：產生轉換品質評估

### 🚀 快速開始

#### 安裝

```bash
# 使用 pip
pip install docflow

# 完整安裝
pip install docflow[all]
```

#### 基本用法

```bash
# 轉換單一檔案
docflow convert document.pdf

# 批次轉換目錄
docflow convert ./documents -o ./markdown
```

### 📄 授權條款

本專案採用 MIT 授權條款 - 詳見 [LICENSE](LICENSE) 檔案。

---

## 📊 Supported Formats

| Format | Extension | Features |
|--------|-----------|----------|
| PDF | `.pdf` | Text, Tables, Images, OCR |
| Word | `.docx`, `.doc` | Text, Tables, Images |
| PowerPoint | `.pptx`, `.ppt` | Slides, Tables, Text |
| Excel | `.xlsx`, `.xls` | Sheets, Tables |
| HTML | `.html`, `.htm` | Full content |
| Text | `.txt`, `.md` | Direct conversion |
| CSV/TSV | `.csv`, `.tsv` | Table conversion |
| JSON/XML | `.json`, `.xml` | Code blocks |
| Images | `.png`, `.jpg`, etc. | OCR, Metadata |

## 🗺️ Roadmap

- [ ] Web UI interface
- [ ] Cloud storage integration
- [ ] More AI providers support
- [ ] Custom template system
- [ ] Real-time collaboration

---

<div align="center">

**Made with ❤️ by DocFlow Team**

</div>
