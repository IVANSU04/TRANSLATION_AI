# 跨文化智能翻译助手 - 桌面版

基于 Qt 的桌面应用程序，不依赖浏览器，提供原生 GUI 体验。
**使用 Vosk 进行免费的离线语音识别！**

---

## ⚠️ 首次运行前必读

**桌面版需要额外安装 GUI 依赖！**

```bash
# 1. 激活虚拟环境（如果还没激活）
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# 2. 安装 GUI 依赖（Python 3.13+ 使用 PySide6 6.8+）
pip install PySide6>=6.8.0 pyttsx3==2.90

# 3. 安装免费的语音识别库 Vosk
pip install vosk

# 4. 安装 PyAudio（麦克风支持）
# Windows: 下载 whl 文件
pip install PyAudio-0.2.11-cp3XX-cp3XX-win_amd64.whl
# Linux:
sudo apt-get install portaudio19-dev python3-pyaudio
pip install pyaudio
# macOS:
brew install portaudio
pip install pyaudio

# 5. 下载 Vosk 语音模型（免费）
# 访问: https://alphacephei.com/vosk/models
# 下载小型模型并解压到 models/ 文件夹
```

---

## ✨ 功能特性

- 🖥️ **原生桌面应用**：不依赖浏览器，独立运行
- 🎨 **现代化界面**：清晰的布局，选项卡式结果展示
- 🎤 **免费语音输入**：使用 Vosk 进行完全离线的语音识别
- 🔊 **离线语音朗读**：使用 pyttsx3 进行离线 TTS
- 📊 **实时状态**：显示 Python 版本和功能可用性
- ⚡ **异步处理**：后台翻译，不阻塞界面
- 💰 **完全免费**：所有功能均使用开源免费库

---

## 🚀 快速开始

### 1. 安装依赖

```bash
# 激活虚拟环境
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# 安装 GUI 框架
pip install PySide6>=6.8.0

# 安装语音相关库
pip install pyttsx3==2.90 vosk>=0.3.45

# 安装 PyAudio（麦克风支持）
# 详见上方"首次运行前必读"
```

### 2. 下载 Vosk 语音模型（免费）

**Vosk 是完全免费和开源的语音识别引擎！**

