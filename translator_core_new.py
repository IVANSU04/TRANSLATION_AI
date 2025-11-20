from typing import Dict
import os
import json
import traceback


def _read_credentials(json_path: str = "credentials.json", legacy_path: str = "credentials") -> Dict:
    """Read credentials with support for a structured JSON file containing multiple tokens.

    Return format:
    {
        "tokens": {"name": {"token": "...", "api_url": "https://..."}},
        "default": "name"
    }

    Backwards compatibility:
    - If `credentials.json` exists and is valid, use it.
    - Else if a legacy `credentials` file exists, accept JSON, KEY=VALUE, or a single-line token.
      A single token will be converted into a named token "deepseek-main".
    - If nothing found, return {}.
    """
    # Prefer structured JSON credentials
    try:
        if os.path.exists(json_path):
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            # Normalize tokens into a dict keyed by name
            tokens = {}
            if isinstance(data.get("tokens"), list):
                for entry in data.get("tokens", []):
                    name = entry.get("name") or entry.get("id") or entry.get("key")
                    if not name:
                        continue
                    tokens[name] = {"token": entry.get("token"), "api_url": entry.get("api_url")}
            elif isinstance(data.get("tokens"), dict):
                for name, entry in data.get("tokens", {}).items():
                    if isinstance(entry, dict):
                        tokens[name] = {"token": entry.get("token"), "api_url": entry.get("api_url")}
            # If top-level looks like a single-token dict, accept common keys
            if not tokens and isinstance(data, dict):
                # keys like token/api_key/api_key_name
                if "token" in data or "api_key" in data:
                    tokens["deepseek-main"] = {"token": data.get("token") or data.get("api_key"), "api_url": data.get("api_url")}

            result = {"tokens": tokens}
            if isinstance(data.get("default"), str):
                result["default"] = data.get("default")
            return result
    except Exception:
        # Fall through to legacy parsing
        pass

    # Legacy support: read the old `credentials` file
    if not os.path.exists(legacy_path):
        return {}

    try:
        with open(legacy_path, "r", encoding="utf-8") as f:
            content = f.read().strip()
    except Exception:
        return {}

    if not content:
        return {}

    # Try JSON first
    try:
        data = json.loads(content)
        if isinstance(data, dict):
            # If it's a simple dict of keys, return as tokens if possible
            if "token" in data or "api_key" in data:
                return {"tokens": {"deepseek-main": {"token": data.get("token") or data.get("api_key"), "api_url": data.get("api_url")}}, "default": "deepseek-main"}
            # If user stored a tokens list/dict, try to normalize
            if "tokens" in data:
                return _read_credentials(json_path=legacy_path, legacy_path=legacy_path)
    except Exception:
        pass

    # KEY=VALUE lines
    kv = {}
    for line in content.splitlines():
        if "=" in line:
            k, v = line.split("=", 1)
            kv[k.strip()] = v.strip()

    if kv:
        # Common keys mapping
        token_val = kv.get("token") or kv.get("TOKEN") or kv.get("api_key") or kv.get("API_KEY")
        api_url = kv.get("api_url") or kv.get("API_URL")
        if token_val:
            return {"tokens": {"deepseek-main": {"token": token_val, "api_url": api_url}}, "default": "deepseek-main"}

    # If it's a single-line token (no key=val), accept it as a single token
    # treat the entire content as the token
    return {"tokens": {"deepseek-main": {"token": content, "api_url": None}}, "default": "deepseek-main"}


