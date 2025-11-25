import streamlit as st
from translator_core_new import generate_translation_and_advice
import streamlit.components.v1 as components
import json
import speech_recognition as sr
import os

# UI Translations
TRANSLATIONS = {
    "zh": {
        "title": "跨文化智能翻译助手（MVP）",
        "version_info": "当前版本：支持文本输入、麦克风录音与浏览器语音输入。",
        "input_label": "请输入要翻译的内容：",
        "source_lang": "源语言",
        "target_lang": "目标语言",
        "lang_zh": "中文",
        "lang_en": "英文",
        "lang_ja": "日文",
        "scenario_label": "使用场景",
        "scenario_tourism": "旅游 / 问路 / 生活场景",
        "scenario_dining": "餐桌聊天 / 饮食场景",
        "scenario_casual": "日常闲聊",
        "scenario_business": "商务 / 半正式场合",
        "tone_label": "语气偏好",
        "tone_casual": "随和",
        "tone_neutral": "中性",
        "tone_polite": "正式/礼貌",
        "translate_btn": "翻译并给出文化建议",
        "input_warning": "请输入要翻译的内容。",
        "spinner": "正在生成翻译和文化建议...",
        "literal_title": "直译",
        "tts_literal_btn": "🔊 朗读直译",
        "natural_title": "更自然的表达",
        "advice_title": "文化建议",
        "voice_input_browser": "🎤 浏览器语音",
        "voice_input_mic": "🎙️ 麦克风录音",
    },
    "en": {
        "title": "Cross-Cultural Translation Assistant (MVP)",
        "version_info": "Current version: Supports text input, microphone recording, and browser voice input.",
        "input_label": "Enter text to translate:",
        "source_lang": "Source Language",
        "target_lang": "Target Language",
        "lang_zh": "Chinese",
        "lang_en": "English",
        "lang_ja": "Japanese",
        "scenario_label": "Scenario",
        "scenario_tourism": "Tourism / Directions / Daily Life",
        "scenario_dining": "Dining / Food",
        "scenario_casual": "Casual Chat",
        "scenario_business": "Business / Semi-formal",
        "tone_label": "Tone Preference",
        "tone_casual": "Casual",
        "tone_neutral": "Neutral",
        "tone_polite": "Polite/Formal",
        "translate_btn": "Translate & Get Cultural Advice",
        "input_warning": "Please enter text to translate.",
        "spinner": "Generating translation and advice...",
        "literal_title": "Literal Translation",
        "tts_literal_btn": "🔊 Read Literal",
        "natural_title": "Natural Expressions",
        "advice_title": "Cultural Advice",
        "voice_input_browser": "🎤 Browser Voice",
        "voice_input_mic": "🎙️ Mic Recording",
    },
    "ja": {
        "title": "異文化翻訳アシスタント (MVP)",
        "version_info": "現在のバージョン：テキスト入力、マイク録音、ブラウザ音声入力をサポート。",
        "input_label": "翻訳するテキストを入力してください：",
        "source_lang": "翻訳元の言語",
        "target_lang": "翻訳先の言語",
        "lang_zh": "中国語",
        "lang_en": "英語",
        "lang_ja": "日本語",
        "scenario_label": "利用シーン",
        "scenario_tourism": "観光 / 道案内 / 生活",
        "scenario_dining": "食事 / レストラン",
        "scenario_casual": "日常会話",
        "scenario_business": "ビジネス / セミフォーマル",
        "tone_label": "口調",
        "tone_casual": "カジュアル",
        "tone_neutral": "ニュートラル",
        "tone_polite": "丁寧 / フォーマル",
        "translate_btn": "翻訳して文化的アドバイスを表示",
        "input_warning": "翻訳するテキストを入力してください。",
        "spinner": "翻訳とアドバイスを生成中...",
        "literal_title": "直訳",
        "tts_literal_btn": "🔊 直訳を読み上げ",
        "natural_title": "より自然な表現",
        "advice_title": "文化的アドバイス",
        "voice_input_browser": "🎤 ブラウザ音声",
        "voice_input_mic": "🎙️ マイク録音",
    }
}


