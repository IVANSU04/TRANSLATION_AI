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
        QSplitter, QStatusBar, QMessageBox, QTabWidget, QProgressBar, QScrollArea
    )
    from PyQt6.QtCore import Qt, QThread, pyqtSignal as Signal
    from PyQt6.QtGui import QFont, QIcon, QTextCursor
    QT_FRAMEWORK = "PyQt6"
except ImportError:
    try:
        from PySide6.QtWidgets import (
            QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
            QLabel, QTextEdit, QPushButton, QComboBox, QGroupBox,
            QSplitter, QStatusBar, QMessageBox, QTabWidget, QProgressBar, QScrollArea
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

# 多语言翻译字典
TRANSLATIONS = {
    "zh-CN": {  # 简体中文
        "app_title": "跨文化智能翻译助手 - 桌面版",
        "ui_language": "界面语言:",
        "source_lang": "源语言:",
        "target_lang": "目标语言:",
        "scenario": "场景:",
        "tone": "语气:",
        "lang_chinese": "中文",
        "lang_english": "英文",
        "lang_japanese": "日文",
        "scenario_tourism": "旅游/问路/生活",
        "scenario_dining": "餐桌聊天/饮食",
        "scenario_casual": "日常闲聊",
        "scenario_business": "商务/半正式",
        "tone_casual": "随和",
        "tone_neutral": "中性",
        "tone_polite": "正式/礼貌",
        "translation_settings": "翻译设置",
        "input_text": "输入文本",
        "input_placeholder": "请输入要翻译的内容...",
        "voice_input": "🎤 Vosk 语音输入 (免费离线)",
        "clear": "🗑️ 清空",
        "translate_btn": "🌐 翻译并给出文化建议",
        "vosk_tip": "💡 提示: 首次使用需要下载免费的 Vosk 语音模型\n   访问: https://alphacephei.com/vosk/models",
        "tab_literal": "📝 直译",
        "tab_natural": "💬 自然表达",
        "tab_advice": "🌏 文化建议",
        "play_audio": "🔊 朗读",
        "play_tooltip": "朗读此表达",
        "warning": "警告",
        "input_required": "请输入要翻译的内容。",
        "translating": "正在生成翻译和文化建议...",
        "translation_complete": "翻译完成！",
        "translation_failed": "翻译失败",
        "translation_error": "翻译错误",
        "translation_error_msg": "翻译过程中发生错误:\n",
        "voice_input_title": "语音输入",
        "voice_recognizing": "✅ 语音识别完成",
        "voice_failed": "语音输入失败",
        "tts_error": "TTS 错误",
        "basic_features": "基础功能",
    },
    "zh-TW": {  # 繁体中文
        "app_title": "跨文化智能翻譯助手 - 桌面版",
        "ui_language": "介面語言:",
        "source_lang": "源語言:",
        "target_lang": "目標語言:",
        "scenario": "場景:",
        "tone": "語氣:",
        "lang_chinese": "中文",
        "lang_english": "英文",
        "lang_japanese": "日文",
        "scenario_tourism": "旅遊/問路/生活",
        "scenario_dining": "餐桌聊天/飲食",
        "scenario_casual": "日常閒聊",
        "scenario_business": "商務/半正式",
        "tone_casual": "隨和",
        "tone_neutral": "中性",
        "tone_polite": "正式/禮貌",
        "translation_settings": "翻譯設置",
        "input_text": "輸入文本",
        "input_placeholder": "請輸入要翻譯的內容...",
        "voice_input": "🎤 Vosk 語音輸入 (免費離線)",
        "clear": "🗑️ 清空",
        "translate_btn": "🌐 翻譯並給出文化建議",
        "vosk_tip": "💡 提示: 首次使用需要下載免費的 Vosk 语音模型\n   訪問: https://alphacephei.com/vosk/models",
        "tab_literal": "📝 直譯",
        "tab_natural": "💬 自然表達",
        "tab_advice": "🌏 文化建議",
        "play_audio": "🔊 朗讀",
        "play_tooltip": "朗讀此表達",
        "warning": "警告",
        "input_required": "請輸入要翻譯的內容。",
        "translating": "正在生成翻譯和文化建議...",
        "translation_complete": "翻譯完成！",
        "translation_failed": "翻譯失敗",
        "translation_error": "翻譯錯誤",
        "translation_error_msg": "翻譯過程中發生錯誤:\n",
        "voice_input_title": "語音輸入",
        "voice_recognizing": "✅ 語音識別完成",
        "voice_failed": "語音輸入失敗",
        "tts_error": "TTS 錯誤",
        "basic_features": "基礎功能",
    },
    "en": {  # English
        "app_title": "Cross-Cultural Translation Assistant - Desktop",
        "ui_language": "UI Language:",
        "source_lang": "Source:",
        "target_lang": "Target:",
        "scenario": "Scenario:",
        "tone": "Tone:",
        "lang_chinese": "Chinese",
        "lang_english": "English",
        "lang_japanese": "Japanese",
        "scenario_tourism": "Tourism/Daily Life",
        "scenario_dining": "Dining/Food",
        "scenario_casual": "Casual Chat",
        "scenario_business": "Business/Semi-formal",
        "tone_casual": "Casual",
        "tone_neutral": "Neutral",
        "tone_polite": "Polite/Formal",
        "translation_settings": "Translation Settings",
        "input_text": "Input Text",
        "input_placeholder": "Enter text to translate...",
        "voice_input": "🎤 Vosk Voice Input (Free Offline)",
        "clear": "🗑️ Clear",
        "translate_btn": "🌐 Translate & Get Cultural Advice",
        "vosk_tip": "💡 Tip: First-time use requires downloading free Vosk speech models\n   Visit: https://alphacephei.com/vosk/models",
        "tab_literal": "📝 Literal",
        "tab_natural": "💬 Natural",
        "tab_advice": "🌏 Cultural Advice",
        "play_audio": "🔊 Play",
        "play_tooltip": "Play this expression",
        "warning": "Warning",
        "input_required": "Please enter text to translate.",
        "translating": "Generating translation and cultural advice...",
        "translation_complete": "Translation complete!",
        "translation_failed": "Translation failed",
        "translation_error": "Translation Error",
        "translation_error_msg": "An error occurred during translation:\n",
        "voice_input_title": "Voice Input",
        "voice_recognizing": "✅ Voice recognition complete",
        "voice_failed": "Voice input failed",
        "tts_error": "TTS Error",
        "basic_features": "Basic Features",
    },
    "ja": {  # 日本語
        "app_title": "異文化翻訳アシスタント - デスクトップ版",
        "ui_language": "UI言語:",
        "source_lang": "元言語:",
        "target_lang": "対象言語:",
        "scenario": "シナリオ:",
        "tone": "トーン:",
        "lang_chinese": "中国語",
        "lang_english": "英語",
        "lang_japanese": "日本語",
        "scenario_tourism": "旅行/道案内/生活",
        "scenario_dining": "食事/会話",
        "scenario_casual": "日常会話",
        "scenario_business": "ビジネス/準公式",
        "tone_casual": "カジュアル",
        "tone_neutral": "ニュートラル",
        "tone_polite": "丁寧/フォーマル",
        "translation_settings": "翻訳設定",
        "input_text": "入力テキスト",
        "input_placeholder": "翻訳するテキストを入力してください...",
        "voice_input": "🎤 Vosk 音声入力 (無料オフライン)",
        "clear": "🗑️ クリア",
        "translate_btn": "🌐 翻訳と文化的アドバイス",
        "vosk_tip": "💡 ヒント: 初回使用時は無料のVosk音声モデルをダウンロードする必要があります\n   訪問: https://alphacephei.com/vosk/models",
        "tab_literal": "📝 直訳",
        "tab_natural": "💬 自然な表現",
        "tab_advice": "🌏 文化的アドバイス",
        "play_audio": "🔊 再生",
        "play_tooltip": "この表現を再生",
        "warning": "警告",
        "input_required": "翻訳するテキストを入力してください。",
        "translating": "翻訳と文化的アドバイスを生成中...",
        "translation_complete": "翻訳完了！",
        "translation_failed": "翻訳失敗",
        "translation_error": "翻訳エラー",
        "translation_error_msg": "翻訳中にエラーが発生しました:\n",
        "voice_input_title": "音声入力",
        "voice_recognizing": "✅ 音声認識完了",
        "voice_failed": "音声入力失敗",
        "tts_error": "TTS エラー",
        "basic_features": "基本機能",
    },
    "es": {  # Español
        "app_title": "Asistente de Traducción Intercultural - Escritorio",
        "ui_language": "Idioma de UI:",
        "source_lang": "Origen:",
        "target_lang": "Destino:",
        "scenario": "Escenario:",
        "tone": "Tono:",
        "lang_chinese": "Chino",
        "lang_english": "Inglés",
        "lang_japanese": "Japonés",
        "scenario_tourism": "Turismo/Vida Diaria",
        "scenario_dining": "Comida/Gastronomía",
        "scenario_casual": "Charla Casual",
        "scenario_business": "Negocios/Semi-formal",
        "tone_casual": "Casual",
        "tone_neutral": "Neutral",
        "tone_polite": "Cortés/Formal",
        "translation_settings": "Configuración de Traducción",
        "input_text": "Texto de Entrada",
        "input_placeholder": "Ingrese el texto a traducir...",
        "voice_input": "🎤 Entrada de Voz Vosk (Gratis Sin Conexión)",
        "clear": "🗑️ Limpiar",
        "translate_btn": "🌐 Traducir y Obtener Consejos Culturales",
        "vosk_tip": "💡 Consejo: El primer uso requiere descargar modelos de voz Vosk gratuitos\n   Visite: https://alphacephei.com/vosk/models",
        "tab_literal": "📝 Literal",
        "tab_natural": "💬 Natural",
        "tab_advice": "🌏 Consejos Culturales",
        "play_audio": "🔊 Reproducir",
        "play_tooltip": "Reproducir esta expresión",
        "warning": "Advertencia",
        "input_required": "Por favor ingrese texto para traducir.",
        "translating": "Generando traducción y consejos culturales...",
        "translation_complete": "¡Traducción completa!",
        "translation_failed": "Traducción fallida",
        "translation_error": "Error de Traducción",
        "translation_error_msg": "Ocurrió un error durante la traducción:\n",
        "voice_input_title": "Entrada de Voz",
        "voice_recognizing": "✅ Reconocimiento de voz completo",
        "voice_failed": "Entrada de voz fallida",
        "tts_error": "Error TTS",
        "basic_features": "Funciones Básicas",
    },
    "fr": {  # Français
        "app_title": "Assistant de Traduction Interculturelle - Bureau",
        "ui_language": "Langue UI:",
        "source_lang": "Source:",
        "target_lang": "Cible:",
        "scenario": "Scénario:",
        "tone": "Ton:",
        "lang_chinese": "Chinois",
        "lang_english": "Anglais",
        "lang_japanese": "Japonais",
        "scenario_tourism": "Tourisme/Vie Quotidienne",
        "scenario_dining": "Repas/Gastronomie",
        "scenario_casual": "Discussion Décontractée",
        "scenario_business": "Affaires/Semi-formel",
        "tone_casual": "Décontracté",
        "tone_neutral": "Neutre",
        "tone_polite": "Poli/Formel",
        "translation_settings": "Paramètres de Traduction",
        "input_text": "Texte d'Entrée",
        "input_placeholder": "Entrez le texte à traduire...",
        "voice_input": "🎤 Entrée Vocale Vosk (Gratuit Hors Ligne)",
        "clear": "🗑️ Effacer",
        "translate_btn": "🌐 Traduire et Obtenir des Conseils Culturels",
        "vosk_tip": "💡 Conseil: La première utilisation nécessite de télécharger des modèles vocaux Vosk gratuits\n   Visitez: https://alphacephei.com/vosk/models",
        "tab_literal": "📝 Littéral",
        "tab_natural": "💬 Naturel",
        "tab_advice": "🌏 Conseils Culturels",
        "play_audio": "🔊 Lire",
        "play_tooltip": "Lire cette expression",
        "warning": "Avertissement",
        "input_required": "Veuillez entrer le texte à traduire.",
        "translating": "Génération de la traduction et des conseils culturels...",
        "translation_complete": "Traduction terminée!",
        "translation_failed": "Traduction échouée",
        "translation_error": "Erreur de Traduction",
        "translation_error_msg": "Une erreur s'est produite lors de la traduction:\n",
        "voice_input_title": "Entrée Vocale",
        "voice_recognizing": "✅ Reconnaissance vocale terminée",
        "voice_failed": "Entrée vocale échouée",
        "tts_error": "TTS-Fehler",
        "basic_features": "Grundfunktionen",
    },
    "de": {  # Deutsch
        "app_title": "Interkultureller Übersetzungsassistent - Desktop",
        "ui_language": "UI-Sprache:",
        "source_lang": "Quelle:",
        "target_lang": "Ziel:",
        "scenario": "Szenario:",
        "tone": "Ton:",
        "lang_chinese": "Chinesisch",
        "lang_english": "Englisch",
        "lang_japanese": "Japanisch",
        "scenario_tourism": "Tourismus/Alltag",
        "scenario_dining": "Essen/Gastronomie",
        "scenario_casual": "Lockeres Gespräch",
        "scenario_business": "Geschäft/Halbformell",
        "tone_casual": "Locker",
        "tone_neutral": "Neutral",
        "tone_polite": "Höflich/Formell",
        "translation_settings": "Übersetzungseinstellungen",
        "input_text": "Eingabetext",
        "input_placeholder": "Geben Sie den zu übersetzenden Text ein...",
        "voice_input": "🎤 Vosk Spracheingabe (Kostenlos Offline)",
        "clear": "🗑️ Löschen",
        "translate_btn": "🌐 Übersetzen & Kulturelle Hinweise Erhalten",
        "vosk_tip": "💡 Tipp: Bei der ersten Verwendung müssen kostenlose Vosk-Sprachmodelle heruntergeladen werden\n   Besuchen Sie: https://alphacephei.com/vosk/models",
        "tab_literal": "📝 Wörtlich",
        "tab_natural": "💬 Natürlich",
        "tab_advice": "🌏 Kulturelle Hinweise",
        "play_audio": "🔊 Abspielen",
        "play_tooltip": "Diesen Ausdruck abspielen",
        "warning": "Warnung",
        "input_required": "Bitte geben Sie Text zum Übersetzen ein.",
        "translating": "Übersetzung und kulturelle Hinweise werden generiert...",
        "translation_complete": "Übersetzung abgeschlossen!",
        "translation_failed": "Übersetzung fehlgeschlagen",
        "translation_error": "Übersetzungsfehler",
        "translation_error_msg": "Während der Übersetzung ist ein Fehler aufgetreten:\n",
        "voice_input_title": "Spracheingabe",
        "voice_recognizing": "✅ Spracherkennung abgeschlossen",
        "voice_failed": "Spracheingabe fehlgeschlagen",
        "tts_error": "TTS-Fehler",
        "basic_features": "Grundfunktionen",
    },
}

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
    progress = Signal(int)  # 进度信号 0-100
    
    def __init__(self, source_text, source_lang, target_lang, scenario, tone):
        super().__init__()
        self.source_text = source_text
        self.source_lang = source_lang
        self.target_lang = target_lang
        self.scenario = scenario
        self.tone = tone
    
    def run(self):
        try:
            self.progress.emit(10)  # 开始翻译
            result = generate_translation_and_advice(
                source_text=self.source_text,
                source_lang=self.source_lang,
                target_lang=self.target_lang,
                scenario=self.scenario,
                tone=self.tone
            )
            self.progress.emit(100)  # 完成
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
            
            # 扩展的语音匹配关键词（包括更多可能的命名格式）
            lang_keywords = {
                "zh": ["chinese", "mandarin", "zh", "cn", "china", "台灣", "中文", "普通话"],
                "en": ["english", "en", "us", "uk", "america", "britain"],
                "ja": ["japanese", "ja", "japan", "日本", "haruka", "ichiro", "sayaka"]  # 添加常见日语语音名称
            }
            
            keywords = lang_keywords.get(self.lang_code, ["english"])
            selected_voice = None
            
            # 尝试匹配语音
            for voice in voices:
                voice_name_lower = voice.name.lower()
                voice_id_lower = voice.id.lower() if hasattr(voice, 'id') else ""
                
                # 检查 name 和 id 字段
                for keyword in keywords:
                    if keyword.lower() in voice_name_lower or keyword.lower() in voice_id_lower:
                        selected_voice = voice
                        break
                
                if selected_voice:
                    break
            
            # 如果找到匹配的语音，使用它
            if selected_voice:
                engine.setProperty('voice', selected_voice.id)
            else:
                # 如果没找到，使用系统默认语音并提示用户
                available_voices = "\n".join([f"- {v.name} ({v.id})" for v in voices[:5]])
                self.error.emit(
                    f"未找到 {self.lang_code} 语音。\n\n"
                    f"将使用系统默认语音。\n\n"
                    f"可用的前 5 个语音：\n{available_voices}\n\n"
                    f"提示：\n"
                    f"- 如需日语语音，请在 Windows 设置中安装日语语音包\n"
                    f"- 设置 → 时间和语言 → 语音 → 添加语音"
                )
            
            engine.say(self.text)
            engine.runAndWait()
            
        except Exception as e:
            self.error.emit(f"TTS 错误: {str(e)}")


class TranslationApp(QMainWindow):
    """主应用窗口"""
    
    def __init__(self):
        super().__init__()
        self.translation_result = None
        self.current_ui_lang = "zh-CN"  # 默认界面语言
        self.init_ui()
        
        # 初始化时检查可用的 TTS 语音（可选，用于调试）
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
        self.progress_bar.setVisible(False)  # 默认隐藏
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
        
        # 语言选择 - 先创建组合框对象
        self.source_lang_label = QLabel(self.t("source_lang"))
        layout.addWidget(self.source_lang_label)
        self.source_lang_combo = QComboBox()
        layout.addWidget(self.source_lang_combo)
        
        layout.addWidget(QLabel("→"))
        
        self.target_lang_label = QLabel(self.t("target_lang"))
        layout.addWidget(self.target_lang_label)
        self.target_lang_combo = QComboBox()
        layout.addWidget(self.target_lang_combo)
        
        # 填充语言选择框的内容
        self.update_lang_combo_items()
        self.target_lang_combo.setCurrentIndex(1)
        
        layout.addSpacing(20)
        
        # 场景选择
        self.scenario_label = QLabel(self.t("scenario"))
        layout.addWidget(self.scenario_label)
        self.scenario_combo = QComboBox()
        layout.addWidget(self.scenario_combo)
        self.update_scenario_combo_items()
        
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
        current_source = self.source_lang_combo.currentIndex() if hasattr(self, 'source_lang_combo') else 0
        current_target = self.target_lang_combo.currentIndex() if hasattr(self, 'target_lang_combo') else 1
        
        self.source_lang_combo.clear()
        self.target_lang_combo.clear()
        
        items = [self.t("lang_chinese"), self.t("lang_english"), self.t("lang_japanese")]
        self.source_lang_combo.addItems(items)
        self.target_lang_combo.addItems(items)
        
        self.source_lang_combo.setCurrentIndex(current_source)
        self.target_lang_combo.setCurrentIndex(current_target)
    
    def update_scenario_combo_items(self):
        """更新场景选择框的选项"""
        current = self.scenario_combo.currentIndex() if hasattr(self, 'scenario_combo') else 0
        self.scenario_combo.clear()
        self.scenario_combo.addItems([
            self.t("scenario_tourism"),
            self.t("scenario_dining"),
            self.t("scenario_casual"),
            self.t("scenario_business")
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
        # 更新窗口标题
        self.setWindowTitle(f"{self.t('app_title')} [{QT_FRAMEWORK}]")
        
        # 更新控制面板
        self.findChild(QGroupBox).setTitle(self.t("translation_settings"))
        self.source_lang_label.setText(self.t("source_lang"))
        self.target_lang_label.setText(self.t("target_lang"))
        self.scenario_label.setText(self.t("scenario"))
        self.tone_label.setText(self.t("tone"))
        
        # 更新下拉框选项
        self.update_lang_combo_items()
        self.update_scenario_combo_items()
        self.update_tone_combo_items()
        
        # 更新输入区域
        self.input_group_box.setTitle(self.t("input_text"))
        self.input_text.setPlaceholderText(self.t("input_placeholder"))
        self.voice_btn.setText(self.t("voice_input"))
        self.clear_btn.setText(self.t("clear"))
        self.translate_btn.setText(self.t("translate_btn"))
        
        if hasattr(self, 'vosk_info_label'):
            self.vosk_info_label.setText(self.t("vosk_tip"))
        
        # 更新输出选项卡
        self.output_tabs.setTabText(0, self.t("tab_literal"))
        self.output_tabs.setTabText(1, self.t("tab_natural"))
        self.output_tabs.setTabText(2, self.t("tab_advice"))
        self.literal_tts_btn.setText(self.t("play_audio"))
        
        # 更新状态栏
        self.update_status_bar()
    
    def create_input_area(self):
        """创建输入区域"""
        self.input_group_box = QGroupBox(self.t("input_text"))
        layout = QVBoxLayout()
        
        # 文本输入框
        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText(self.t("input_placeholder"))
        font = QFont("Microsoft YaHei", 11)
        self.input_text.setFont(font)
        layout.addWidget(self.input_text)
        
        # 按钮区
        button_layout = QHBoxLayout()
        
        # 语音输入按钮
        self.voice_btn = QPushButton(self.t("voice_input"))
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
        self.clear_btn = QPushButton(self.t("clear"))
        self.clear_btn.clicked.connect(self.input_text.clear)
        button_layout.addWidget(self.clear_btn)
        
        button_layout.addStretch()
        
        # 翻译按钮
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
        
        # 添加 Vosk 模型下载提示
        if not VOSK_AVAILABLE or not self._check_vosk_models():
            self.vosk_info_label = QLabel(self.t("vosk_tip"))
            self.vosk_info_label.setStyleSheet("color: #666; font-size: 10px; padding: 5px;")
            layout.addWidget(self.vosk_info_label)
        
        self.input_group_box.setLayout(layout)
        return self.input_group_box
    
    def _check_vosk_models(self):
        """检查是否有可用的 Vosk 模型"""
        model_paths = ["models/zh", "models/en", "models/ja"]
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
        
        # 自然表达选项卡（使用滚动区域容纳动态按钮）
        natural_tab = QWidget()
        natural_layout = QVBoxLayout(natural_tab)
        
        # 创建滚动区域用于显示自然表达列表
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
        # 支持多语言界面的语言名称
        lang_map = {
            # 简体中文
            "中文": "zh", "英文": "en", "日文": "ja",
            # 繁体中文
            "中文": "zh", "英文": "en", "日文": "ja",
            # English
            "Chinese": "zh", "English": "en", "Japanese": "ja",
            # 日本語
            "中国語": "zh", "英語": "en", "日本語": "ja",
            # Español
            "Chino": "zh", "Inglés": "en", "Japonés": "ja",
            # Français
            "Chinois": "zh", "Anglais": "en", "Japonais": "ja",
            # Deutsch
            "Chinesisch": "zh", "Englisch": "en", "Japanisch": "ja"
        }
        return lang_map.get(lang_text, "en")
    
    def get_scenario_code(self, scenario_text):
        """将场景文本转换为代码"""
        # 匹配多语言的场景文本
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
        # 匹配多语言的语气文本
        if any(keyword in tone_text for keyword in ["随和", "隨和", "Casual", "カジュアル", "Décontracté", "Locker"]):
            return "casual"
        elif any(keyword in tone_text for keyword in ["正式", "礼貌", "禮貌", "Polite", "Formal", "丁寧", "フォーマル", "Cortés", "Poli", "Höflich", "Formell"]):
            return "polite"
        else:
            return "neutral"
    
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
        QMessageBox.warning(self, self.t("voice_input_title"), error_msg)
        self.voice_btn.setEnabled(True)
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
        
        # 禁用翻译按钮
        self.translate_btn.setEnabled(False)
        self.status_bar.showMessage(self.t("translating"))
        
        # 清空之前的结果
        self.literal_text.clear()
        self.clear_natural_items()  # 清空自然表达列表
        self.advice_text.clear()
        self.literal_tts_btn.setEnabled(False)
        
        # 显示进度条
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        # 启动翻译线程
        self.translation_thread = TranslationThread(
            source_text, source_lang, target_lang, scenario, tone
        )
        self.translation_thread.finished.connect(self.on_translation_finished)
        self.translation_thread.error.connect(self.on_translation_error)
        self.translation_thread.progress.connect(self.on_translation_progress)
        self.translation_thread.start()
    
    def format_advice_text(self, advice):
        """
        将文化建议从 Markdown 格式转换为易读的纯文本格式
        - 移除 ** 粗体标记
        - 将 - 开头的列表项转换为数字列表
        - 保持清晰的段落结构
        """
        if not advice:
            return ""
        
        # 移除 Markdown 粗体标记
        formatted = advice.replace("**", "")
        
        lines = formatted.split('\n')
        result_lines = []
        section_counter = 0
        item_counter = 0
        in_section = False
        
        for line in lines:
            stripped = line.strip()
            
            # 空行保持
            if not stripped:
                result_lines.append("")
                item_counter = 0
                in_section = False
                continue
            
            # 检测主标题（独立的一行，非列表项）
            if not stripped.startswith('-') and not stripped.startswith('•'):
                if in_section:
                    result_lines.append("")  # 标题前加空行
                section_counter += 1
                result_lines.append(f"{section_counter}. {stripped}")
                in_section = True
                item_counter = 0
            # 列表项
            elif stripped.startswith('-') or stripped.startswith('•'):
                content = stripped.lstrip('-•').strip()
                if content:
                    item_counter += 1
                    # 使用缩进和数字标记子项
                    result_lines.append(f"   {section_counter}.{item_counter} {content}")
            # 普通段落
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
        """创建单个自然表达项（带播放按钮）"""
        item_widget = QWidget()
        item_layout = QHBoxLayout(item_widget)
        item_layout.setContentsMargins(5, 5, 5, 5)
        
        # 左侧文本区域
        text_widget = QWidget()
        text_layout = QVBoxLayout(text_widget)
        text_layout.setContentsMargins(0, 0, 0, 0)
        
        # 主文本
        text_label = QLabel(f"<b>{idx}. {text}</b>")
        text_label.setFont(QFont("Microsoft YaHei", 11))
        text_label.setWordWrap(True)
        text_layout.addWidget(text_label)
        
        # 解释文本
        if explanation:
            explain_label = QLabel(explanation)
            explain_label.setFont(QFont("Microsoft YaHei", 9))
            explain_label.setStyleSheet("color: #666; margin-left: 20px;")
            explain_label.setWordWrap(True)
            text_layout.addWidget(explain_label)
        
        item_layout.addWidget(text_widget, stretch=1)
        
        # 右侧播放按钮
        play_btn = QPushButton("🔊")
        play_btn.setFixedSize(40, 40)
        play_btn.setStyleSheet("""
            QPushButton {
                font-size: 18px;
                border: 2px solid #4CAF50;
                border-radius: 20px;
                background-color: white;
            }
            QPushButton:hover {
                background-color: #e8f5e9;
            }
            QPushButton:pressed {
                background-color: #c8e6c9;
            }
        """)
        play_btn.clicked.connect(lambda: self.play_tts(text))
        play_btn.setEnabled(TTS_AVAILABLE)
        play_btn.setToolTip(self.t("play_tooltip"))
        item_layout.addWidget(play_btn)
        
        # 添加分隔线
        item_widget.setStyleSheet("""
            QWidget {
                border-bottom: 1px solid #e0e0e0;
                padding: 5px;
            }
        """)
        
        return item_widget
    
    def on_translation_finished(self, result):
        """翻译完成"""
        self.translation_result = result
        
        # 显示直译
        literal = result.get("literal_translation", "")
        self.literal_text.setPlainText(literal)
        if literal and not literal.startswith("["):
            self.literal_tts_btn.setEnabled(TTS_AVAILABLE)
        
        # 显示自然表达（使用动态组件）
        self.clear_natural_items()
        # 支持两种字段名：natural_translation 和 natural_expressions
        natural_data = result.get("natural_translation") or result.get("natural_expressions", [])
        if isinstance(natural_data, list) and natural_data:
            for idx, item in enumerate(natural_data, 1):
                text = item.get("text", "")
                explanation = item.get("explanation", "")
                item_widget = self.create_natural_item(idx, text, explanation)
                self.natural_items_layout.addWidget(item_widget)
            # 添加底部弹性空间
            self.natural_items_layout.addStretch()
        elif natural_data:
            # 如果不是列表格式，显示原始数据
            fallback_label = QLabel(str(natural_data))
            fallback_label.setWordWrap(True)
            self.natural_items_layout.addWidget(fallback_label)
        
        # 显示文化建议（格式化处理）
        advice = result.get("advice", "") or result.get("cultural_advice", "")
        formatted_advice = self.format_advice_text(advice)
        self.advice_text.setPlainText(formatted_advice)
        
        # 恢复UI
        self.translate_btn.setEnabled(True)
        self.progress_bar.setVisible(False)  # 隐藏进度条
        self.status_bar.showMessage(self.t("translation_complete"), 3000)
    
    def on_translation_error(self, error_msg):
        """翻译错误"""
        QMessageBox.critical(self, self.t("translation_error"), f"{self.t('translation_error_msg')}{error_msg}")
        self.translate_btn.setEnabled(True)
        self.progress_bar.setVisible(False)  # 隐藏进度条
        self.status_bar.showMessage(self.t("translation_failed"), 3000)
    
    def play_tts(self, text):
        """播放文本转语音"""
        if not text or text.startswith("["):
            return
        
        target_lang = self.get_lang_code(self.target_lang_combo.currentText())
        
        self.tts_thread = TTSThread(text, target_lang)
        self.tts_thread.error.connect(lambda msg: QMessageBox.warning(self, self.t("tts_error"), msg))
        self.tts_thread.start()


def main():
    """主函数"""
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    window = TranslationApp()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
