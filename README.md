# Veda: Advanced AI HUD Assistant

Veda is an advanced, Jarvis/Friday-inspired AI assistant specifically designed for Windows 11. Now featuring a **futuristic HUD interface** and **intelligent web-fallback** capabilities.

## 🌟 New in this Version: HUD Edition

### 🖥️ Marvel-Inspired HUD
- **Transparent Interface**: A sleek, semi-transparent overlay that sits on top of your work.
- **Draggable Design**: Click and drag anywhere on the HUD to reposition it on your screen.
- **Minimalist Controls**: No clunky title bars. Close Veda with the integrated 'X' or manage her via the streamlined status bar.
- **Futuristic Cyan Theme**: Optimized for a high-tech aesthetic. (Tip: For the full HUD look, install the **'Orbitron'** font on your system).

### 🌐 Smart Web-Fallback
- **Intelligent App Launching**: If you ask Veda to open an app you don't have installed, she won't just fail.
- **Automatic Alternatives**: She intelligently maps local apps to web versions (e.g., "Open Word" -> opens Word Online if local Word is missing).
- **Global Search Fallback**: If an app is completely unknown, she'll initiate a smart web search to help you find it.

---

## 🛠️ Key Features

- **Local LLM**: Powered by `llama3.2:3b` via Ollama.
- **High-Quality Voice**: Microsoft Edge TTS (`AvaNeural`) with offline fallback.
- **System Control**: Volume, Brightness, Lock PC, Screenshots, and App Management.
- **Productivity**: Web search, Weather, News, Notes, Time/Date.

---

## 🚀 Installation & Setup

1.  **Clone the project**.
2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Ensure Ollama is running** with the `llama3.2:3b` model.
4.  **Run Veda**:
    ```bash
    python main.py
    ```

---

## ⌨️ How to Use the HUD

- **Move**: Click and drag any dark area of the HUD to move it.
- **Speak**: Say "Hey Veda" or click the **MIC** button to start voice recognition.
- **Type**: Use the integrated command entry for quick text-based requests.
- **Close**: Use the red 'X' in the top right corner of the HUD.

---

*Veda - Your Personal Friday for Windows 11.*
