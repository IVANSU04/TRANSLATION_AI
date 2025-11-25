import streamlit as st
from translator_core_new import generate_translation_and_advice
import streamlit.components.v1 as components
import json
import speech_recognition as sr  # 恢复使用
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
        # "voice_input_mic": "🎙️ 麦克风录音",  # 暂时注释
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
        # "voice_input_mic": "🎙️ Mic Recording",  # 暂时注释
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
        # "voice_input_mic": "🎙️ マイク録音",  # 暂时注释
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
    Simplified browser speech recognition with direct HTML rendering.
    完全不依赖任何 API，使用浏览器原生功能
    """
    lang_map = {"zh": "zh-CN", "en": "en-US", "ja": "ja-JP"}
    recognition_lang = lang_map.get(lang_code, "en-US")
    
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: Arial, sans-serif;
                padding: 20px;
                background: #f5f5f5;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                background: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            .status {{
                padding: 10px;
                margin: 10px 0;
                border-radius: 5px;
                text-align: center;
                font-weight: bold;
            }}
            .status.ready {{ background: #e3f2fd; color: #1976d2; }}
            .status.listening {{ background: #e8f5e9; color: #4caf50; }}
            .status.success {{ background: #c8e6c9; color: #2e7d32; }}
            .status.error {{ background: #ffcdd2; color: #c62828; }}
            
            #volumeBar {{
                width: 100%;
                height: 30px;
                background: #e0e0e0;
                border-radius: 15px;
                overflow: hidden;
                margin: 15px 0;
            }}
            #volumeLevel {{
                height: 100%;
                background: linear-gradient(90deg, #4caf50, #8bc34a);
                width: 0%;
                transition: width 0.1s ease;
            }}
            
            #resultBox {{
                min-height: 100px;
                padding: 15px;
                border: 2px solid #ddd;
                border-radius: 5px;
                margin: 15px 0;
                background: #fafafa;
                word-wrap: break-word;
                font-size: 16px;
            }}
            
            .interim {{ color: #999; font-style: italic; }}
            .final {{ color: #333; font-weight: bold; }}
            
            button {{
                padding: 12px 24px;
                margin: 5px;
                border: none;
                border-radius: 5px;
                font-size: 16px;
                cursor: pointer;
                transition: all 0.3s;
            }}
            button:hover {{ transform: translateY(-2px); }}
            .btn-start {{ background: #4caf50; color: white; }}
            .btn-stop {{ background: #f44336; color: white; }}
            .btn-copy {{ background: #2196f3; color: white; }}
            button:disabled {{ background: #ccc; cursor: not-allowed; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div id="status" class="status ready">🎤 准备就绪，点击开始按钮</div>
            
            <div id="volumeBar">
                <div id="volumeLevel"></div>
            </div>
            
            <div style="text-align: center; margin: 20px 0;">
                <button id="startBtn" class="btn-start" onclick="startRecognition()">🎤 开始识别</button>
                <button id="stopBtn" class="btn-stop" onclick="stopRecognition()" disabled>⏹️ 停止</button>
                <button id="copyBtn" class="btn-copy" onclick="copyResult()" disabled>📋 复制结果</button>
            </div>
            
            <div id="resultBox">等待开始...</div>
        </div>

        <script>
            let recognition = null;
            let audioContext = null;
            let analyser = null;
            let microphone = null;
            let animationId = null;
            let finalTranscript = '';

            console.log('Script loaded');

            // 检查浏览器支持
            if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {{
                document.getElementById('status').className = 'status error';
                document.getElementById('status').textContent = '❌ 浏览器不支持语音识别';
                document.getElementById('resultBox').textContent = '请使用 Chrome 或 Edge 浏览器';
                document.getElementById('startBtn').disabled = true;
            }} else {{
                console.log('Speech recognition is supported');
            }}

            function updateStatus(message, className) {{
                const statusDiv = document.getElementById('status');
                statusDiv.textContent = message;
                statusDiv.className = 'status ' + className;
                console.log('Status:', message);
            }}

            function updateVolume() {{
                if (!analyser) return;
                
                const dataArray = new Uint8Array(analyser.frequencyBinCount);
                analyser.getByteFrequencyData(dataArray);
                
                const average = dataArray.reduce((a, b) => a + b) / dataArray.length;
                const percentage = Math.min(100, (average / 128) * 100);
                
                document.getElementById('volumeLevel').style.width = percentage + '%';
                animationId = requestAnimationFrame(updateVolume);
            }}

            async function setupAudioMonitoring() {{
                console.log('Setting up audio monitoring...');
                try {{
                    const stream = await navigator.mediaDevices.getUserMedia({{ audio: true }});
                    console.log('Microphone access granted');
                    audioContext = new (window.AudioContext || window.webkitAudioContext)();
                    analyser = audioContext.createAnalyser();
                    microphone = audioContext.createMediaStreamSource(stream);
                    
                    analyser.fftSize = 256;
                    microphone.connect(analyser);
                    
                    updateVolume();
                    return stream;
                }} catch (err) {{
                    console.error('Microphone access error:', err);
                    updateStatus('❌ 无法访问麦克风：' + err.message, 'error');
                    throw err;
                }}
            }}

            async function startRecognition() {{
                console.log('Start button clicked');
                try {{
                    // 设置音量监控
                    await setupAudioMonitoring();
                    
                    // 初始化语音识别
                    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
                    recognition = new SpeechRecognition();
                    console.log('SpeechRecognition initialized');
                    
                    recognition.lang = '{recognition_lang}';
                    recognition.continuous = true;
                    recognition.interimResults = true;
                    
                    finalTranscript = '';
                    
                    recognition.onstart = function() {{
                        console.log('Recognition started');
                        updateStatus('🎤 正在监听... 请说话', 'listening');
                        document.getElementById('startBtn').disabled = true;
                        document.getElementById('stopBtn').disabled = false;
                        document.getElementById('resultBox').innerHTML = '<span class="interim">等待语音输入...</span>';
                    }};
                    
                    recognition.onresult = function(event) {{
                        console.log('Recognition result received');
                        let interimTranscript = '';
                        
                        for (let i = event.resultIndex; i < event.results.length; i++) {{
                            const transcript = event.results[i][0].transcript;
                            if (event.results[i].isFinal) {{
                                finalTranscript += transcript + ' ';
                                console.log('Final:', transcript);
                            }} else {{
                                interimTranscript += transcript;
                                console.log('Interim:', transcript);
                            }}
                        }}
                        
                        let html = '';
                        if (finalTranscript) {{
                            html += '<span class="final">' + finalTranscript + '</span>';
                            updateStatus('✅ 识别中... 继续说话或点击停止', 'success');
                            document.getElementById('copyBtn').disabled = false;
                        }}
                        if (interimTranscript) {{
                            html += '<span class="interim">' + interimTranscript + '</span>';
                        }}
                        
                        document.getElementById('resultBox').innerHTML = html || '<span class="interim">等待语音输入...</span>';
                    }};
                    
                    recognition.onerror = function(event) {{
                        console.error('Recognition error:', event.error);
                        if (event.error === 'no-speech') {{
                            updateStatus('⚠️ 未检测到语音', 'error');
                        }} else if (event.error === 'not-allowed') {{
                            updateStatus('❌ 麦克风权限被拒绝', 'error');
                        }} else {{
                            updateStatus('❌ 错误: ' + event.error, 'error');
                        }}
                    }};
                    
                    recognition.onend = function() {{
                        console.log('Recognition ended');
                        document.getElementById('startBtn').disabled = false;
                        document.getElementById('stopBtn').disabled = true;
                        
                        if (finalTranscript) {{
                            updateStatus('✅ 识别完成！点击复制结果', 'success');
                        }} else {{
                            updateStatus('⏸️ 已停止', 'ready');
                        }}
                    }};
                    
                    console.log('Starting recognition...');
                    recognition.start();
                    
                }} catch (err) {{
                    console.error('Start error:', err);
                    updateStatus('❌ 启动失败: ' + err.message, 'error');
                }}
            }}

            function stopRecognition() {{
                console.log('Stop button clicked');
                if (recognition) {{
                    recognition.stop();
                }}
                if (animationId) {{
                    cancelAnimationFrame(animationId);
                }}
                if (audioContext) {{
                    audioContext.close();
                }}
                document.getElementById('volumeLevel').style.width = '0%';
            }}

            function copyResult() {{
                console.log('Copy button clicked');
                const text = finalTranscript.trim();
                if (!text) {{
                    alert('没有可复制的内容');
                    return;
                }}
                
                navigator.clipboard.writeText(text).then(function() {{
                    console.log('Copied successfully');
                    const btn = document.getElementById('copyBtn');
                    btn.textContent = '✅ 已复制';
                    setTimeout(function() {{
                        btn.textContent = '📋 复制结果';
                    }}, 2000);
                    
                    alert('识别结果已复制到剪贴板：\\n\\n' + text + '\\n\\n请粘贴到输入框中。');
                }}.catch(function(err) {{
                    console.error('Copy failed:', err);
                    alert('复制失败，请手动复制：\\n\\n' + text);
                }});
            }}
        </script>
    </body>
    </html>
    """
    
    components.html(html_code, height=400, scrolling=False)


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

    # 1. Language Selection
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
        if st.button("🎙️ 麦克风录音", key="mic_recording", use_container_width=True):
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
