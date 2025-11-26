"""
后台线程模块 - 包含翻译、语音识别、TTS 线程
"""

import json
import os
from translator_core_new import generate_translation_and_advice
from config import VOSK_MODEL_MAP, LANG_NAMES, MODEL_INFO

# 尝试导入 Qt 框架
try:
    from PyQt6.QtCore import QThread, pyqtSignal as Signal
except ImportError:
    from PySide6.QtCore import QThread, Signal

# 尝试导入 Vosk
VOSK_AVAILABLE = False
try:
    from vosk import Model, KaldiRecognizer
    import pyaudio
    VOSK_AVAILABLE = True
except ImportError:
    pass

# 尝试导入 TTS
TTS_AVAILABLE = False
try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    pass


class TranslationThread(QThread):
    """后台翻译线程，避免阻塞 UI"""
    finished = Signal(dict)
    error = Signal(str)
    progress = Signal(int)
    
    def __init__(self, source_text, source_lang, target_lang, scenario, tone):
        super().__init__()
        self.source_text = source_text
        self.source_lang = source_lang
        self.target_lang = target_lang
        self.scenario = scenario
        self.tone = tone
    
    def run(self):
        try:
            self.progress.emit(10)
            result = generate_translation_and_advice(
                source_text=self.source_text,
                source_lang=self.source_lang,
                target_lang=self.target_lang,
                scenario=self.scenario,
                tone=self.tone
            )
            self.progress.emit(100)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class VoiceInputThread(QThread):
    """使用 Vosk 进行免费的本地语音识别"""
    finished = Signal(str)
    error = Signal(str)
    status = Signal(str)
    
    def __init__(self, lang_code, model_path=None):
        super().__init__()
        self.lang_code = lang_code
        self.model_path = model_path or VOSK_MODEL_MAP.get(lang_code, "models/en")
        self.should_stop = False
        self.stream = None
        self.p = None
    
    def stop_recording(self):
        """请求停止录音"""
        self.should_stop = True
    
    def run(self):
        if not VOSK_AVAILABLE:
            self.error.emit(
                "语音识别库未安装。\n\n"
                "请安装以下免费库：\npip install vosk pyaudio\n\n"
                "然后下载语音模型：\n访问 https://alphacephei.com/vosk/models"
            )
            return
        
        lang_name = LANG_NAMES.get(self.lang_code, "未知语言")
        recommended_model = MODEL_INFO.get(self.lang_code, "vosk-model-small-en-us-0.15")
        
        if not os.path.exists(self.model_path):
            self.error.emit(
                f"❌ {lang_name}语音模型未找到\n\n"
                f"模型路径: {self.model_path}\n\n"
                f"📥 请下载 {lang_name} 语音模型：\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"1️⃣ 访问官网: https://alphacephei.com/vosk/models\n"
                f"2️⃣ 下载推荐模型: {recommended_model}\n"
                f"3️⃣ 解压后将文件夹重命名为: {self.lang_code}\n"
                f"4️⃣ 放入项目的 models 文件夹 (最终路径: {self.model_path})\n\n"
                f"💡 提示：\n"
                f"• 小型模型（small）适合日常使用，体积小，速度快\n"
                f"• 大型模型（large）识别更准确，但体积较大\n"
                f"• 完全免费且支持离线使用"
            )
            return
        
        try:
            self.status.emit(f"⏳ 正在加载 {lang_name} 语音模型...")
            model = Model(self.model_path)
            rec = KaldiRecognizer(model, 16000)
            rec.SetWords(True)
            
            self.p = pyaudio.PyAudio()
            self.stream = self.p.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=16000,
                input=True,
                frames_per_buffer=8192
            )
            self.stream.start_stream()
            
            self.status.emit(f"🎙️ {lang_name}语音识别进行中... (点击停止按钮结束)")
            
            results = []
            silent_chunks = 0
            max_silent_chunks = 50
            
            while not self.should_stop and silent_chunks < max_silent_chunks:
                if self.should_stop:
                    break
                
                data = self.stream.read(4096, exception_on_overflow=False)
                
                if rec.AcceptWaveform(data):
                    result = json.loads(rec.Result())
                    text = result.get("text", "")
                    if text:
                        results.append(text)
                        self.status.emit(f"✅ 识别到: {text}")
                        silent_chunks = 0
                    else:
                        silent_chunks += 1
                else:
                    partial = json.loads(rec.PartialResult())
                    partial_text = partial.get("partial", "")
                    if partial_text:
                        self.status.emit(f"🔄 识别中: {partial_text}...")
                        silent_chunks = 0
                    else:
                        silent_chunks += 1
            
            final_result = json.loads(rec.FinalResult())
            final_text = final_result.get("text", "")
            if final_text:
                results.append(final_text)
            
            self.cleanup()
            
            full_text = " ".join(results).strip()
            
            if full_text:
                self.finished.emit(full_text)
            else:
                if self.should_stop:
                    self.error.emit(f"⚠️ 识别已停止\n\n未识别到有效的 {lang_name} 内容")
                else:
                    self.error.emit(f"⚠️ 未识别到任何 {lang_name} 内容\n\n请检查：\n• 麦克风是否正常工作\n• 说话音量是否足够\n• 是否选择了正确的源语言")
                
        except OSError as e:
            self.cleanup()
            self.error.emit(f"🎤 麦克风访问错误: {str(e)}\n\n请检查：\n1. 麦克风是否已连接\n2. 是否授予了麦克风权限\n3. 其他程序是否占用麦克风")
        except Exception as e:
            self.cleanup()
            self.error.emit(f"❌ 语音识别错误: {str(e)}\n\n如果问题持续，请尝试：\n• 重新下载语音模型\n• 检查模型文件完整性")
    
    def cleanup(self):
        """清理音频资源"""
        try:
            if self.stream:
                self.stream.stop_stream()
                self.stream.close()
            if self.p:
                self.p.terminate()
        except:
            pass


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
                "zh": ["chinese", "mandarin", "zh", "cn", "china", "台灣", "中文", "普通话"],
                "en": ["english", "en", "us", "uk", "america", "britain"],
                "ja": ["japanese", "ja", "japan", "日本", "haruka", "ichiro", "sayaka"]
            }
            
            keywords = lang_keywords.get(self.lang_code, ["english"])
            selected_voice = None
            
            for voice in voices:
                voice_name_lower = voice.name.lower()
                voice_id_lower = voice.id.lower() if hasattr(voice, 'id') else ""
                
                for keyword in keywords:
                    if keyword.lower() in voice_name_lower or keyword.lower() in voice_id_lower:
                        selected_voice = voice
                        break
                
                if selected_voice:
                    break
            
            if selected_voice:
                engine.setProperty('voice', selected_voice.id)
            else:
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
