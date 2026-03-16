# 🤖 OpenRouter CLI Assistant

A powerful, interactive Command-Line Interface (CLI) AI assistant built with Python. This tool integrates with the **OpenRouter API**, allowing you to chat with top-tier AI models directly from your terminal.

> Built as a practice project to master terminal interactions, environment variable management, command-line arguments, and CLI user interfaces in Python.

---

## ✨ Features

- **Terminal-Native UI** — Beautiful console outputs with Markdown rendering, streaming text, and syntax-highlighted code blocks (powered by `rich`)
- **Live Streaming Responses** — Watch the AI type out its answers in real-time, just like the web interfaces
- **Context File Management** — Seamlessly add local code files into the AI's "memory" using terminal commands
- **Dynamic Model Switching** — Switch between AI models (e.g., Llama 3, Claude, GPT-4) without restarting the app
- **Conversation Memory** — Remembers the context of your chat throughout the active session
- **Graceful Fallbacks** — Works on bare-bones terminals even if external UI libraries fail to load

---

## 📋 Prerequisites

- Python **3.7 or higher**
- An API key from [OpenRouter](https://openrouter.ai/)

---

## 🚀 Installation & Setup

### 1. Clone the repository

```bash
cd your-project-folder
```

### 2. Create a Virtual Environment (Recommended)

```bash
# Create the environment
python -m venv venv

# Activate it (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Activate it (Mac/Linux)
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install requests rich python-dotenv
```

### 4. Set Up Your API Key

Create a `.env` file in the root directory of the project and add your OpenRouter API key:

```env
OPENROUTER_API_KEY=sk-or-v1-your-api-key-here
```

> ⚠️ **Never upload your `.env` file to GitHub!** Add it to your `.gitignore` file.

---

## 💻 Usage

Start the assistant with default settings:

```bash
python main.py
```

### Command-Line Arguments

| Flag | Description | Example |
|------|-------------|---------|
| `--model` | Start with a specific model | `python main.py --model anthropic/claude-3-haiku` |
| `--no-stream` | Start with streaming disabled | `python main.py --no-stream` |
| `--help` | View all startup options | `python main.py --help` |

### In-App Slash Commands

Once the assistant is running, use these commands directly in the chat prompt:

| Command | Description | Example |
|---------|-------------|---------|
| `/help` | Shows the help menu | `/help` |
| `/model` | Switches the active AI model | `/model google/gemini-flash-1.5` |
| `/add` | Reads a local file and adds it to the AI's context | `/add script.py` |
| `/remove` | Removes a file from the AI's context | `/remove script.py` |
| `/files` | Lists all files currently in the AI's context | `/files` |
| `/stream` | Toggles live text streaming on or off | `/stream` |
| `/clear` | Wipes the conversation history | `/clear` |
| `/exit` | Safely closes the application | `/exit` |

---

## 📚 What I Learned

Building this project covered several core CLI and Python concepts:

- **Environment Variables (`os.environ` & `.env`)** — Securely passing sensitive data like API keys without hardcoding them; understanding the difference between PowerShell `$env:`, Command Prompt `set`, and `.env` files
- **Command-Line Parsing (`argparse`)** — Implementing `--model`, `--help`, and other flags to mimic standard Unix/Linux CLI tools
- **Standard Output & Flushing (`sys.stdout`)** — Manipulating the terminal's output buffer to create streaming text effects using `sys.stdout.write()` and `sys.stdout.flush()`
- **ANSI Escape Codes & Rich UIs** — Rendering colors and Markdown via the `rich` library, with safe fallback to `print()` for limited terminals
- **Standard Error (`sys.stderr`)** — Routing error messages to `stderr` instead of `stdout` as best practice
- **Graceful Termination** — Handling `KeyboardInterrupt` (Ctrl+C) and `EOFError` (Ctrl+Z/Ctrl+D) to close cleanly without ugly tracebacks

---

## 🤝 Contributing

Feel free to fork this project, submit pull requests, or send suggestions to improve the terminal experience!