def play_text_js(text, lang):
    """
    Generate and execute JavaScript to play audio using the browser's built-in SpeechSynthesis API.
    This avoids backend network issues (403 Forbidden, connection errors) by running entirely in the client's browser.
    """
    lang_map = {
        "zh": "zh-CN",
        "en": "en-US",
        "ja": "ja-JP"
    }
    js_lang = lang_map.get(lang, "en-US")
    safe_text = json.dumps(text)
    
    js_code = f"""
    <script>
        try {{
            window.parent.speechSynthesis.cancel();
            var msg = new SpeechSynthesisUtterance({safe_text});
            msg.lang = "{js_lang}";
            msg.rate = 1.0; 
            window.parent.speechSynthesis.speak(msg);
        }} catch (e) {{
            console.error("TTS Error:", e);
        }}
    </script>
    """
    components.html(js_code, height=0)


def browser_speech_recognition_js(lang_code):
    """
    Use browser's native Web Speech API for voice input.
    This is a client-side solution that works on all Python versions.
    """
    lang_map = {"zh": "zh-CN", "en": "en-US", "ja": "ja-JP"}
    recognition_lang = lang_map.get(lang_code, "en-US")
    
    # Use a unique ID to store results
    unique_id = f"speech_result_{hash(recognition_lang) % 10000}"
    
    js_code = f"""
    <script>
        (function() {{
            try {{
                const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
                recognition.lang = "{recognition_lang}";
                recognition.continuous = false;
                recognition.interimResults = false;
                
                recognition.onstart = function() {{
                    console.log('Speech recognition started');
                }};
                
                recognition.onresult = function(event) {{
                    const transcript = event.results[0][0].transcript;
                    console.log('Speech result:', transcript);
                    
                    // Store result in session storage for Streamlit to read
                    sessionStorage.setItem('{unique_id}', transcript);
                    
                    // Try to trigger a Streamlit rerun by dispatching an event
                    window.parent.postMessage({{
                        type: 'streamlit:setComponentValue',
                        value: transcript
                    }}, '*');
                }};
                
                recognition.onerror = function(event) {{
                    console.error('Speech recognition error:', event.error);
                    sessionStorage.setItem('{unique_id}_error', event.error);
                }};
                
                recognition.onend = function() {{
                    console.log('Speech recognition ended');
                }};
                
                recognition.start();
            }} catch (e) {{
                console.error('Browser speech recognition not supported:', e);
                alert('您的浏览器不支持语音识别功能。请使用 Chrome/Edge 浏览器，或使用麦克风录音功能。');
            }}
        }})();
    </script>
    <div style="text-align: center; padding: 10px; background: #e3f2fd; border-radius: 5px; margin: 10px 0;">
        <p style="margin: 0; color: #1976d2;">🎤 正在监听... 请开始说话</p>
        <p style="margin: 5px 0 0 0; font-size: 12px; color: #666;">
            说完后请等待几秒，然后手动点击下方文本框查看识别结果
        </p>
    </div>
    """
    components.html(js_code, height=120)
    
    st.info("💡 提示：浏览器语音识别结果会显示在浏览器控制台。由于技术限制，请说完后手动刷新页面或点击文本框查看结果。推荐使用麦克风录音功能获得更好的体验。")


