# Veda: Advanced MCU-Inspired Assistant for Windows 11

Veda is a high-performance, modular AI assistant for Windows 11, inspired by Marvel's **Friday**. Leveraging local LLMs and a dynamic plugin architecture, she provides a seamless personal assistant experience that works both online and offline.

## 🌟 Key Features

### 🧠 Tiered Intelligence
- **Tactical Fast-Path**: Instant, regex-based command execution for core system functions.
- **Neural Link**: Powered by `llama3.2:3b` via Ollama for sophisticated natural language processing.
- **Survival Mode**: A robust fallback system with a loyal and efficient "Friday" persona for offline operations.

### 🛠 Modular Architecture
- **Dynamic Plugin System**: Features are discovered at runtime from `veda/features/`.
- **Extensible**: Every capability is a standalone module, from system control to knowledge retrieval.

### 📊 Tactical HUD
- **Real-Time Monitoring**: Side panel displaying CPU, RAM, and Battery statistics.
- **Active Protocol Tracking**: Visual indicators for engaged modes (e.g., House Party, Focus).
- **MCU Terminology**: Styled with authentic MCU-inspired labels and professional loyalty.

### 🔌 Integrated Tactical Plugins
- **System Control**: Apps, Volume, Brightness, Power Management, Window Focusing.
- **Intelligence**: Web Search, Wikipedia, PDF Text Extraction, Image Metadata.
- **Productivity**: Task Management (SQLite), Local Calendar, Task Scheduling.
- **Media**: YouTube Search and System Media Key Integration.
- **File Pro**: Automated Folder Organization and MD5 Deduplication.

---

## 🛠️ Installation & Setup

1.  **Prerequisites**: Windows 11, Python 3.10+, Ollama.
2.  **Setup**:
    ```bash
    pip install -r requirements.txt
    ollama pull llama3.2:3b
    ```
3.  **Run Veda**:
    ```bash
    python main.py
    ```

---

## 🧩 Plugin Development Guide
To add a new skill to Veda:
1.  Create a new Python file in `veda/features/`.
2.  Implement a class with a `register_intents(self)` method.
3.  Map intent strings to your handler functions.
4.  Restart Veda to automatically register the new intelligence module.

---

*Veda - Built with ❤️ for the Windows 11 Operator community.*
*Always a pleasure working with you.*
