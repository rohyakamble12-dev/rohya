import ollama
import json
import re
import os
import threading
from openai import OpenAI
from veda.core.memory import VedaMemory
from veda.utils.logger import logger

class VedaLLM:
    def __init__(self, primary_model="qwen2.5:3b", fallback_model="tinyllama"):
        self.primary_model = primary_model
        self.fallback_model = fallback_model
        self.memory = VedaMemory()

        # Cloud Neural Link Configuration (Neural Trinity)
        self.deepseek_key = os.getenv("DEEPSEEK_API_KEY")
        self.grok_key = os.getenv("GROK_API_KEY")

        # Unified Cloud Clients (OpenAI Compatible)
        self.deepseek_client = OpenAI(api_key=self.deepseek_key, base_url="https://api.deepseek.com") if self.deepseek_key else None
        self.grok_client = OpenAI(api_key=self.grok_key, base_url="https://api.x.ai/v1") if self.grok_key else None

        # High-Speed Neural Cache for zero-latency repeat intent recognition
        self._intent_cache = {}
        self._max_cache_size = 100

        self.system_prompt = (
            "You are Veda, a sophisticated AI partner inspired by JARVIS and FRIDAY. "
            "Refer to the user as 'Sir'. No markdown or emojis. Output the final tactical result only. "
            "Direct Action Policy: Prioritize actions over suggestions. Do not suggest doing things; just do them if a tool is available. "
            "Conversational Awareness: If the user is just talking or asking for information that doesn't require a tool, respond naturally as a helpful partner."
        )
        self.messages = [{"role": "system", "content": self.system_prompt}]

    def chat(self, user_input, context_info=None, protocols=None, stream_callback=None):
        from veda.utils.privacy import privacy

        # 0. Context Pruning
        self._prune_context()
        user_input = privacy.scrub(user_input)

        facts = self.memory.get_all_facts_summary()
        episodes = self.memory.get_recent_episodes(3)

        context_aware_input = (
            f"[Protocols: {protocols}]\n[Episodes: {episodes}]\n"
            f"[Knowledge: {facts}]\nUser: {user_input}"
        )

        self.messages.append({"role": "user", "content": context_aware_input})

        # Neural Trinity Implementation
        response = self.chat_completion(self.messages, stream_callback=stream_callback)
        if response:
            self.messages.append({"role": "assistant", "content": response})
            self.memory.store_episode("conversation", f"Veda: {response[:50]}...")
            return response

        fallback = self._survival_chat(user_input)
        if stream_callback:
             stream_callback(fallback)
        return fallback

    def chat_completion(self, messages, stream_callback=None):
        """Unified Cloud-Hybrid chat completion: DeepSeek -> Grok -> Local."""
        from veda.core.runtime import runtime

        # Priority Tier 1: Cloud-Reasoning (Neural Trinity)
        providers = [
            ("deepseek", "deepseek-chat", self.deepseek_client),
            ("grok", "grok-beta", self.grok_client),
            ("ollama", self.primary_model, ollama),
            ("ollama_fallback", self.fallback_model, ollama)
        ]

        for name, model, client in providers:
            if not client: continue

            try:
                if stream_callback:
                    full_response = ""
                    if name in ["deepseek", "grok"]:
                        # Cloud Streaming Interface
                        response = client.chat.completions.create(
                            model=model, messages=messages, stream=True, timeout=15
                        )
                        for chunk in response:
                            content = chunk.choices[0].delta.content or ""
                            full_response += content
                            stream_callback(content)
                    else:
                        # Local Streaming Interface
                        for chunk in client.chat(model=model, messages=messages, stream=True):
                            content = chunk['message']['content']
                            full_response += content
                            stream_callback(content)
                    if full_response: return full_response
                else:
                    # Non-Streaming logic with Governed timeouts
                    if name in ["deepseek", "grok"]:
                        res = client.chat.completions.create(model=model, messages=messages, timeout=12)
                        return res.choices[0].message.content
                    else:
                        res = runtime.execute_llm(client.chat, timeout=10, model=model, messages=messages)
                        if res.success: return res.data['message']['content']

            except Exception as e:
                logger.error(f"Neural Link [{name}] failure: {e}")
        return None

    def _survival_chat(self, user_input):
        ui = user_input.lower()
        if "status" in ui: return "Sir, LLM systems offline. Core plugins operative."
        return "I am operating in survival mode (LLM offline). Direct commands only, Sir."

    def extract_intent(self, user_input):
        """Tiered Intent Extraction with Cloud Support and Neural Caching."""
        user_input = user_input.strip()

        # 0. High-Speed Neural Cache lookup
        if user_input in self._intent_cache:
            return self._intent_cache[user_input]

        # 0.1 Tactical Fast-Path (Zero Latency) - High reliability for core commands
        fast_path = self._survival_intent_extraction(user_input)
        if fast_path.get("confidence", 0) >= 0.9:
            self._update_cache(user_input, fast_path)
            return fast_path

        intent_prompt = f"Extract tactical intent and params as JSON from: {user_input}"
        sys_p = (
            "Analyze the user command and extract the tactical intent. Output raw JSON ONLY. "
            "JSON Format: {'intent': str, 'params': dict, 'confidence': float}. "
            "Strategic Directives:\n"
            "1. If it's just conversation (greeting, feedback, small talk), set intent to 'chat' and put your response in params.response.\n"
            "2. If it's a request for a known tactical action but you are missing parameters, use intent 'none'.\n"
            "3. Set confidence to 1.0 only for direct, unambiguous commands.\n"
            "4. Ignore polite filler words (please, could you, etc.)."
        )

        # Neural Trinity for Intent Extraction
        providers = [
            ("deepseek", "deepseek-chat", self.deepseek_client),
            ("grok", "grok-beta", self.grok_client),
            ("ollama", self.primary_model, ollama)
        ]

        for name, model, client in providers:
            if not client: continue
            try:
                if name in ["deepseek", "grok"]:
                    res = client.chat.completions.create(
                        model=model,
                        messages=[{"role": "system", "content": sys_p}, {"role": "user", "content": intent_prompt}],
                        response_format={"type": "json_object"},
                        timeout=8
                    )
                    content = res.choices[0].message.content
                else:
                    from veda.core.runtime import runtime
                    res = runtime.execute_llm(client.chat, timeout=6, model=model,
                                             messages=[{"role": "system", "content": sys_p}, {"role": "user", "content": intent_prompt}])
                    if not res.success: continue
                    content = res.data['message']['content']

                result = self._parse_json(content)
                if result.get("intent") != "none":
                    self._update_cache(user_input, result)
                    return result
            except Exception: continue

        return self._survival_intent_extraction(user_input)

    def _update_cache(self, key, value):
        if len(self._intent_cache) >= self._max_cache_size:
            # Simple eviction: clear oldest entries if full
            self._intent_cache.clear()
        self._intent_cache[key] = value

    def _prune_context(self, max_messages=10):
        """Neural Context Management: Prevents latency scaling with history length."""
        if len(self.messages) > max_messages:
            # Keep the system prompt + most recent exchanges
            system_msg = self.messages[0]
            recent_msgs = self.messages[-(max_messages-1):]
            self.messages = [system_msg] + recent_msgs

    def _parse_json(self, content):
        """Resilient JSON extraction for malformed or verbose LLM outputs (handles objects and arrays)."""
        content = content.strip()

        # 1. High-Precision Markdown Extraction (Handles multiple blocks, takes first valid)
        blocks = re.findall(r'```(?:json)?\s*([\s\S]*?)\s*```', content)
        for block in blocks:
            try:
                data = json.loads(block)
                if data: return data
            except Exception: continue

        # 2. Strategic Structural Search (Non-greedy discovery of Objects or Arrays)
        # We try to find the largest valid JSON structure in the string
        for pattern in [r'(\{[\s\S]*\})', r'(\[[\s\S]*\])']:
            match = re.search(pattern, content)
            if match:
                snippet = match.group(1)
                try: return json.loads(snippet)
                except json.JSONDecodeError:
                    # Attempt cleanup of trailing conversational noise often appended by LLMs
                    for i in range(len(snippet)-1, 0, -1):
                        if snippet[i] in ['}', ']']:
                            try: return json.loads(snippet[:i+1])
                            except: continue

        # 3. Direct Parse (for clean outputs)
        try: return json.loads(content)
        except Exception: pass

        logger.warning(f"Neural Link: Failed to parse tactical JSON. Payload: {content[:150]}...")
        return {"intent": "none", "params": {}, "raw_failure": content}

    def _survival_intent_extraction(self, user_input):
        """Tactical Fast-Path: Regex-based extraction for zero-latency execution of core commands."""
        # 1. Recursive Prefix Normalization
        ui = user_input.lower().strip()
        prev_ui = None
        while ui != prev_ui:
            prev_ui = ui
            # Strip Veda/Friday names and polite filler
            ui = re.sub(r'^(?:veda|friday|hey veda|hey friday|hi veda|hi friday|please|could you|can you|i want to|go ahead and|will you)[,\s!.]*\s*', '', ui)

        # 1.1 Segment input and take the dominant first part
        segments = re.split(r'\s+and\s+|\s+then\s+|\.|\,', ui)
        ui = segments[0].strip() if segments and segments[0].strip() else ui

        # 2. Direct Match Confidence Multiplier
        # We search for commands within the full string, but only give 1.0 confidence
        # if the command is the primary part of the sentence.
        def get_confidence(match_text):
            if match_text in ui and (len(ui) - len(match_text)) < 15:
                return 1.0
            return 0.7

        # 3. System Controls
        if "mute" in ui:
             return {"intent": "mute_toggle", "params": {}, "confidence": get_confidence("mute"), "survival": True}

        if "volume" in ui:
            match = re.search(r"(?:set|change|put|volume)\D*(\d+)", ui)
            if match: return {"intent": "set_volume", "params": {"level": int(match.group(1))}, "confidence": 1.0, "survival": True}
            if "up" in ui or "increase" in ui:
                 return {"intent": "set_volume", "params": {"level": 70}, "confidence": 0.9, "survival": True}
            if "down" in ui or "decrease" in ui:
                 return {"intent": "set_volume", "params": {"level": 30}, "confidence": 0.9, "survival": True}

        if "brightness" in ui:
            match = re.search(r"(?:set|change|put|brightness)\D*(\d+)", ui)
            if match: return {"intent": "set_brightness", "params": {"level": int(match.group(1))}, "confidence": 1.0, "survival": True}

        # 4. App Management
        if any(word in ui for word in ["open", "launch", "start"]):
            # Optimized regex for multi-word app names, stopping at common sentence connectors
            match = re.search(r"(?:open|launch|start)\s+(?:the\s+)?([a-zA-Z0-9.\-_ ]+?)(?:\s+and\s+|\s+then\s+|\.|\,|$)", ui)
            if match:
                 app = match.group(1).strip()
                 return {"intent": "open_app", "params": {"app_name": app}, "confidence": get_confidence(app), "survival": True}

        if any(word in ui for word in ["close", "exit", "terminate", "stop"]):
            match = re.search(r"(?:close|exit|terminate|stop)\s+(?:the\s+)?([a-zA-Z0-9.\-_ ]+?)(?:\s+and\s+|\s+then\s+|\.|\,|$)", ui)
            if match:
                app = match.group(1).strip()
                return {"intent": "close_app", "params": {"app_name": app}, "confidence": get_confidence(app), "survival": True}

        # 5. Modes
        if any(word in ui for word in ["describe modes", "what modes", "list modes", "modes available"]):
            return {"intent": "describe_modes", "params": {}, "confidence": 1.0, "survival": True}

        mode_match = re.search(r"(?:set|engage|switch to|change to|go to|activate|switch|turn on)\s+(?:mode\s+)?(\w+)", ui)
        if mode_match:
            mode_val = mode_match.group(1).strip()
            # If the extracted word is a known mode, boost confidence to 1.0
            known_modes = ["focus", "stealth", "gaming", "normal", "clean slate", "house party"]
            if mode_val in known_modes:
                 return {"intent": "set_mode", "params": {"mode": mode_val}, "confidence": 1.0, "survival": True}
            return {"intent": "set_mode", "params": {"mode": mode_val}, "confidence": 0.9, "survival": True}

        if "focus mode" in ui: return {"intent": "focus_mode", "params": {}, "confidence": 1.0, "survival": True}
        if "stealth mode" in ui: return {"intent": "stealth_mode", "params": {}, "confidence": 1.0, "survival": True}
        if "shutdown" in ui: return {"intent": "shutdown", "params": {}, "confidence": 1.0, "survival": True}
        if "restart" in ui: return {"intent": "restart", "params": {}, "confidence": 1.0, "survival": True}
        if "screenshot" in ui or "capture" in ui: return {"intent": "screenshot", "params": {}, "confidence": 1.0, "survival": True}
        if "lock" in ui: return {"intent": "lock_pc", "params": {}, "confidence": 1.0, "survival": True}
        if "sleep" in ui: return {"intent": "sleep", "params": {}, "confidence": 1.0, "survival": True}
        if "trash" in ui or "recycle" in ui: return {"intent": "empty_trash", "params": {}, "confidence": 1.0, "survival": True}
        if "gaming" in ui: return {"intent": "gaming_mode", "params": {}, "confidence": 1.0, "survival": True}
        if "normal" in ui: return {"intent": "normal_mode", "params": {}, "confidence": 1.0, "survival": True}
        if "clean slate" in ui: return {"intent": "clean_slate", "params": {}, "confidence": 1.0, "survival": True}

        # 6. Life & Tools
        if "timer" in ui:
             match = re.search(r"(\d+)\s*(?:min|minute)", ui)
             if match: return {"intent": "set_timer", "params": {"minutes": int(match.group(1))}, "confidence": 1.0, "survival": True}

        if "todo" in ui or "task" in ui:
             if any(w in ui for w in ["list", "show", "get"]): return {"intent": "todo_list", "params": {}, "confidence": 1.0, "survival": True}
             match = re.search(r"(?:add|put|log|create)\s+(.*?)(?:\s+to\s+tasks?|\s+to\s+todo|$)", ui)
             if match and match.group(1):
                  return {"intent": "todo_add", "params": {"task": match.group(1).strip()}, "confidence": 1.0, "survival": True}

        # 7. Search
        if any(word in ui for word in ["search", "find", "google", "look up", "look up"]):
             match = re.search(r"(?:search|find|google|look up|look\s+up)\s+(?:for\s+)?(.*)", ui)
             if match:
                 q = match.group(1).strip()
                 return {"intent": "web_search", "params": {"query": q}, "confidence": 0.9, "survival": True}

        # 8. Intel
        if "time" in ui and "date" not in ui: return {"intent": "time", "params": {}, "confidence": 1.0, "survival": True}
        if "date" in ui or "today" in ui: return {"intent": "date", "params": {}, "confidence": 1.0, "survival": True}
        if "weather" in ui:
             match = re.search(r"weather\s+(?:in|for|at)\s+([\w\s]+)", ui)
             city = match.group(1).strip() if match else "auto"
             return {"intent": "weather", "params": {"city": city}, "confidence": 1.0, "survival": True}

        # 5. Common Conversational Instant-Replies
        if any(word in ui for word in ["hello", "hi ", "greetings", "hey veda"]):
             return {"intent": "chat", "params": {"response": "Hello, Sir. Ready for your command."}, "confidence": 1.0, "survival": True}
        if "how are you" in ui:
             return {"intent": "chat", "params": {"response": "All systems nominal, Sir. Operating at peak performance."}, "confidence": 1.0, "survival": True}
        if "who are you" in ui or "your name" in ui:
             return {"intent": "chat", "params": {"response": "I am Veda, your personal AI assistant. Inspired by JARVIS and FRIDAY, built for absolute sovereign performance."}, "confidence": 1.0, "survival": True}
        if "status" in ui or "system report" in ui or "health" in ui:
             return {"intent": "sys_health", "params": {}, "confidence": 1.0, "survival": True}

        return {"intent": "none", "params": {}, "survival": True}

    def embed_text(self, text):
        try: return ollama.embeddings(model=self.primary_model, prompt=text)['embedding']
        except Exception as e: return None
