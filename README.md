# 跨文化智能翻译助手 / Cross-Cultural Translation Assistant

一个基于 Deepseek AI 的智能翻译工具，提供直译、自然表达和文化建议。支持中文、英文、日文之间的互译，并提供语音输入和语音朗读功能。

An intelligent translation tool powered by Deepseek AI, providing literal translation, natural expressions, and cultural advice. Supports translation between Chinese, English, and Japanese with voice input and text-to-speech features.

---

## ✨ 功能特性 / Features

- 🌍 **多语言支持**：中文 ↔ 英文 ↔ 日文
- 📝 **三种翻译输出**：
  - 直译（Literal Translation）
  - 自然表达（Natural Expressions）
  - 文化建议（Cultural Advice）
- 🎤 **语音输入**：支持麦克风语音识别（在线/离线）
- 🔊 **语音朗读**：基于浏览器的 TTS（文本转语音）
- 🎭 **场景化翻译**：旅游、餐饮、闲聊、商务等场景
- 💬 **语气调节**：随和、中性、正式/礼貌
- 🌐 **多语言界面**：中文/English/日本語

---

## 🚀 快速开始 / Quick Start

### 1. 环境要求 / Prerequisites

- **Python 3.8+**（✅ 现已支持 Python 3.13+）
- pip（Python 包管理器）
- 麦克风（可选，用于语音输入）
- 现代浏览器（Chrome/Edge/Firefox，用于浏览器语音输入）

> **✅ Python 3.13+ 兼容性**：
> - 应用已更新以支持 Python 3.13+
> - 在 Python 3.13+ 上，麦克风录音功能不可用（因 `aifc` 模块被移除）
> - **替代方案**：使用浏览器原生语音输入（Web Speech API），功能完全相同
> - Python 3.8-3.12 用户可使用两种语音输入方式：浏览器语音 + 麦克风录音

### 2. 安装步骤 / Installation

```bash
# 检查 Python 版本
python --version

# 克隆或下载项目
cd E:\TRANSLATION_AI

# 创建虚拟环境（推荐）
python -m venv .venv

# 激活虚拟环境
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# === Python 3.8-3.12 用户（可选）===
# 如果需要麦克风录音功能，安装 PyAudio
# Windows: 从 https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio 下载 whl
pip install PyAudio-0.2.11-cp3XX-cp3XX-win_amd64.whl

# 离线语音识别（可选）
pip install vosk

# === Python 3.13+ 用户 ===
# 无需额外安装，直接使用浏览器语音输入功能
```

### 3. 配置 API 密钥 / Configure API Key

**方法 1：使用配置文件（推荐）**

复制示例配置文件并编辑：

```bash
cp credentials.example.json credentials.json
```

编辑 `credentials.json`，填入你的 Deepseek API Token：

```json
{
  "tokens": [
    {
      "name": "deepseek-main",
      "token": "YOUR_ACTUAL_TOKEN_HERE",
      "api_url": "https://api.deepseek.com"
    }
  ],
  "default": "deepseek-main"
}
```

**方法 2：使用环境变量**

```bash
# Windows (CMD)
set DEEPSEEK_API_KEY=your_token_here

# Windows (PowerShell)
$env:DEEPSEEK_API_KEY="your_token_here"

# Linux/Mac
export DEEPSEEK_API_KEY=your_token_here
```