def generate_translation_and_advice(
    source_text: str,
    source_lang: str,
    target_lang: str,
    scenario: str,
    tone: str = "neutral",
    token_name: str = None,
) -> Dict[str, str]:
    """Construct a prompt and (if possible) call Deepseek via the OpenAI SDK.

    Behavior:
    - Prefer DEEPSEEK_API_KEY from environment; fallback to credentials file.
    - Prefer api_url from credentials or default to https://api.deepseek.com
    - Try to import OpenAI SDK (from openai import OpenAI). If not available,
      return a helpful message in the advice field instructing how to install it
      and fall back to the safe fake outputs so the UI remains functional.
    - Always avoid raising exceptions to the caller; return safe strings.
    """

    try:
        s_text = source_text if isinstance(source_text, str) else ""
        s_lang = source_lang.strip() if isinstance(source_lang, str) and source_lang.strip() else "<unknown>"
        t_lang = target_lang.strip() if isinstance(target_lang, str) and target_lang.strip() else "<unknown>"
        scenario = scenario.strip() if isinstance(scenario, str) and scenario.strip() else "general"
        tone = tone.strip() if isinstance(tone, str) and tone.strip() else "neutral"

        # Map language codes to natural names for the prompt
        lang_names = {
            "zh": "Simplified Chinese",
            "en": "English",
            "ja": "Japanese"
        }
        s_lang_name = lang_names.get(s_lang, s_lang)
        t_lang_name = lang_names.get(t_lang, t_lang)

        if not s_text:
            return {
                "literal_translation": "[Literal Example] Source text not provided.",
                "natural_translation": [{"text": "[No Natural Expression]", "explanation": ""}],
                "advice": "[Tip] Source text not provided; please enter text to translate to get translation and cultural advice.",
            }

        # Build prompt and messages
        prompt = (
            "Act as a cross-cultural translation assistant. Output JSON data based on the following requirements.\n"
            "Input content:\n"
            f"Source Text: {s_text}\n"
            f"Source Language: {s_lang}\n"
            f"Target Language: {t_lang}\n"
            f"Scenario: {scenario}\n"
            f"Tone Preference: {tone}\n\n"
            "Please return the following JSON structure (do not include Markdown code block markers, ensure valid JSON):\n"
            "{\n"
            '  "literal_translation": "Literal translation result (string)",\n'
            '  "natural_expressions": [\n'
            f'    {{"text": "Natural expression 1 (Target Language)", "explanation": "Explanation and usage context in {s_lang_name}"}},\n'
            f'    {{"text": "Natural expression 2 (Target Language)", "explanation": "Explanation and usage context in {s_lang_name}"}}\n'
            '  ],\n'
            f'  "cultural_advice": "Cultural advice (Markdown string, written in {s_lang_name}. Based on the \'{scenario}\' scenario and \'{tone}\' tone, provide deep cultural background analysis. Include: 1. Cultural mindset differences behind the language; 2. Etiquette taboos or unwritten rules in this scenario; 3. Potential emotional reaction of the other party. Use lists or bold text to organize content, do not use # headers, ensure empty lines between paragraphs, clear layout, substantial content, avoid vague generalizations.)"\n'
            "}\n"
        )

        messages = [
            {"role": "system", "content": "You are a helpful cross-cultural translation assistant. Output valid JSON only."},
            {"role": "user", "content": prompt},
        ]

        # Credentials: prefer environment variable; then structured credentials.json;
        # keep backward compatibility with legacy single-line `credentials`.
        creds = _read_credentials()

        # Choose token: environment variable overrides everything
        env_token = os.environ.get("DEEPSEEK_API_KEY") or os.environ.get("DEEPSEEK_API_KEY_0")
        token = None
        api_url = None
        if env_token:
            token = env_token
        else:
            # structured creds: {'tokens': {name: {token, api_url}}, 'default': name}
            tokens = creds.get("tokens") if isinstance(creds, dict) else None
            default_name = creds.get("default") if isinstance(creds, dict) else None
            if token_name and tokens and token_name in tokens:
                token = tokens[token_name].get("token")
                api_url = tokens[token_name].get("api_url")
            elif default_name and tokens and default_name in tokens:
                token = tokens[default_name].get("token")
                api_url = tokens[default_name].get("api_url")
            elif tokens:
                # pick the first available token
                first = next(iter(tokens.items()))
                token = first[1].get("token")
                api_url = first[1].get("api_url")

        if not api_url:
            # allow top-level api_url in legacy kv formats
            if isinstance(creds, dict) and creds.get("api_url"):
                api_url = creds.get("api_url")
            else:
                api_url = "https://api.deepseek.com"

        # Try to call Deepseek via OpenAI SDK
        model_text = ""
        try:
            from openai import OpenAI

            if token:
                client = OpenAI(api_key=token, base_url=api_url)
                response = client.chat.completions.create(
                    model="deepseek-chat",
                    messages=messages,
                    stream=False,
                    response_format={"type": "json_object"}  # Enforce JSON if supported, otherwise prompt handles it
                )
                # Extract text from common response shape
                try:
                    model_text = response.choices[0].message.content
                except Exception:
                    # fallback: stringify response
                    try:
                        model_text = json.dumps(response)
                    except Exception:
                        model_text = str(response)
            else:
                model_text = "[Missing Credentials] DEEPSEEK API token not found in environment variables or credentials file."
        except ImportError:
            model_text = "[SDK Not Installed] Please run: pip install openai and set DEEPSEEK_API_KEY to your token."
        except Exception as e:
            # Capture trace for debugging but do not raise
            model_text = f"[Deepseek Call Error] {str(e)}"

        # If we got model_text from API, parse JSON
        if model_text and not model_text.startswith("[SDK Not Installed]") and not model_text.startswith("[Missing Credentials]") and not model_text.startswith("[Deepseek Call Error]"):
            # Debug: print raw output to console
            print(f"DEBUG: Raw model output:\n{model_text}\n" + "-"*20)

            try:
                # Clean up potential markdown markers
                clean_text = model_text.strip()
                if clean_text.startswith("```json"):
                    clean_text = clean_text[7:]
                if clean_text.startswith("```"):
                    clean_text = clean_text[3:]
                if clean_text.endswith("```"):
                    clean_text = clean_text[:-3]
                
                data = json.loads(clean_text.strip())
                
                literal = data.get("literal_translation", "") or "[No Literal Translation Output]"
                natural = data.get("natural_expressions", []) 
                if not natural:
                    natural = [{"text": "[No Natural Expression Output]", "explanation": ""}]
                advice = data.get("cultural_advice", "") or "[No Cultural Advice Output]"

                return {
                    "literal_translation": literal,
                    "natural_translation": natural, # List of dicts
                    "advice": advice,
                }
            except Exception as e:
                print(f"JSON Parsing failed: {e}")
                # parsing failed — continue to fallback
                pass

        # If we reach here, either SDK missing, token missing, API error, or parsing failed
        note = ""
        if model_text.startswith("[SDK Not Installed]"):
            note = "\n\n**Tip**: OpenAI SDK not installed. Please run `pip install openai` and set `DEEPSEEK_API_KEY`."
        elif model_text.startswith("[Missing Credentials]"):
            note = "\n\n**Tip**: Deepseek credentials not found. Please set token in `DEEPSEEK_API_KEY` environment variable or `credentials` file in project root."
        elif model_text.startswith("[Deepseek Call Error]"):
            note = f"\n\n**Deepseek Call Error**: {model_text}"

        # Fallback safe fake implementation
        literal = f"[Literal Example] ({s_lang} -> {t_lang}): {s_text}"
        # Natural needs to be a list now
        natural = [
            {"text": f"[Natural Expression Example] {s_text}", "explanation": f"(Scenario: {scenario}) This is an example of a more natural expression generated for the source text."}
        ]
        advice = (
            "【Cultural Advice Example】\n"
            "- Based on your selected scenario, remind the user to pay attention to polite language and local customs.\n"
            "- This will be generated by the large model based on source text and target culture in the future."
        ) + note

        return {
            "literal_translation": literal,
            "natural_translation": natural,
            "advice": advice,
        }
    except Exception as exc:
        # Ultimate fallback — never raise
        return {
            "literal_translation": "[Error] Cannot generate literal translation.",
            "natural_translation": [{"text": "[Error]", "explanation": f"Cannot generate natural translation: {str(exc)}"}],
            "advice": f"[Error] Exception during advice generation: {str(exc)}\n{traceback.format_exc()}",
        }