def recognize_speech_from_mic(lang_code):
    """
    Capture audio from the microphone and transcribe it.
    Prioritizes Google Speech Recognition (online).
    Falls back to Vosk (offline) if Google fails and Vosk model is available.
    """
    r = sr.Recognizer()
    
    # Map app language codes to Google Speech Recognition codes
    google_lang_map = {
        "zh": "zh-CN",
        "en": "en-US",
        "ja": "ja-JP"
    }
    target_lang = google_lang_map.get(lang_code, "en-US")

    # Map app language codes to Vosk model paths (relative to app.py)
    vosk_model_map = {
        "zh": "models/zh",
        "en": "models/en",
        "ja": "models/ja"
    }
    vosk_model_path = vosk_model_map.get(lang_code)

    try:
        with sr.Microphone() as source:
            st.info(f"🎙️ 正在监听 ({target_lang})...")
            r.adjust_for_ambient_noise(source, duration=0.5)
            audio = r.listen(source, timeout=5, phrase_time_limit=15)
            
            st.info("🔄 正在识别...")
            
            # 1. Try Google (Online)
            try:
                text = r.recognize_google(audio, language=target_lang)
                st.success("✅ 识别成功！")
                return text
            except sr.RequestError as e:
                # Network error (e.g. GFW blocking Google)
                st.warning(f"⚠️ Google 语音服务连接失败: {e}")
                
                # 2. Try Vosk (Offline) as fallback
                if vosk_model_path and os.path.exists(vosk_model_path):
                    st.info(f"🔄 尝试 Vosk 离线识别 (模型: {vosk_model_path})...")
                    try:
                        from vosk import Model, KaldiRecognizer
                        
                        model = Model(vosk_model_path)
                        rec = KaldiRecognizer(model, 16000)
                        
                        # Convert audio data to bytes
                        data = audio.get_raw_data(convert_rate=16000, convert_width=2)
                        if rec.AcceptWaveform(data):
                            res = json.loads(rec.Result())
                            return res.get("text", "")
                        else:
                            res = json.loads(rec.FinalResult())
                            return res.get("text", "")
                            
                    except ImportError:
                        st.error("❌ Vosk 库未安装。请运行: pip install vosk")
                    except Exception as vosk_e:
                        st.error(f"❌ Vosk 识别失败: {vosk_e}")
                else:
                    st.error("❌ 离线识别不可用。请下载 Vosk 模型并解压到 `models/zh` (或 en/ja) 文件夹。")
                    with st.expander("📖 如何启用离线语音识别 (Vosk)"):
                        st.markdown("""
                        **步骤：**
                        1. 下载对应语言的模型 (https://alphacephei.com/vosk/models)
                           - 中文: `vosk-model-small-cn-0.22`
                           - 英文: `vosk-model-small-en-us-0.15`
                           - 日文: `vosk-model-small-ja-0.22`
                        2. 在项目根目录创建 `models` 文件夹
                        3. 解压下载的模型，重命名为 `zh`、`en` 或 `ja`，放入 `models` 文件夹
                        4. 安装 vosk: `pip install vosk`
                        """)
                return None
                
    except sr.WaitTimeoutError:
        st.warning("⏱️ 未检测到语音")
    except sr.UnknownValueError:
        st.warning("❓ 无法理解音频内容")
    except Exception as e:
        st.error(f"❌ 麦克风或系统错误: {e}")
    return None


