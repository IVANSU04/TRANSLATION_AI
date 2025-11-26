"""
主窗口模块
"""

import sys
import os

# 尝试导入 Qt 框架
try:
    from PyQt6.QtWidgets import (
        QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QLabel, QTextEdit, QPushButton, QComboBox, QGroupBox,
        QSplitter, QStatusBar, QMessageBox, QTabWidget, QProgressBar, QScrollArea
    )
    from PyQt6.QtCore import Qt
    from PyQt6.QtGui import QFont, QPalette, QColor
    QT_FRAMEWORK = "PyQt6"
except ImportError:
    from PySide6.QtWidgets import (
        QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QLabel, QTextEdit, QPushButton, QComboBox, QGroupBox,
        QSplitter, QStatusBar, QMessageBox, QTabWidget, QProgressBar, QScrollArea
    )
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QFont, QPalette, QColor
    QT_FRAMEWORK = "PySide6"

from config import TRANSLATIONS, THEME_STYLES, VOSK_MODEL_MAP
from threads import TranslationThread, VoiceInputThread, TTSThread, VOSK_AVAILABLE, TTS_AVAILABLE
from .widgets import create_natural_expression_item


class TranslationApp(QMainWindow):
    """主应用窗口"""
    
    def __init__(self):
        super().__init__()
        self.translation_result = None
        self.current_ui_lang = "zh-CN"
        self.current_theme = "light"
        self.init_ui()
        self.apply_theme()
        
        if TTS_AVAILABLE:
            self.check_available_voices()
    
    def check_available_voices(self):
        """检查系统可用的 TTS 语音（调试用）"""
        try:
            import pyttsx3
            engine = pyttsx3.init()
            voices = engine.getProperty('voices')
            print("\n" + "=" * 60)
            print("可用的 TTS 语音:")
            print("=" * 60)
            for i, voice in enumerate(voices, 1):
                print(f"{i}. {voice.name}")
                print(f"   ID: {voice.id}")
                if hasattr(voice, 'languages'):
                    print(f"   语言: {voice.languages}")
                print()
            print("=" * 60 + "\n")
            engine.stop()
        except Exception as e:
            print(f"检查 TTS 语音时出错: {e}")
    
    def t(self, key):
        """获取当前语言的翻译文本"""
        return TRANSLATIONS.get(self.current_ui_lang, TRANSLATIONS["zh-CN"]).get(key, key)
    
    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle(f"{self.t('app_title')} [{QT_FRAMEWORK}]")
        self.setGeometry(100, 100, 1200, 800)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        control_panel = self.create_control_panel()
        main_layout.addWidget(control_panel)
        
        # 添加进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #ddd;
                border-radius: 5px;
                text-align: center;
                height: 25px;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 3px;
            }
        """)
        main_layout.addWidget(self.progress_bar)
        
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
        
        self.update_status_bar()
    
    def update_status_bar(self):
        """更新状态栏"""
        py_ver = f"Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        features = []
        if VOSK_AVAILABLE:
            features.append("Vosk✓")
        if TTS_AVAILABLE:
            features.append("TTS✓")
        status_text = f"{QT_FRAMEWORK} | {py_ver} | {' | '.join(features) if features else self.t('basic_features')}"
        self.status_bar.showMessage(status_text)
    
    def create_control_panel(self):
        """创建顶部控制面板"""
        group = QGroupBox(self.t("translation_settings"))
        layout = QHBoxLayout()
        
        # 界面语言选择
        layout.addWidget(QLabel(self.t("ui_language")))
        self.ui_lang_combo = QComboBox()
        self.ui_lang_combo.addItems([
            "简体中文", "繁體中文", "English", "日本語", "Español", "Français", "Deutsch"
        ])
        self.ui_lang_combo.currentIndexChanged.connect(self.change_ui_language)
        layout.addWidget(self.ui_lang_combo)
        
        layout.addSpacing(20)
        
        # 主题切换
        self.theme_label = QLabel(self.t("theme_label"))
        layout.addWidget(self.theme_label)
        self.theme_combo = QComboBox()
        layout.addWidget(self.theme_combo)
        self.update_theme_combo_items()
        self.theme_combo.currentIndexChanged.connect(self.change_theme)
        
        layout.addSpacing(20)
        
        # 语言选择
        self.source_lang_label = QLabel(self.t("source_lang"))
        layout.addWidget(self.source_lang_label)
        self.source_lang_combo = QComboBox()
        layout.addWidget(self.source_lang_combo)
        
        layout.addWidget(QLabel("→"))
        
        self.target_lang_label = QLabel(self.t("target_lang"))
        layout.addWidget(self.target_lang_label)
        self.target_lang_combo = QComboBox()
        layout.addWidget(self.target_lang_combo)
        
        self.update_lang_combo_items()
        self.target_lang_combo.setCurrentIndex(1)
        
        layout.addSpacing(20)
        
        # 场景选择
        self.scenario_label = QLabel(self.t("scenario"))
        layout.addWidget(self.scenario_label)
        self.scenario_combo = QComboBox()
        layout.addWidget(self.scenario_combo)
        self.update_scenario_combo_items()
        # 设置默认场景为"日常闲聊"（索引2）
        self.scenario_combo.setCurrentIndex(2)
        
        layout.addSpacing(20)
        
        # 语气选择
        self.tone_label = QLabel(self.t("tone"))
        layout.addWidget(self.tone_label)
        self.tone_combo = QComboBox()
        layout.addWidget(self.tone_combo)
        self.update_tone_combo_items()
        self.tone_combo.setCurrentIndex(1)
        
        layout.addStretch()
        
        group.setLayout(layout)
        return group
    
    def update_lang_combo_items(self):
        """更新语言选择框的选项"""
        current_source = self.source_lang_combo.currentIndex() if hasattr(self, 'source_lang_combo') and self.source_lang_combo.count() > 0 else 0
        current_target = self.target_lang_combo.currentIndex() if hasattr(self, 'target_lang_combo') and self.target_lang_combo.count() > 0 else 1
        
        self.source_lang_combo.clear()
        self.target_lang_combo.clear()
        
        items = [self.t("lang_chinese"), self.t("lang_english"), self.t("lang_japanese")]
        self.source_lang_combo.addItems(items)
        self.target_lang_combo.addItems(items)
        
        self.source_lang_combo.setCurrentIndex(current_source)
        self.target_lang_combo.setCurrentIndex(current_target)
    
    def update_scenario_combo_items(self):
        """更新场景选择框的选项"""
        # 修改默认值为索引2（日常闲聊）
        current = self.scenario_combo.currentIndex() if hasattr(self, 'scenario_combo') and self.scenario_combo.count() > 0 else 2
        self.scenario_combo.clear()
        self.scenario_combo.addItems([
            self.t("scenario_tourism"),      # 索引0: 旅游/问路/生活
            self.t("scenario_dining"),       # 索引1: 餐桌聊天/饮食
            self.t("scenario_casual"),       # 索引2: 日常闲聊 (默认)
            self.t("scenario_business")      # 索引3: 商务/半正式
        ])
        self.scenario_combo.setCurrentIndex(current)
    
    def update_tone_combo_items(self):
        """更新语气选择框的选项"""
        current = self.tone_combo.currentIndex() if hasattr(self, 'tone_combo') else 1
        self.tone_combo.clear()
        self.tone_combo.addItems([
            self.t("tone_casual"),
            self.t("tone_neutral"),
            self.t("tone_polite")
        ])
        self.tone_combo.setCurrentIndex(current)
    
    def update_theme_combo_items(self):
        """更新主题选择框的选项"""
        current_theme_index = 0 if self.current_theme == "light" else 1
        self.theme_combo.clear()
        self.theme_combo.addItems([
            self.t("theme_light"),
            self.t("theme_dark")
        ])
        self.theme_combo.setCurrentIndex(current_theme_index)
    
    def change_ui_language(self, index):
        """切换界面语言"""
        lang_map = {
            0: "zh-CN",
            1: "zh-TW",
            2: "en",
            3: "ja",
            4: "es",
            5: "fr",
            6: "de"
        }
        self.current_ui_lang = lang_map.get(index, "zh-CN")
        self.update_all_ui_texts()
    
    def update_all_ui_texts(self):
        """更新所有界面文本"""
        self.setWindowTitle(f"{self.t('app_title')} [{QT_FRAMEWORK}]")
        
        self.findChild(QGroupBox).setTitle(self.t("translation_settings"))
        self.source_lang_label.setText(self.t("source_lang"))
        self.target_lang_label.setText(self.t("target_lang"))
        self.scenario_label.setText(self.t("scenario"))
        self.tone_label.setText(self.t("tone"))
        
        self.update_lang_combo_items()
        self.update_scenario_combo_items()
        self.update_tone_combo_items()
        self.update_theme_combo_items()
        
        self.theme_label.setText(self.t("theme_label"))
        
        self.input_group_box.setTitle(self.t("input_text"))
        self.input_text.setPlaceholderText(self.t("input_placeholder"))
        self.voice_start_btn.setText(self.t("voice_start"))
        self.voice_stop_btn.setText(self.t("voice_stop"))
        self.clear_btn.setText(self.t("clear"))
        self.translate_btn.setText(self.t("translate_btn"))
        
        if hasattr(self, 'vosk_info_label'):
            self.vosk_info_label.setText(self.t("vosk_tip"))
        
        self.output_tabs.setTabText(0, self.t("tab_literal"))
        self.output_tabs.setTabText(1, self.t("tab_natural"))
        self.output_tabs.setTabText(2, self.t("tab_advice"))
        self.literal_tts_btn.setText(self.t("play_audio"))
        
        self.update_status_bar()
    
    def create_input_area(self):
        """创建输入区域"""
        self.input_group_box = QGroupBox(self.t("input_text"))
        layout = QVBoxLayout()
        
        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText(self.t("input_placeholder"))
        font = QFont("Microsoft YaHei", 11)
        self.input_text.setFont(font)
        layout.addWidget(self.input_text)
        
        button_layout = QHBoxLayout()
        
        voice_layout = QHBoxLayout()
        
        self.voice_start_btn = QPushButton(self.t("voice_start"))
        self.voice_start_btn.clicked.connect(self.start_voice_input)
        self.voice_start_btn.setEnabled(VOSK_AVAILABLE)
        self.voice_start_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                padding: 8px 15px;
                font-size: 12px;
                border-radius: 5px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:disabled {
                background-color: #BDBDBD;
            }
        """)
        
        tooltip = "使用 Vosk 进行免费的本地语音识别（完全离线）"
        if not VOSK_AVAILABLE:
            tooltip = (
                "需要安装 Vosk:\n"
                "1. pip install vosk pyaudio\n"
                "2. 下载语音模型: https://alphacephei.com/vosk/models"
            )
        self.voice_start_btn.setToolTip(tooltip)
        voice_layout.addWidget(self.voice_start_btn)
        
        self.voice_stop_btn = QPushButton(self.t("voice_stop"))
        self.voice_stop_btn.clicked.connect(self.stop_voice_input)
        self.voice_stop_btn.setEnabled(False)
        self.voice_stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #F44336;
                color: white;
                padding: 8px 15px;
                font-size: 12px;
                border-radius: 5px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #D32F2F;
            }
            QPushButton:disabled {
                background-color: #BDBDBD;
            }
        """)
        self.voice_stop_btn.setToolTip("停止当前的语音识别")
        voice_layout.addWidget(self.voice_stop_btn)
        
        button_layout.addLayout(voice_layout)
        
        self.clear_btn = QPushButton(self.t("clear"))
        self.clear_btn.clicked.connect(self.input_text.clear)
        button_layout.addWidget(self.clear_btn)
        
        button_layout.addStretch()
        
        self.translate_btn = QPushButton(self.t("translate_btn"))
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
        
        if not VOSK_AVAILABLE or not self._check_vosk_models():
            self.vosk_info_label = QLabel(self.t("vosk_tip"))
            self.vosk_info_label.setStyleSheet("color: #666; font-size: 10px; padding: 5px;")
            layout.addWidget(self.vosk_info_label)
        
        self.input_group_box.setLayout(layout)
        return self.input_group_box
    
    def _check_vosk_models(self):
        """检查是否有可用的 Vosk 模型"""
        model_paths = [
            "models/zh",
            "models/en",
            "models/ja",
        ]
        return any(os.path.exists(path) for path in model_paths)
    
    def create_output_area(self):
        """创建输出区域（选项卡）"""
        self.output_tabs = QTabWidget()
        
        # 直译选项卡
        literal_tab = QWidget()
        literal_layout = QVBoxLayout(literal_tab)
        self.literal_text = QTextEdit()
        self.literal_text.setReadOnly(True)
        self.literal_text.setFont(QFont("Microsoft YaHei", 11))
        literal_layout.addWidget(self.literal_text)
        
        literal_btn_layout = QHBoxLayout()
        self.literal_tts_btn = QPushButton(self.t("play_audio"))
        self.literal_tts_btn.clicked.connect(lambda: self.play_tts(self.literal_text.toPlainText()))
        self.literal_tts_btn.setEnabled(False)
        literal_btn_layout.addWidget(self.literal_tts_btn)
        literal_btn_layout.addStretch()
        literal_layout.addLayout(literal_btn_layout)
        
        self.output_tabs.addTab(literal_tab, self.t("tab_literal"))
        
        # 自然表达选项卡
        natural_tab = QWidget()
        natural_layout = QVBoxLayout(natural_tab)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_widget = QWidget()
        self.natural_items_layout = QVBoxLayout(scroll_widget)
        self.natural_items_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        scroll_area.setWidget(scroll_widget)
        natural_layout.addWidget(scroll_area)
        
        self.output_tabs.addTab(natural_tab, self.t("tab_natural"))
        
        # 文化建议选项卡
        advice_tab = QWidget()
        advice_layout = QVBoxLayout(advice_tab)
        self.advice_text = QTextEdit()
        self.advice_text.setReadOnly(True)
        self.advice_text.setFont(QFont("Microsoft YaHei", 10))
        advice_layout.addWidget(self.advice_text)
        
        self.output_tabs.addTab(advice_tab, self.t("tab_advice"))
        
        return self.output_tabs
    
    def get_lang_code(self, lang_text):
        """将界面语言文本转换为代码"""
        lang_map = {
            "中文": "zh", "英文": "en", "日文": "ja",
            "Chinese": "zh", "English": "en", "Japanese": "ja",
            "中国語": "zh", "英語": "en", "日本語": "ja",
            "Chino": "zh", "Inglés": "en", "Japonés": "ja",
            "Chinois": "zh", "Anglais": "en", "Japonais": "ja",
            "Chinesisch": "zh", "Englisch": "en", "Japanisch": "ja"
        }
        return lang_map.get(lang_text, "en")
    
    def get_scenario_code(self, scenario_text):
        """将场景文本转换为代码"""
        if any(keyword in scenario_text for keyword in ["旅游", "旅遊", "Tourism", "旅行", "Turismo", "Tourisme"]):
            return "tourism"
        elif any(keyword in scenario_text for keyword in ["餐桌", "飲食", "Dining", "食事", "Comida", "Repas", "Essen"]):
            return "dining"
        elif any(keyword in scenario_text for keyword in ["闲聊", "閒聊", "Casual", "日常", "Charla", "Discussion", "Gespräch"]):
            return "casual_chat"
        elif any(keyword in scenario_text for keyword in ["商务", "商務", "Business", "ビジネス", "Negocios", "Affaires", "Geschäft"]):
            return "business"
        return "general"
    
    def get_tone_code(self, tone_text):
        """将语气文本转换为代码"""
        if any(keyword in tone_text for keyword in ["随和", "隨和", "Casual", "カジュアル", "Décontracté", "Locker"]):
            return "casual"
        elif any(keyword in tone_text for keyword in ["正式", "礼貌", "禮貌", "Polite", "Formal", "丁寧", "フォーマル", "Cortés", "Poli", "Höflich", "Formell"]):
            return "polite"
        else:
            return "neutral"
    
    def start_voice_input(self):
        """开始语音输入"""
        source_lang = self.get_lang_code(self.source_lang_combo.currentText())
        
        lang_names = {
            "zh": "中文",
            "en": "英文",
            "ja": "日文"
        }
        lang_name = lang_names.get(source_lang, "未知语言")
        
        self.voice_start_btn.setEnabled(False)
        self.voice_stop_btn.setEnabled(True)
        self.status_bar.showMessage(f"🎤 准备 {lang_name} 语音识别...")
        
        self.voice_thread = VoiceInputThread(source_lang)
        self.voice_thread.finished.connect(self.on_voice_finished)
        self.voice_thread.error.connect(self.on_voice_error)
        self.voice_thread.status.connect(self.status_bar.showMessage)
        self.voice_thread.start()
    
    def stop_voice_input(self):
        """停止语音输入"""
        if hasattr(self, 'voice_thread') and self.voice_thread.isRunning():
            self.voice_thread.stop_recording()
            self.status_bar.showMessage("⏹️ 正在停止语音识别...")
            self.voice_stop_btn.setEnabled(False)
    
    def on_voice_finished(self, text):
        """语音输入完成"""
        self.input_text.setPlainText(text)
        self.voice_start_btn.setEnabled(True)
        self.voice_stop_btn.setEnabled(False)
        self.status_bar.showMessage("✅ 语音识别完成", 3000)
    
    def on_voice_error(self, error_msg):
        """语音输入错误"""
        QMessageBox.warning(self, self.t("voice_input_title"), error_msg)
        self.voice_start_btn.setEnabled(True)
        self.voice_stop_btn.setEnabled(False)
        self.status_bar.showMessage(self.t("voice_failed"), 3000)
    
    def start_translation(self):
        """开始翻译"""
        source_text = self.input_text.toPlainText().strip()
        
        if not source_text:
            QMessageBox.warning(self, self.t("warning"), self.t("input_required"))
            return
        
        source_lang = self.get_lang_code(self.source_lang_combo.currentText())
        target_lang = self.get_lang_code(self.target_lang_combo.currentText())
        scenario = self.get_scenario_code(self.scenario_combo.currentText())
        tone = self.get_tone_code(self.tone_combo.currentText())
        
        self.translate_btn.setEnabled(False)
        self.status_bar.showMessage(self.t("translating"))
        
        self.literal_text.clear()
        self.clear_natural_items()
        self.advice_text.clear()
        self.literal_tts_btn.setEnabled(False)
        
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        self.translation_thread = TranslationThread(
            source_text, source_lang, target_lang, scenario, tone
        )
        self.translation_thread.finished.connect(self.on_translation_finished)
        self.translation_thread.error.connect(self.on_translation_error)
        self.translation_thread.progress.connect(self.on_translation_progress)
        self.translation_thread.start()
    
    def format_advice_text(self, advice):
        """将文化建议从 Markdown 格式转换为易读的纯文本格式"""
        if not advice:
            return ""
        
        formatted = advice.replace("**", "")
        
        lines = formatted.split('\n')
        result_lines = []
        section_counter = 0
        item_counter = 0
        in_section = False
        
        for line in lines:
            stripped = line.strip()
            
            if not stripped:
                result_lines.append("")
                item_counter = 0
                in_section = False
                continue
            
            if not stripped.startswith('-') and not stripped.startswith('•'):
                if in_section:
                    result_lines.append("")
                section_counter += 1
                result_lines.append(f"{section_counter}. {stripped}")
                in_section = True
                item_counter = 0
            elif stripped.startswith('-') or stripped.startswith('•'):
                content = stripped.lstrip('-•').strip()
                if content:
                    item_counter += 1
                    result_lines.append(f"   {section_counter}.{item_counter} {content}")
            else:
                result_lines.append(f"   {stripped}")
        
        return '\n'.join(result_lines)
    
    def on_translation_progress(self, value):
        """更新翻译进度"""
        self.progress_bar.setValue(value)
        if value < 100:
            self.progress_bar.setFormat(f"正在翻译... {value}%")
        else:
            self.progress_bar.setFormat("翻译完成！")
    
    def clear_natural_items(self):
        """清空自然表达列表"""
        while self.natural_items_layout.count():
            child = self.natural_items_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
    
    def create_natural_item(self, idx, text, explanation):
        """创建单个自然表达项"""
        theme = THEME_STYLES[self.current_theme]
        return create_natural_expression_item(
            idx, text, explanation, theme, self.play_tts, TTS_AVAILABLE
        )
    
    def on_translation_finished(self, result):
        """翻译完成"""
        self.translation_result = result
        
        literal = result.get("literal_translation", "")
        self.literal_text.setPlainText(literal)
        if literal and not literal.startswith("["):
            self.literal_tts_btn.setEnabled(TTS_AVAILABLE)
        
        self.clear_natural_items()
        natural_data = result.get("natural_translation") or result.get("natural_expressions", [])
        if isinstance(natural_data, list) and natural_data:
            for idx, item in enumerate(natural_data, 1):
                text = item.get("text", "")
                explanation = item.get("explanation", "")
                item_widget = self.create_natural_item(idx, text, explanation)
                self.natural_items_layout.addWidget(item_widget)
            self.natural_items_layout.addStretch()
        elif natural_data:
            fallback_label = QLabel(str(natural_data))
            fallback_label.setWordWrap(True)
            self.natural_items_layout.addWidget(fallback_label)
        
        advice = result.get("advice", "") or result.get("cultural_advice", "")
        formatted_advice = self.format_advice_text(advice)
        self.advice_text.setPlainText(formatted_advice)
        
        self.translate_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.status_bar.showMessage(self.t("translation_complete"), 3000)
    
    def on_translation_error(self, error_msg):
        """翻译错误"""
        QMessageBox.critical(self, self.t("translation_error"), f"{self.t('translation_error_msg')}{error_msg}")
        self.translate_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.status_bar.showMessage(self.t("translation_failed"), 3000)
    
    def play_tts(self, text):
        """播放文本转语音"""
        if not text or text.startswith("["):
            return
        
        target_lang = self.get_lang_code(self.target_lang_combo.currentText())
        
        self.tts_thread = TTSThread(text, target_lang)
        self.tts_thread.error.connect(lambda msg: QMessageBox.warning(self, self.t("tts_error"), msg))
        self.tts_thread.start()
    
    def change_theme(self, index):
        """切换主题"""
        self.current_theme = "light" if index == 0 else "dark"
        self.apply_theme()
    
    def apply_theme(self):
        """应用当前主题样式"""
        theme = THEME_STYLES[self.current_theme]
        
        palette = QPalette()
        
        palette.setColor(QPalette.ColorRole.Window, QColor(theme["window_bg"]))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(theme["text_color"]))
        palette.setColor(QPalette.ColorRole.Base, QColor(theme["input_bg"]))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(theme["widget_bg"]))
        palette.setColor(QPalette.ColorRole.Text, QColor(theme["text_color"]))
        palette.setColor(QPalette.ColorRole.BrightText, QColor(theme["text_color"]))
        palette.setColor(QPalette.ColorRole.Button, QColor(theme["widget_bg"]))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(theme["text_color"]))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(theme["accent_color"]))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))
        
        self.setPalette(palette)
        
        self.translate_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme["button_bg"]};
                color: white;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 5px;
            }}
            QPushButton:hover {{
                background-color: {theme["button_hover"]};
            }}
            QPushButton:disabled {{
                background-color: {theme["button_disabled"]};
            }}
        """)
        
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 2px solid {theme["border_color"]};
                border-radius: 5px;
                text-align: center;
                height: 25px;
                background-color: {theme["widget_bg"]};
                color: {theme["text_color"]};
            }}
            QProgressBar::chunk {{
                background-color: {theme["accent_color"]};
                border-radius: 3px;
            }}
        """)
        
        text_edit_style = f"""
            QTextEdit {{
                background-color: {theme["input_bg"]};
                color: {theme["text_color"]};
                border: 1px solid {theme["border_color"]};
                border-radius: 5px;
                padding: 5px;
                selection-background-color: {theme["accent_color"]};
                selection-color: #ffffff;
            }}
        """
        self.input_text.setStyleSheet(text_edit_style)
        self.literal_text.setStyleSheet(text_edit_style)
        self.advice_text.setStyleSheet(text_edit_style)
        
        for i in range(self.natural_items_layout.count()):
            item = self.natural_items_layout.itemAt(i)
            if item and item.widget():
                widget = item.widget()
                for label in widget.findChildren(QLabel):
                    if "color: #666" in label.styleSheet():
                        label.setStyleSheet(f"color: {theme['secondary_text']}; margin-left: 20px;")
        
        self.status_bar.setStyleSheet(f"""
            QStatusBar {{
                background-color: {theme["widget_bg"]};
                color: {theme["secondary_text"]};
            }}
        """)
