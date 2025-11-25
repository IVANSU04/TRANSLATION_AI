"""
Cross-Cultural Translation Assistant - Desktop GUI Version
基于 Qt 的桌面应用程序，不依赖浏览器
支持 PyQt6 或 PySide6
使用 Vosk 进行免费的本地语音识别
"""

import sys
import json
import os
import wave
import tempfile

# Try to import Qt framework (prefer PyQt6, fallback to PySide6)
QT_FRAMEWORK = None
try:
    from PyQt6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QLabel, QTextEdit, QPushButton, QComboBox, QGroupBox,
        QSplitter, QStatusBar, QMessageBox, QTabWidget
    )
    from PyQt6.QtCore import Qt, QThread, pyqtSignal as Signal
    from PyQt6.QtGui import QFont, QIcon, QTextCursor
    QT_FRAMEWORK = "PyQt6"
except ImportError:
    try:
        from PySide6.QtWidgets import (
            QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
            QLabel, QTextEdit, QPushButton, QComboBox, QGroupBox,
            QSplitter, QStatusBar, QMessageBox, QTabWidget
        )
        from PySide6.QtCore import Qt, QThread, Signal
        from PySide6.QtGui import QFont, QIcon, QTextCursor
        QT_FRAMEWORK = "PySide6"
    except ImportError:
        print("=" * 60)
        print("ERROR: Neither PyQt6 nor PySide6 is installed!")
        print("=" * 60)
        print("\nPlease install one of the following:")
        print("\n  Option 1 (PyQt6):")
        print("    pip install PyQt6==6.6.1")
        print("\n  Option 2 (PySide6 - Recommended if PyQt6 has DLL issues):")
        print("    pip install PySide6==6.6.1")
        print("\n" + "=" * 60)
        sys.exit(1)

print(f"✓ Using {QT_FRAMEWORK} for GUI")

from translator_core_new import generate_translation_and_advice

# Try to import text-to-speech
TTS_AVAILABLE = False
try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    print("⚠️ pyttsx3 not available. Install with: pip install pyttsx3")

# Try to import Vosk for speech recognition (free and offline)
VOSK_AVAILABLE = False
try:
    from vosk import Model, KaldiRecognizer
    import pyaudio
    VOSK_AVAILABLE = True
    print("✓ Vosk speech recognition available")
except ImportError as e:
    print(f"⚠️ Vosk not available: {e}")
    print("   Install with: pip install vosk pyaudio")


