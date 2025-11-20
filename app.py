import streamlit as st
from translator_core_new import generate_translation_and_advice
import streamlit.components.v1 as components
import json
import speech_recognition as sr

# UI Translations
TRANSLATIONS = {
    "zh": {
        "title": "跨文化智能翻译助手（MVP）",
        "version_info": "当前版本：支持文本输入与语音朗读（使用浏览器本地语音）。",
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
    },
    "en": {
        "title": "Cross-Cultural Translation Assistant (MVP)",
        "version_info": "Current version: Supports text input and speech synthesis (browser-based).",
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
    },
    "ja": {
        "title": "異文化翻訳アシスタント (MVP)",
        "version_info": "現在のバージョン：テキスト入力と音声読み上げ（ブラウザ機能）をサポート。",
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
    }
}


def play_text_js(text, lang):
    """
    Generate and execute JavaScript to play audio using the browser's built-in SpeechSynthesis API.
    This avoids backend network issues (403 Forbidden, connection errors) by running entirely in the client's browser.
    """
    # Map app language codes to BCP 47 language tags
    lang_map = {
        "zh": "zh-CN",
        "en": "en-US",
        "ja": "ja-JP"
    }
    js_lang = lang_map.get(lang, "en-US")
    
    # JSON dump ensures the text is properly escaped for JavaScript string
    safe_text = json.dumps(text)
    
    # JavaScript code to execute
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


import speech_recognition as sr
import os

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
    # User needs to download models and place them in 'models/zh', 'models/en', etc.
    vosk_model_map = {
        "zh": "models/zh",
        "en": "models/en",
        "ja": "models/ja"
    }
    vosk_model_path = vosk_model_map.get(lang_code)

    try:
        with sr.Microphone() as source:
            st.info(f"Listening ({target_lang})...")
            r.adjust_for_ambient_noise(source, duration=0.5)
            audio = r.listen(source, timeout=5, phrase_time_limit=15)
            
            st.info("Recognizing...")
            
            # 1. Try Google (Online)
            try:
                text = r.recognize_google(audio, language=target_lang)
                return text
            except sr.RequestError as e:
                # Network error (e.g. GFW blocking Google)
                st.warning(f"Google Speech Service connection failed (likely network issue): {e}")
                
                # 2. Try Vosk (Offline) as fallback
                if vosk_model_path and os.path.exists(vosk_model_path):
                    st.info(f"Attempting Vosk offline recognition (Model: {vosk_model_path})...")
                    try:
                        # recognize_vosk expects the model path if not default
                        # Note: speech_recognition's recognize_vosk might need 'vosk' package installed
                        text = r.recognize_vosk(audio, language=target_lang) 
                        # Note: recognize_vosk implementation details vary, usually it takes audio and language? 
                        # Actually sr.recognize_vosk doesn't take 'model_path' directly in all versions, 
                        # but usually looks for 'model' folder. 
                        # Let's try passing the model path if the library supports it, 
                        # or we might need to use vosk library directly if sr doesn't support path.
                        # Checking source code of speech_recognition:
                        # It tries to import vosk. It creates Model(model_path).
                        # But standard recognize_vosk doesn't let us pass path easily in older versions?
                        # Let's assume we can't easily pass path via sr, so we might need to use vosk directly.
                        
                        # Direct Vosk usage for better control
                        from vosk import Model, KaldiRecognizer
                        import json
                        
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
                        st.error("vosk library not installed. Please run `pip install vosk`.")
                    except Exception as vosk_e:
                        st.error(f"Vosk recognition failed: {vosk_e}")
                else:
                    st.error("Offline recognition unavailable. Please download Vosk model and unzip to `models/zh` (or en/ja) folder.")
                    st.markdown("""
                    **How to enable Offline Speech Recognition (Vosk):**
                    1. Download the corresponding language model (https://alphacephei.com/vosk/models)
                       - Chinese: `vosk-model-small-cn-0.22`
                       - English: `vosk-model-small-en-us-0.15`
                       - Japanese: `vosk-model-small-ja-0.22`
                    2. Create a `models` folder in the project root.
                    3. Unzip the downloaded model, rename it to `zh`, `en`, or `ja`, and place it in the `models` folder.
                    """)
                return None
                
    except sr.WaitTimeoutError:
        st.warning("No speech detected")
    except sr.UnknownValueError:
        st.warning("Could not understand audio")
    except Exception as e:
        st.error(f"Microphone or system error: {e}")
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

    # 2. Input Area with Voice Input
    col_label, col_mic = st.columns([5, 1])
    with col_label:
        st.write(t["input_label"])
    with col_mic:
        # Voice Input Button
        if st.button("🎤", help="Voice Input"):
            recognized_text = recognize_speech_from_mic(source_lang)
            if recognized_text:
                st.session_state.input_text = recognized_text
                st.rerun()

    def update_input():
        st.session_state.input_text = st.session_state.widget_input

    source_text = st.text_area(
        label="Input Text",
        value=st.session_state.input_text,
        height=150,
        key="widget_input",
        on_change=update_input,
        label_visibility="collapsed"
    )

    # 3. Other Parameters
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

    if st.button(t["translate_btn"]):
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
        
        st.subheader(t["literal_title"])
        literal_text = result.get("literal_translation", "")
        st.write(literal_text)
        
        # TTS button for literal translation
        if literal_text and not literal_text.startswith("["):
            clean_literal = literal_text.replace("直译：", "").strip()
            if st.button(t["tts_literal_btn"], key="tts_literal"):
                play_text_js(clean_literal, target_lang)

        st.subheader(t["natural_title"])
        natural_data = result.get("natural_translation", [])
        
        if isinstance(natural_data, list):
            for idx, item in enumerate(natural_data):
                text = item.get("text", "")
                explanation = item.get("explanation", "")
                
                col_text, col_btn = st.columns([5, 1])
                with col_text:
                    st.markdown(f"**{text}**")
                    if explanation:
                        st.caption(explanation)
                with col_btn:
                    if text and not text.startswith("["):
                        if st.button("🔊", key=f"tts_natural_{idx}"):
                            play_text_js(text, target_lang)
        else:
            st.write(natural_data)

        st.subheader(t["advice_title"])
        st.markdown(result.get("advice", ""))


if __name__ == "__main__":
    main()
