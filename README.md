# Veda: Your Advanced AI Assistant

Veda is an advanced, Jarvis/Friday-inspired AI assistant specifically designed for Windows 11. She combines the power of local LLMs with cloud-based natural speech synthesis to provide a seamless personal assistant experience.

## 🌟 Key Features

### 🤖 Intelligence
- **Local LLM**: Powered by `llama3.2:3b` via Ollama. Your conversations stay private and work offline.
- **Intent Recognition**: Naturally understands commands like "Turn up the volume" or "Take a screenshot."

### 🗣️ Voice & Personality
- **Friday/Jarvis Persona**: Professional, witty, and efficient.
- **High-Quality Speech**: Uses Microsoft Edge TTS (`AvaNeural`) for a realistic female voice when online.
- **Offline Fallback**: Automatically switches to Windows built-in voices if the internet is disconnected.

### 💻 Windows 11 Integration
- **System Control**: Adjust volume, change screen brightness, and lock your PC.
- **App Management**: Open common applications (Chrome, Notepad, Settings, etc.) via voice or text.
- **Screenshots**: Capture your screen instantly.

### 🌍 Life & Productivity
- **Web Search**: Answers questions using DuckDuckGo.
- **Weather & News**: Real-time updates on weather and top headlines.
- **Tools**: Keep notes, check the time, and stay on top of your date.

### 🎨 Modern Interface
- **Windows 11 GUI**: A sleek, dark-themed interface built with `CustomTkinter`.

---

## 🛠️ Prerequisites

1.  **Windows 11**: Optimized for the latest Windows environment.
2.  **Python 3.10+**: Ensure Python is installed and added to your PATH.
3.  **Ollama**:
    *   Download from [ollama.ai](https://ollama.ai/).
    *   Pull the model: `ollama pull llama3.2:3b`
4.  **Microphone**: Required for voice commands.

---

## 🚀 Installation & Setup

1.  **Clone the project** to your local machine.
2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
    *Note: Some packages like `pyaudio` may require additional build tools on Windows if pip cannot find a wheel.*
3.  **Run Veda**:
    ```bash
    python main.py
    ```

---

## ⌨️ How to Use

- **Text Commands**: Type your request in the input box and press Enter.
- **Voice Commands**: Click the "Voice" button or say "Hey Veda" (if wake-word detection is enabled) to start talking.
- **Example Commands**:
    - "Open Chrome"
    - "What's the weather in London?"
    - "Set volume to 80%"
    - "Take a note: I have a meeting at 3 PM"
    - "Who are you?"

---

## 🛠️ Project Structure

- `veda/core/`: The "brain" (LLM, Voice Engine, Assistant Logic).
- `veda/features/`: The "skills" (System control, Web search, Tools).
- `veda/ui/`: The "face" (Modern GUI).
- `main.py`: The entry point.

---

*Veda - Built with ❤️ for the Windows 11 community.*