class TranslationThread(QThread):
    """后台翻译线程，避免阻塞 UI"""
    finished = Signal(dict)
    error = Signal(str)
    
    def __init__(self, source_text, source_lang, target_lang, scenario, tone):
        super().__init__()
        self.source_text = source_text
        self.source_lang = source_lang
        self.target_lang = target_lang
        self.scenario = scenario
        self.tone = tone
    
    def run(self):
        try:
            result = generate_translation_and_advice(
                source_text=self.source_text,
                source_lang=self.source_lang,
                target_lang=self.target_lang,
                scenario=self.scenario,
                tone=self.tone
            )
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class VoiceInputThread(QThread):
    """
    使用 Vosk 进行免费的本地语音识别
    完全离线，无需网络连接
    """
    finished = Signal(str)
    error = Signal(str)
    status = Signal(str)
    
    def __init__(self, lang_code, model_path=None):
        super().__init__()
        self.lang_code = lang_code
        self.model_path = model_path
    
    def run(self):
        if not VOSK_AVAILABLE:
            self.error.emit(
                "语音识别库未安装。\n\n"
                "请安装以下免费库：\n"
                "pip install vosk pyaudio\n\n"
                "然后下载语音模型：\n"
                "访问 https://alphacephei.com/vosk/models"
            )
            return
        
        # 获取语音模型路径
        if not self.model_path:
            model_map = {
                "zh": "models/zh",
                "en": "models/en",
                "ja": "models/ja"
            }
            self.model_path = model_map.get(self.lang_code, "models/en")
        
        # 检查模型是否存在
        if not os.path.exists(self.model_path):
            self.error.emit(
                f"语音模型未找到: {self.model_path}\n\n"
                f"请下载 {self.lang_code} 语音模型：\n"
                f"1. 访问 https://alphacephei.com/vosk/models\n"
                f"2. 下载小型模型（例如 vosk-model-small-{self.lang_code}-*）\n"
                f"3. 解压到 {self.model_path} 文件夹\n\n"
                f"推荐模型：\n"
                f"- 中文: vosk-model-small-cn-0.22\n"
                f"- 英文: vosk-model-small-en-us-0.15\n"
                f"- 日文: vosk-model-small-ja-0.22"
            )
            return
        
        try:
            # 初始化 Vosk 模型
            self.status.emit(f"正在加载语音模型 ({self.lang_code})...")
            model = Model(self.model_path)
            rec = KaldiRecognizer(model, 16000)
            rec.SetWords(True)  # 启用词级识别
            
            # 初始化麦克风
            p = pyaudio.PyAudio()
            stream = p.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=16000,
                input=True,
                frames_per_buffer=8192
            )
            stream.start_stream()
            
            self.status.emit("🎙️ 正在监听... 请说话")
            
            # 录音和识别
            results = []
            silent_chunks = 0
            max_silent_chunks = 30  # 约3秒静默后停止
            
            while silent_chunks < max_silent_chunks:
                data = stream.read(4096, exception_on_overflow=False)
                
                if rec.AcceptWaveform(data):
                    result = json.loads(rec.Result())
                    text = result.get("text", "")
                    if text:
                        results.append(text)
                        self.status.emit(f"识别中: {text}")
                        silent_chunks = 0
                    else:
                        silent_chunks += 1
                else:
                    # 部分识别结果
                    partial = json.loads(rec.PartialResult())
                    partial_text = partial.get("partial", "")
                    if partial_text:
                        self.status.emit(f"识别中: {partial_text}...")
                        silent_chunks = 0
                    else:
                        silent_chunks += 1
            
            # 获取最终结果
            final_result = json.loads(rec.FinalResult())
            final_text = final_result.get("text", "")
            if final_text:
                results.append(final_text)
            
            # 清理资源
            stream.stop_stream()
            stream.close()
            p.terminate()
            
            # 合并所有识别结果
            full_text = " ".join(results).strip()
            
            if full_text:
                self.finished.emit(full_text)
            else:
                self.error.emit("未识别到任何内容，请重试")
                
        except OSError as e:
            self.error.emit(f"麦克风访问错误: {str(e)}\n\n请检查：\n1. 麦克风是否连接\n2. 是否授予麦克风权限")
        except Exception as e:
            self.error.emit(f"语音识别错误: {str(e)}")


class TTSThread(QThread):
    """文本转语音线程"""
    error = Signal(str)
    
    def __init__(self, text, lang_code):
        super().__init__()
        self.text = text
        self.lang_code = lang_code
    
    def run(self):
        if not TTS_AVAILABLE:
            self.error.emit("TTS 库未安装。请安装: pip install pyttsx3")
            return
        
        try:
            engine = pyttsx3.init()
            engine.setProperty('rate', 150)
            
            voices = engine.getProperty('voices')
            lang_keywords = {
                "zh": ["chinese", "mandarin", "zh"],
                "en": ["english", "en"],
                "ja": ["japanese", "ja"]
            }
            
            keywords = lang_keywords.get(self.lang_code, ["english"])
            for voice in voices:
                if any(kw in voice.name.lower() for kw in keywords):
                    engine.setProperty('voice', voice.id)
                    break
            
            engine.say(self.text)
            engine.runAndWait()
        except Exception as e:
            self.error.emit(f"TTS 错误: {str(e)}")


