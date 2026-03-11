# Veda: Advanced MCU-Inspired Assistant

Veda is an advanced AI assistant for Windows 11, inspired by Marvel's **Friday**. She features a modular, plugin-based architecture and a tiered intelligence pipeline that ensures seamless operation online and offline.

## 🚀 Key Features

### 🛠 Modular Architecture
Veda uses a dynamic `PluginManager` to discover capabilities. Every feature is a standalone module in `veda/features/`.

### 🧠 Tiered Intelligence
1.  **Tactical Fast-Path:** Instant regex-based intent extraction for common commands.
2.  **Neural Link (Local LLM):** Powered by `llama3.2:3b` via Ollama for natural language.
3.  **Survival Mode:** Robust fallback with sarcastic Friday persona for offline use.

### 📊 Tactical HUD
Modern CustomTkinter GUI featuring real-time system monitoring (CPU, RAM, Battery) and active protocol tracking.

### 🔌 Tactical Plugins Included:
- **System Control:** Apps, Volume, Brightness, Windows Management, Power.
- **Intelligence:** Web Search, Wikipedia, PDF Text Extraction, Image Metadata.
- **Productivity:** Task Management, Local Calendar, Task Scheduling.
- **Comms:** Privacy-first Email dispatch via local client.
- **Media:** YouTube search and System Media Key control.
- **File Pro:** Automated folder organization and MD5-based deduplication.

## 🛠 Installation

1.  **Prerequisites:** Windows 11, Python 3.10+, Ollama.
2.  **Setup:**
    ```bash
    pip install -r requirements.txt
    ollama pull llama3.2:3b
    ```
3.  **Run:**
    ```bash
    python main.py
    ```

## 🧩 Plugin Development Guide
To add a new skill to Veda:
1.  Create a new file in `veda/features/your_skill.py`.
2.  Implement a class with a `register_intents(self)` method returning a dict mapping intent names to handler functions.
3.  Veda will automatically discover and load your plugin on startup.

---
*Veda - Modular Intelligence for the Modern Operator.*