访问 [https://alphacephei.com/vosk/models](https://alphacephei.com/vosk/models)

推荐下载小型模型：

| 语言 | 模型名称 | 大小 | 下载 |
|-----|---------|------|------|
| 中文 | vosk-model-small-cn-0.22 | ~42 MB | [下载](https://alphacephei.com/vosk/models/vosk-model-small-cn-0.22.zip) |
| 英文 | vosk-model-small-en-us-0.15 | ~40 MB | [下载](https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip) |
| 日文 | vosk-model-small-ja-0.22 | ~48 MB | [下载](https://alphacephei.com/vosk/models/vosk-model-small-ja-0.22.zip) |

**安装步骤：**

```bash
# 1. 在项目根目录创建 models 文件夹
mkdir models

# 2. 下载对应语言的模型（选择小型模型即可）
# 3. 解压模型文件
# 4. 重命名解压后的文件夹为 zh、en 或 ja

# 最终目录结构：
E:\TRANSLATION_AI\
├── models\
│   ├── zh\          # 中文模型（解压后的内容）
│   │   ├── am\
│   │   ├── conf\
│   │   └── graph\
│   ├── en\          # 英文模型
│   └── ja\          # 日文模型
```

**Windows 快速命令：**

```bash
# 假设你已下载 vosk-model-small-cn-0.22.zip 到 Downloads
cd E:\TRANSLATION_AI
mkdir models
cd models
# 解压（使用 7-Zip 或 WinRAR）
# 然后重命名文件夹
ren vosk-model-small-cn-0.22 zh
```

### 3. 配置 API 密钥

与 Web 版相同，配置 `credentials.json` 文件：

```json
{
  "tokens": [
    {
      "name": "deepseek-main",
      "token": "YOUR_TOKEN_HERE",
      "api_url": "https://api.deepseek.com"
    }
  ],
  "default": "deepseek-main"
}
```

### 4. 运行桌面应用

```bash
python app_gui.py
```

---

## 📖 使用指南

### 界面布局

```
┌─────────────────────────────────────────────────────────────┐
│  翻译设置                                                     │
│  源语言: [中文▼] → 目标语言: [英文▼]  场景: [旅游▼]  语气: [中性▼] │
├────────────────────┬────────────────────────────────────────┤
│  输入文本          │  📝 直译 | 💬 自然表达 | 🌏 文化建议    │
│                    │                                        │
│  [文本输入框]      │  [结果显示区]                          │
│                    │                                        │
│  🎤语音  🗑️清空   │  🔊 朗读                                │
│  🌐 翻译并给出文化建议                                        │
├────────────────────┴────────────────────────────────────────┤
│  Python 3.11.9 | 语音输入✓ | 语音朗读✓                       │
└─────────────────────────────────────────────────────────────┘
```

### 基本操作

1. **设置参数**
   - 在顶部选择源语言、目标语言、场景和语气

2. **输入文本**
   - 方式 1：直接在输入框中输入或粘贴文本
   - 方式 2：点击 🎤 按钮进行语音输入

3. **开始翻译**
   - 点击 "🌐 翻译并给出文化建议" 按钮
   - 等待后台处理完成

4. **查看结果**
   - 切换选项卡查看不同类型的翻译结果
   - 📝 直译：逐字翻译结果
   - 💬 自然表达：多个地道的表达方式
   - 🌏 文化建议：深入的文化背景分析

5. **语音朗读**
   - 在直译或自然表达选项卡中点击 🔊 按钮
   - 系统将朗读当前显示的文本

### 语音输入（Vosk）

**Vosk 特点：**
- ✅ 完全免费和开源
- ✅ 100% 离线工作，无需网络
- ✅ 支持多种语言
- ✅ 准确度高（商业级别）
- ✅ 轻量级，小型模型仅 40-50 MB
- ✅ 跨平台（Windows/Linux/macOS）
- ✅ 兼容所有 Python 版本（包括 3.13+）

**使用步骤：**

1. 确保已下载对应语言的 Vosk 模型
2. 点击 "🎤 Vosk 语音输入" 按钮
3. 允许应用访问麦克风（首次使用时）
4. 开始说话
5. 应用会实时显示识别进度
6. 停止说话 3 秒后自动完成识别
7. 识别结果自动填入文本框

**提示：**
- 首次加载模型需要 1-2 秒
- 后续使用会更快
- 支持长时间连续识别
- 完全本地处理，保护隐私

---

## 🔧 功能对比

| 功能 | Web 版 (app.py) | 桌面版 (app_gui.py) |
|-----|----------------|-------------------|
| 运行方式 | 浏览器 | 独立桌面应用 |
| 依赖库 | Streamlit | PyQt6 |
| 文本翻译 | ✅ | ✅ |
| 语音输入 | ✅ (浏览器/麦克风) | ✅ (麦克风) |
| 语音朗读 | ✅ (浏览器 API) | ✅ (pyttsx3 离线) |
| 离线使用 | ❌ (需浏览器) | ✅ (完全离线) |
| 界面美观度 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 启动速度 | 慢 | 快 |
| 资源占用 | 高 | 中 |

---

## 🎯 推荐使用场景

### 选择桌面版 (app_gui.py)

- ✅ 需要离线使用
- ✅ 不想占用浏览器资源
- ✅ 喜欢原生应用体验
- ✅ 需要快速启动
- ✅ 在企业内网环境使用

### 选择 Web 版 (app.py)

- ✅ 需要远程访问
- ✅ 跨平台兼容性优先
- ✅ 希望浏览器语音功能
- ✅ 已熟悉 Streamlit 界面
- ✅ 需要分享给他人使用（局域网）

---

## ⚙️ 依赖说明

### 必需依赖

```bash
# Python 3.13+
PySide6>=6.8.0        # Qt 框架（官方推荐）
openai==1.30.0        # Deepseek API 客户端
pyttsx3==2.90         # 离线 TTS
```

### 语音功能依赖（免费）

```bash
vosk>=0.3.45          # 免费离线语音识别
pyaudio               # 麦克风支持
```

**所有依赖都是免费和开源的！**

---

## 🔧 故障排除

### ⚠️ 问题：Vosk 模型未找到

**症状**：点击语音输入后提示"语音模型未找到"

**解决方案**：

```bash
# 1. 检查模型文件夹是否存在
dir models\zh  # Windows
ls models/zh   # Linux/Mac

# 2. 如果不存在，下载并解压模型
# 访问: https://alphacephei.com/vosk/models

# 3. 确保文件夹结构正确
# models/zh/ 应该包含 am/, conf/, graph/ 子文件夹
```

### ⚠️ 问题：PyAudio 安装失败

**解决方案**：

- 确保已安装正确版本的 whl 文件
- Windows 用户请下载与 Python 版本匹配的 whl 文件
- Linux 用户请确保已安装 portaudio19-dev

```bash
# Windows 示例
pip install PyAudio-0.2.11-cp39-cp39-win_amd64.whl

# Linux 示例
sudo apt-get install portaudio19-dev python3-pyaudio
pip install pyaudio
```

### ⚠️ 问题：语音朗读无声音

**原因**：pyttsx3 未安装或系统 TTS 引擎问题

**解决方案**：
```bash
# 安装 pyttsx3
pip install pyttsx3

# Windows: 确保系统有 SAPI5 语音引擎
# Linux: 安装 espeak
sudo apt-get install espeak

# macOS: 系统自带 TTS，无需额外配置
```

### ⚠️ 问题：语音输入不可用

**原因**：Python 3.13+ 或 PyAudio 未安装

**解决方案**：
- Python 3.13+：降级到 3.8-3.12
- 或手动安装 PyAudio whl 文件（见主 README）

### ⚠️ 问题：字体显示异常

**解决方案**：
```python
# 编辑 app_gui.py，修改字体设置
font = QFont("Microsoft YaHei", 11)  # Windows
# font = QFont("PingFang SC", 11)  # macOS
# font = QFont("Noto Sans CJK SC", 11)  # Linux
```

### ⚠️ 问题：Vosk 识别不准确

**解决方案**：

1. **使用更大的模型**
   - 小型模型: ~40 MB，适合快速识别
   - 大型模型: ~1 GB，准确度更高
   - 从 https://alphacephei.com/vosk/models 下载

2. **改善录音环境**
   - 减少背景噪音
   - 靠近麦克风说话
   - 使用质量好的麦克风

3. **调整说话方式**
   - 清晰发音
   - 适中语速
   - 避免口音过重

### ⚠️ 问题：麦克风权限被拒绝

**Windows**:

1. 右键点击开始菜单，选择"设置"
2. 点击"隐私"
3. 在左侧菜单中选择"麦克风"
4. 确保"允许应用访问麦克风"已开启
5. 在下方应用列表中找到你的应用，确保其麦克风权限已开启

**Linux**:

```bash
# 确保已安装 alsa-utils
sudo apt-get install alsa-utils

# 使用 alsamixer 调整麦克风设置
alsamixer
```

**macOS**:

1. 打开"系统偏好设置"
2. 点击"安全性与隐私"
3. 选择"麦克风"标签
4. 确保应用程序已被授权使用麦克风

---

## 🎨 自定义主题

### 修改配色方案

在 `app_gui.py` 中找到样式设置部分：

```python
# 修改翻译按钮颜色
self.translate_btn.setStyleSheet("""
    QPushButton {
        background-color: #4CAF50;  # 改为你喜欢的颜色
        ...
    }
""")
```

### 应用全局主题

```python
# 在 main() 函数中
app.setStyle("Fusion")  # 可选: Windows, Fusion, macOS
```

---

## 📊 性能优化建议

1. **首次启动优化**
   ```bash
   # 预编译 PyQt6 模块
   python -m PyQt6.pyrcc_main
   ```

2. **减少内存占用**
   - 关闭不需要的选项卡
   - 清空大段翻译历史

3. **加快翻译速度**
   - 使用更快的网络连接
   - 缩短输入文本长度

---

## 🚀 高级功能

### 打包为可执行文件

使用 PyInstaller 打包成 `.exe`：

```bash
# 安装 PyInstaller
pip install pyinstaller

# 打包
pyinstaller --onefile --windowed --name="TranslationAssistant" app_gui.py

# 生成的 exe 在 dist/ 目录
```

### 添加快捷键

在 `TranslationApp` 类中添加：

```python
from PyQt6.QtGui import QShortcut, QKeySequence

def init_shortcuts(self):
    # Ctrl+Enter 翻译
    QShortcut(QKeySequence("Ctrl+Return"), self, self.start_translation)
    # Ctrl+L 清空
    QShortcut(QKeySequence("Ctrl+L"), self, self.input_text.clear)
```

---

## 📝 开发计划

- [ ] 添加翻译历史记录
- [ ] 支持批量文件翻译
- [ ] 添加词典查询功能
- [ ] 支持更多语言
- [ ] 添加自定义词库
- [ ] 导出翻译结果为 PDF/Word

---

## 💡 技术栈

- **GUI 框架**: PyQt6
- **异步处理**: QThread
- **TTS 引擎**: pyttsx3 (离线)
- **语音识别**: speech_recognition (可选)
- **AI 模型**: Deepseek API

---

**享受桌面版翻译体验！🎉**