**获取 Deepseek API Token**：
访问 [https://platform.deepseek.com/](https://platform.deepseek.com/) 注册并获取 API 密钥。

### 4. 运行应用 / Run the Application

```bash
streamlit run app.py
```

应用将自动在浏览器中打开（默认地址：`http://localhost:8501`）

---

## 📖 使用指南 / User Guide

### 基本使用流程

1. **选择界面语言**：在侧边栏选择中文/English/日本語
2. **选择源语言和目标语言**
3. **输入文本**：
   - 手动输入文本
   - 或点击 🎤 按钮使用**浏览器语音输入**（所有 Python 版本可用）
   - 或点击 🎙️ 按钮使用**麦克风录音**（仅 Python 3.8-3.12）
4. **选择场景和语气**
5. **点击"翻译并给出文化建议"按钮**
6. **查看结果**

### 语音功能说明

#### 🎤 浏览器语音输入（推荐，所有版本可用）

- **兼容性**：Python 3.8+ 包括 3.13+
- **工作原理**：使用浏览器内置的 Web Speech API
- **优点**：
  - 无需安装额外库
  - 实时识别，速度快
  - 支持多种语言
  - 在线识别，准确度高
- **使用方法**：
  1. 点击 🎤 按钮
  2. 允许浏览器访问麦克风（首次使用时）
  3. 开始说话
  4. 识别结果自动填入文本框
- **支持的浏览器**：
  - ✅ Chrome/Edge (最佳支持)
  - ✅ Safari
  - ⚠️ Firefox (部分支持)

#### 🎙️ 麦克风录音（仅 Python 3.8-3.12）

- **兼容性**：仅 Python 3.8-3.12
- **需要安装**：PyAudio + speech_recognition
- **工作原理**：后端录音并识别
- **优点**：
  - 支持 Google 在线识别
  - 支持 Vosk 离线识别
  - 可自定义识别参数
- **使用方法**：与原版相同

**离线语音识别配置（Vosk，可选）**

如果无法访问 Google 服务，可以设置 Vosk 离线识别：

1. 从 [https://alphacephei.com/vosk/models](https://alphacephei.com/vosk/models) 下载模型：
   - 中文：`vosk-model-small-cn-0.22`
   - 英文：`vosk-model-small-en-us-0.15`
   - 日文：`vosk-model-small-ja-0.22`

2. 在项目根目录创建 `models` 文件夹：
   ```
   E:\TRANSLATION_AI\
   ├── models\
   │   ├── zh\  (解压后的中文模型)
   │   ├── en\  (解压后的英文模型)
   │   └── ja\  (解压后的日文模型)
   ```

3. 解压下载的模型并重命名文件夹为 `zh`、`en` 或 `ja`

#### 🔊 语音朗读

- 使用浏览器内置的 Web Speech API
- 无需额外配置，点击按钮即可朗读
- 所有 Python 版本可用

---

## 🏗️ 项目结构 / Project Structure

```
E:\TRANSLATION_AI\
├── app.py                      # Streamlit 主应用
├── translator_core_new.py      # 翻译核心逻辑
├── requirements.txt            # Python 依赖
├── credentials.json            # API 配置（不提交到 Git）
├── credentials.example.json    # API 配置示例
├── .gitignore                  # Git 忽略文件
├── models/                     # Vosk 离线模型（可选）
│   ├── zh/
│   ├── en/
│   └── ja/
└── README.md                   # 项目说明
```

---

## 🧪 测试建议 / Testing Guide

### 基础功能测试

1. **文本翻译测试**
   ```
   输入（中文）："你好，请问洗手间在哪里？"
   源语言：中文 → 目标语言：英文
   场景：旅游
   ```

2. **浏览器语音输入测试（所有 Python 版本）**
   - 点击 🎤 按钮
   - 允许浏览器访问麦克风
   - 说话并观察识别结果

3. **麦克风录音测试（仅 Python 3.8-3.12）**
   - 点击 🎙️ 按钮
   - 确保 PyAudio 已安装
   - 观察识别结果

4. **语音朗读测试**
   - 翻译完成后点击 🔊 按钮
   - 检查浏览器音量设置

5. **多场景和语气测试**
   - 尝试不同组合
   - 对比输出差异

### Python 版本兼容性测试

**Python 3.13+ 用户**：
```bash
# 确认应用正常启动
streamlit run app.py

# 测试浏览器语音输入 🎤
# 确认麦克风录音按钮 🎙️ 显示为禁用状态
# 确认所有其他功能正常
```

**Python 3.8-3.12 用户**：
```bash
# 确认两种语音输入都可用
# 测试 🎤 浏览器语音输入
# 测试 🎙️ 麦克风录音
```

---

## 🔧 故障排除 / Troubleshooting

### ✅ Python 3.13+ 兼容性（已解决）

**状态**：应用已完全支持 Python 3.13+

**功能对比**：

| 功能 | Python 3.8-3.12 | Python 3.13+ |
|-----|----------------|--------------|
| 文本翻译 | ✅ | ✅ |
| 浏览器语音输入 🎤 | ✅ | ✅ |
| 麦克风录音 🎙️ | ✅ | ❌ (库不兼容) |
| 语音朗读 🔊 | ✅ | ✅ |
| Vosk 离线识别 | ✅ | ❌ |

**推荐方案**：
- 所有用户：优先使用 **🎤 浏览器语音输入**，功能完整且无需额外配置
- 需要离线语音识别：使用 Python 3.8-3.12 + Vosk

### 问题：浏览器语音输入无响应

**症状**：点击 🎤 按钮后没有反应

**解决方案**：
1. **检查浏览器兼容性**
   - 推荐使用 Chrome 或 Edge
   - Firefox 对 Web Speech API 支持有限
   
2. **检查麦克风权限**
   - 浏览器应提示允许麦克风访问
   - 检查浏览器设置 → 隐私 → 麦克风权限
   
3. **检查 HTTPS**
   - Web Speech API 在某些浏览器中要求 HTTPS
   - 本地开发（localhost）通常可用
   
4. **查看浏览器控制台**
   - 按 F12 打开开发者工具
   - 查看 Console 标签中的错误信息

### 问题：语音输入无响应（Python 3.8-3.12 麦克风录音）

**症状**：点击 🎙️ 按钮后没有反应

**解决方案**：
1. **检查 PyAudio 是否安装**
   ```bash
   pip show pyaudio
   ```
   - 如果未安装，参考安装步骤安装 PyAudio
   
2. **检查麦克风权限**
   - 确保系统和浏览器均已允许麦克风访问
   
3. **查看控制台错误信息**
   - 按 F12 打开开发者工具
   - 查看 Console 标签中的错误信息

### 问题：语音朗读没有声音
- 检查浏览器音量设置
- 尝试其他浏览器（Chrome/Edge 支持最好）
- 查看浏览器控制台 JavaScript 错误

### 问题：翻译返回错误信息
- 检查 `credentials.json` 中的 API Token 是否正确
- 确认网络可以访问 `https://api.deepseek.com`
- 查看 Deepseek API 配额是否用尽

### 问题：PyAudio 安装失败（Windows）

**仅适用于 Python 3.8-3.12 用户想使用麦克风录音功能**

**症状**：`pip install PyAudio` 报错，提示编译错误。

**解决方案**：
1. 访问 [https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio)
2. 下载与你的 Python 版本和系统架构匹配的 `.whl` 文件
   - `cp38` = Python 3.8
   - `cp39` = Python 3.9
   - `cp310` = Python 3.10
   - `cp311` = Python 3.11
   - `cp312` = Python 3.12
   - `win32` = 32位系统
   - `win_amd64` = 64位系统

3. 安装下载的文件：
   ```bash
   pip install 路径\到\PyAudio-0.2.11-cp311-cp311-win_amd64.whl
   ```

**确认 Python 版本和架构**：
```bash
python -c "import sys; print(f'Python {sys.version_info.major}.{sys.version_info.minor} ({sys.maxsize > 2**32 and \"64bit\" or \"32bit\"})')"
```

---

## 📝 技术栈 / Tech Stack

- **Frontend**: Streamlit (Python Web UI 框架)
- **AI Model**: Deepseek API (通过 OpenAI SDK)
- **Speech Recognition**: 
  - **浏览器语音输入**：Web Speech API (客户端，所有 Python 版本)
  - **麦克风录音**：Google Speech Recognition (Python 3.8-3.12)
  - **离线识别**：Vosk (Python 3.8-3.12，可选)
- **Text-to-Speech**: Browser Web Speech API
- **Languages**: Python 3.8+ (✅ 包括 3.13+)

---

## 💡 开发路线图 / Roadmap

- [x] ~~等待 `speech_recognition` 支持 Python 3.13+~~ ✅ 已通过浏览器 API 解决
- [x] Python 3.13+ 完全兼容 ✅
- [ ] 添加更多语言支持
- [ ] 优化语音识别准确度
- [ ] 添加历史记录功能
- [ ] 支持批量翻译
- [ ] PWA 支持（Progressive Web App）

---

## 🤝 贡献 / Contributing

欢迎提交 Issue 和 Pull Request！

---

## 📄 许可证 / License

本项目仅供学习和研究使用。

---

## 📮 联系方式 / Contact

如有问题或建议，请通过 GitHub Issues 联系。

---

**Enjoy translating! 🎉**