class TranslationApp(QMainWindow):
    """主应用窗口"""
    
    def __init__(self):
        super().__init__()
        self.translation_result = None
        self.init_ui()
    
    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle(f"跨文化智能翻译助手 - 桌面版 [{QT_FRAMEWORK}]")
        self.setGeometry(100, 100, 1200, 800)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        control_panel = self.create_control_panel()
        main_layout.addWidget(control_panel)
        
        splitter = QSplitter(Qt.Orientation.Horizontal)
        input_group = self.create_input_area()
        splitter.addWidget(input_group)
        output_tabs = self.create_output_area()
        splitter.addWidget(output_tabs)
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 3)
        main_layout.addWidget(splitter)
        
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        py_ver = f"Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        features = []
        if VOSK_AVAILABLE:
            features.append("Vosk语音输入✓(免费离线)")
        if TTS_AVAILABLE:
            features.append("语音朗读✓")
        status_text = f"{QT_FRAMEWORK} | {py_ver} | {' | '.join(features) if features else '基础功能'}"
        self.status_bar.showMessage(status_text)
    
    def create_control_panel(self):
        """创建顶部控制面板"""
        group = QGroupBox("翻译设置")
        layout = QHBoxLayout()
        
        # 语言选择
        layout.addWidget(QLabel("源语言:"))
        self.source_lang_combo = QComboBox()
        self.source_lang_combo.addItems(["中文", "英文", "日文"])
        layout.addWidget(self.source_lang_combo)
        
        layout.addWidget(QLabel("→"))
        
        layout.addWidget(QLabel("目标语言:"))
        self.target_lang_combo = QComboBox()
        self.target_lang_combo.addItems(["中文", "英文", "日文"])
        self.target_lang_combo.setCurrentIndex(1)
        layout.addWidget(self.target_lang_combo)
        
        layout.addSpacing(20)
        
        # 场景选择
        layout.addWidget(QLabel("场景:"))
        self.scenario_combo = QComboBox()
        self.scenario_combo.addItems([
            "旅游/问路/生活",
            "餐桌聊天/饮食",
            "日常闲聊",
            "商务/半正式"
        ])
        layout.addWidget(self.scenario_combo)
        
        layout.addSpacing(20)
        
        # 语气选择
        layout.addWidget(QLabel("语气:"))
        self.tone_combo = QComboBox()
        self.tone_combo.addItems(["随和", "中性", "正式/礼貌"])
        self.tone_combo.setCurrentIndex(1)
        layout.addWidget(self.tone_combo)
        
        layout.addStretch()
        
        group.setLayout(layout)
        return group
    
    def create_input_area(self):
        """创建输入区域"""
        group = QGroupBox("输入文本")
        layout = QVBoxLayout()
        
        # 文本输入框
        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText("请输入要翻译的内容...")
        font = QFont("Microsoft YaHei", 11)
        self.input_text.setFont(font)
        layout.addWidget(self.input_text)
        
        # 按钮区
        button_layout = QHBoxLayout()
        
        # 语音输入按钮
        self.voice_btn = QPushButton("🎤 Vosk 语音输入 (免费离线)")
        self.voice_btn.clicked.connect(self.start_voice_input)
        self.voice_btn.setEnabled(VOSK_AVAILABLE)
        
        tooltip = "使用 Vosk 进行免费的本地语音识别（完全离线）"
        if not VOSK_AVAILABLE:
            tooltip = (
                "需要安装 Vosk:\n"
                "1. pip install vosk pyaudio\n"
                "2. 下载语音模型: https://alphacephei.com/vosk/models"
            )
        self.voice_btn.setToolTip(tooltip)
        button_layout.addWidget(self.voice_btn)
        
        # 清空按钮
        clear_btn = QPushButton("🗑️ 清空")
        clear_btn.clicked.connect(self.input_text.clear)
        button_layout.addWidget(clear_btn)
        
        button_layout.addStretch()
        
        # 翻译按钮
        self.translate_btn = QPushButton("🌐 翻译并给出文化建议")
        self.translate_btn.clicked.connect(self.start_translation)
        self.translate_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        button_layout.addWidget(self.translate_btn)
        
        layout.addLayout(button_layout)
        
        # 添加 Vosk 模型下载提示
        if not VOSK_AVAILABLE or not self._check_vosk_models():
            info_label = QLabel(
                "💡 提示: 首次使用需要下载免费的 Vosk 语音模型\n"
                "   访问: https://alphacephei.com/vosk/models"
            )
            info_label.setStyleSheet("color: #666; font-size: 10px; padding: 5px;")
            layout.addWidget(info_label)
        
        group.setLayout(layout)
        return group
    
    def _check_vosk_models(self):
        """检查是否有可用的 Vosk 模型"""
        model_paths = ["models/zh", "models/en", "models/ja"]
        return any(os.path.exists(path) for path in model_paths)
    
    def create_output_area(self):
        """创建输出区域（选项卡）"""
        tabs = QTabWidget()
        
        # 直译选项卡
        literal_tab = QWidget()
        literal_layout = QVBoxLayout(literal_tab)
        self.literal_text = QTextEdit()
        self.literal_text.setReadOnly(True)
        self.literal_text.setFont(QFont("Microsoft YaHei", 11))
        literal_layout.addWidget(self.literal_text)
        
        literal_btn_layout = QHBoxLayout()
        self.literal_tts_btn = QPushButton("🔊 朗读")
        self.literal_tts_btn.clicked.connect(lambda: self.play_tts(self.literal_text.toPlainText()))
        self.literal_tts_btn.setEnabled(False)
        literal_btn_layout.addWidget(self.literal_tts_btn)
        literal_btn_layout.addStretch()
        literal_layout.addLayout(literal_btn_layout)
        
        tabs.addTab(literal_tab, "📝 直译")
        
        # 自然表达选项卡
        natural_tab = QWidget()
        natural_layout = QVBoxLayout(natural_tab)
        self.natural_text = QTextEdit()
        self.natural_text.setReadOnly(True)
        self.natural_text.setFont(QFont("Microsoft YaHei", 11))
        natural_layout.addWidget(self.natural_text)
        
        natural_btn_layout = QHBoxLayout()
        self.natural_tts_btn = QPushButton("🔊 朗读全部")
        self.natural_tts_btn.clicked.connect(self.play_natural_tts)
        self.natural_tts_btn.setEnabled(False)
        natural_btn_layout.addWidget(self.natural_tts_btn)
        natural_btn_layout.addStretch()
        natural_layout.addLayout(natural_btn_layout)
        
        tabs.addTab(natural_tab, "💬 自然表达")
        
        # 文化建议选项卡
        advice_tab = QWidget()
        advice_layout = QVBoxLayout(advice_tab)
        self.advice_text = QTextEdit()
        self.advice_text.setReadOnly(True)
        self.advice_text.setFont(QFont("Microsoft YaHei", 10))
        advice_layout.addWidget(self.advice_text)
        
        tabs.addTab(advice_tab, "🌏 文化建议")
        
        return tabs
    
    def get_lang_code(self, lang_text):
        """将界面语言文本转换为代码"""
        lang_map = {"中文": "zh", "英文": "en", "日文": "ja"}
        return lang_map.get(lang_text, "en")
    
    def get_scenario_code(self, scenario_text):
        """将场景文本转换为代码"""
        scenario_map = {
            "旅游/问路/生活": "tourism",
            "餐桌聊天/饮食": "dining",
            "日常闲聊": "casual_chat",
            "商务/半正式": "business"
        }
        return scenario_map.get(scenario_text, "general")
    
    def get_tone_code(self, tone_text):
        """将语气文本转换为代码"""
        tone_map = {
            "随和": "casual",
            "中性": "neutral",
            "正式/礼貌": "polite"
        }
        return tone_map.get(tone_text, "neutral")
    
    def start_voice_input(self):
        """开始语音输入"""
        source_lang = self.get_lang_code(self.source_lang_combo.currentText())
        
        self.voice_btn.setEnabled(False)
        self.status_bar.showMessage("正在准备 Vosk 语音识别...")
        
        self.voice_thread = VoiceInputThread(source_lang)
        self.voice_thread.finished.connect(self.on_voice_finished)
        self.voice_thread.error.connect(self.on_voice_error)
        self.voice_thread.status.connect(self.status_bar.showMessage)
        self.voice_thread.start()
    
    def on_voice_finished(self, text):
        """语音输入完成"""
        self.input_text.setPlainText(text)
        self.voice_btn.setEnabled(True)
        self.status_bar.showMessage("✅ 语音识别完成", 3000)
    
    def on_voice_error(self, error_msg):
        """语音输入错误"""
        QMessageBox.warning(self, "语音输入", error_msg)
        self.voice_btn.setEnabled(True)
        self.status_bar.showMessage("语音输入失败", 3000)
    
    def start_translation(self):
        """开始翻译"""
        source_text = self.input_text.toPlainText().strip()
        
        if not source_text:
            QMessageBox.warning(self, "警告", "请输入要翻译的内容。")
            return
        
        source_lang = self.get_lang_code(self.source_lang_combo.currentText())
        target_lang = self.get_lang_code(self.target_lang_combo.currentText())
        scenario = self.get_scenario_code(self.scenario_combo.currentText())
        tone = self.get_tone_code(self.tone_combo.currentText())
        
        # 禁用翻译按钮
        self.translate_btn.setEnabled(False)
        self.status_bar.showMessage("正在生成翻译和文化建议...")
        
        # 清空之前的结果
        self.literal_text.clear()
        self.natural_text.clear()
        self.advice_text.clear()
        self.literal_tts_btn.setEnabled(False)
        self.natural_tts_btn.setEnabled(False)
        
        # 启动翻译线程
        self.translation_thread = TranslationThread(
            source_text, source_lang, target_lang, scenario, tone
        )
        self.translation_thread.finished.connect(self.on_translation_finished)
        self.translation_thread.error.connect(self.on_translation_error)
        self.translation_thread.start()
    
    def on_translation_finished(self, result):
        """翻译完成"""
        self.translation_result = result
        
        # 显示直译
        literal = result.get("literal_translation", "")
        self.literal_text.setPlainText(literal)
        if literal and not literal.startswith("["):
            self.literal_tts_btn.setEnabled(TTS_AVAILABLE)
        
        # 显示自然表达
        natural_data = result.get("natural_translation", [])
        if isinstance(natural_data, list):
            natural_html = ""
            for idx, item in enumerate(natural_data, 1):
                text = item.get("text", "")
                explanation = item.get("explanation", "")
                natural_html += f"<p><b>{idx}. {text}</b></p>"
                if explanation:
                    natural_html += f"<p style='margin-left: 20px; color: #666;'>{explanation}</p>"
                natural_html += "<br>"
            self.natural_text.setHtml(natural_html)
            if natural_data:
                self.natural_tts_btn.setEnabled(TTS_AVAILABLE)
        else:
            self.natural_text.setPlainText(str(natural_data))
        
        # 显示文化建议
        advice = result.get("advice", "")
        self.advice_text.setPlainText(advice)
        
        # 恢复UI
        self.translate_btn.setEnabled(True)
        self.status_bar.showMessage("翻译完成！", 3000)
    
    def on_translation_error(self, error_msg):
        """翻译错误"""
        QMessageBox.critical(self, "翻译错误", f"翻译过程中发生错误:\n{error_msg}")
        self.translate_btn.setEnabled(True)
        self.status_bar.showMessage("翻译失败", 3000)
    
    def play_tts(self, text):
        """播放文本转语音"""
        if not text or text.startswith("["):
            return
        
        target_lang = self.get_lang_code(self.target_lang_combo.currentText())
        
        self.tts_thread = TTSThread(text, target_lang)
        self.tts_thread.error.connect(lambda msg: QMessageBox.warning(self, "TTS 错误", msg))
        self.tts_thread.start()
    
    def play_natural_tts(self):
        """播放自然表达的第一条"""
        if not self.translation_result:
            return
        
        natural_data = self.translation_result.get("natural_translation", [])
        if isinstance(natural_data, list) and natural_data:
            first_text = natural_data[0].get("text", "")
            if first_text and not first_text.startswith("["):
                self.play_tts(first_text)


def main():
    """主函数"""
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    window = TranslationApp()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