def main():
    # Sidebar for language selection
    with st.sidebar:
        st.header("Settings / 设置 / 設定")
        ui_lang_option = st.selectbox(
            "界面语言 / Interface Language",
            ["中文", "English", "日本語"],
            index=0
        )
        
        # Show Python version
        import sys
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        st.caption(f"🐍 Python {python_version}")
        st.caption("✅ 麦克风录音 + 浏览器语音输入")
    
    lang_code_map = {"中文": "zh", "English": "en", "日本語": "ja"}
    ui_lang = lang_code_map[ui_lang_option]
    t = TRANSLATIONS[ui_lang]

    st.title(t["title"])
    st.write(t["version_info"])

    # Initialize session state for input text
    if "input_text" not in st.session_state:
        st.session_state.input_text = ""

    # 1. Language Selection (Moved to top for Voice Input context)
    col1, col2 = st.columns(2)
    with col1:
        source_lang = st.selectbox(t["source_lang"], ["zh", "en", "ja"], index=0,
                                   format_func=lambda x: {"zh": t["lang_zh"], "en": t["lang_en"], "ja": t["lang_ja"]}[x])
    with col2:
        target_lang = st.selectbox(t["target_lang"], ["zh", "en", "ja"], index=1,
                                   format_func=lambda x: {"zh": t["lang_zh"], "en": t["lang_en"], "ja": t["lang_ja"]}[x])

    # 2. Input Area with Voice Input Options
    st.subheader(t["input_label"])
    
    # Voice input buttons in columns
    voice_col1, voice_col2, voice_col3 = st.columns([1, 1, 3])
    
    with voice_col1:
        # Microphone Recording (traditional method)
        if st.button(t["voice_input_mic"], key="mic_recording", use_container_width=True):
            recognized_text = recognize_speech_from_mic(source_lang)
            if recognized_text:
                st.session_state.input_text = recognized_text
                st.rerun()
    
    with voice_col2:
        # Browser Voice Input (Web Speech API)
        if st.button(t["voice_input_browser"], key="browser_voice", use_container_width=True):
            browser_speech_recognition_js(source_lang)
    
    with voice_col3:
        st.caption("🎙️ 推荐使用麦克风录音 | 🎤 浏览器语音为备选方案")

    # Text input area
    def update_input():
        st.session_state.input_text = st.session_state.widget_input

    source_text = st.text_area(
        label="Input Text",
        value=st.session_state.input_text,
        height=150,
        key="widget_input",
        on_change=update_input,
        label_visibility="collapsed",
        placeholder="在此输入或粘贴文本，或使用上方的语音输入按钮..."
    )

    # 3. Other Parameters
    param_col1, param_col2 = st.columns(2)
    
    with param_col1:
        scenario = st.selectbox(
            t["scenario_label"],
            ["tourism", "dining", "casual_chat", "business"],
            index=0,
            format_func=lambda x: {
                "tourism": t["scenario_tourism"],
                "dining": t["scenario_dining"],
                "casual_chat": t["scenario_casual"],
                "business": t["scenario_business"],
            }[x],
        )
    
    with param_col2:
        tone = st.selectbox(
            t["tone_label"],
            ["casual", "neutral", "polite"],
            index=1,
            format_func=lambda x: {
                "casual": t["tone_casual"],
                "neutral": t["tone_neutral"],
                "polite": t["tone_polite"],
            }[x],
        )

    # 4. Translate Button
    if "translation_result" not in st.session_state:
        st.session_state.translation_result = None

    if st.button(t["translate_btn"], type="primary", use_container_width=True):
        if not source_text or not source_text.strip():
            st.warning(t["input_warning"])
        else:
            with st.spinner(t["spinner"]):
                result = generate_translation_and_advice(
                    source_text=source_text,
                    source_lang=source_lang,
                    target_lang=target_lang,
                    scenario=scenario,
                    tone=tone,
                )
                st.session_state.translation_result = result

    # 5. Results Display
    if st.session_state.translation_result:
        result = st.session_state.translation_result
        
        st.divider()
        
        # Literal Translation
        st.subheader(t["literal_title"])
        literal_text = result.get("literal_translation", "")
        st.write(literal_text)
        
        # TTS button for literal translation
        if literal_text and not literal_text.startswith("["):
            clean_literal = literal_text.replace("直译：", "").strip()
            if st.button(t["tts_literal_btn"], key="tts_literal"):
                play_text_js(clean_literal, target_lang)

        st.divider()
        
        # Natural Expressions
        st.subheader(t["natural_title"])
        natural_data = result.get("natural_translation", [])
        
        if isinstance(natural_data, list):
            for idx, item in enumerate(natural_data):
                text = item.get("text", "")
                explanation = item.get("explanation", "")
                
                col_text, col_btn = st.columns([5, 1])
                with col_text:
                    st.markdown(f"**{idx + 1}. {text}**")
                    if explanation:
                        st.caption(explanation)
                with col_btn:
                    if text and not text.startswith("["):
                        if st.button("🔊", key=f"tts_natural_{idx}"):
                            play_text_js(text, target_lang)
        else:
            st.write(natural_data)

        st.divider()
        
        # Cultural Advice
        st.subheader(t["advice_title"])
        st.markdown(result.get("advice", ""))


if __name__ == "__main__":
    main()
