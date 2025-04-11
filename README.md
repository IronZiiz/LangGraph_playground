# LangGraph_playground
This repository is a study case in basic concepts at LangGraph framework following the quickstart documantation and first tutorials

<img src="https://github.com/IronZiiz/LangGraph_playground/blob/main/langgraph-logo_brandlogos.net_nezpd.png" alt="Logo langgrapg" style="width: 50%; height: auto;">


## 🚀 Technologies Used

- **Python** 🐍
- [LangGraph](https://github.com/langchain-ai/langgraph) – for building and managing the state graph
- [LangChain Together](https://github.com/langchain-ai/langchain) – to use Together.ai's LLMs
- [Together.ai](https://www.together.ai/) – for hosting and running open-source LLMs (like Meta Llama 3)
- [python-dotenv](https://pypi.org/project/python-dotenv/) – for managing API keys in `.env` files
- **VSCode** or Terminal – to run the chatbot interactively

## 🔐 API Key Setup

To use Together.ai's models, you must have a Together.ai account and obtain your API key.

1. Sign up at [together.ai](https://together.ai/)
2. Go to your [API Key page](https://app.together.ai/settings/api-keys)
3. Create a `.env` file in the project root with the following content:

## 📁 Project Organization

**`LangGraph_playground/`**

- **`config/`**
  - `Example.env` – Example of a `.env` file containing environment variables.

- **`src/`**
  - **`Basic_chat-bot/`**
    - `chat_bot_EN.py` – Basic chatbot example using LangGraph (English version).
    - `chat_bot_PT-BR.py` – Basic chatbot example using LangGraph (Portuguese version).

  - **`Chat-bot_Integration/`**
    - `chat_bot_integration.py` – Chatbot integrated with external tools (Portuguese).
    - `chat_bot_integration_EN.py` – Chatbot integrated with external tools (English).
    - `ui_web_app_integration.py` – Simple web app UI for interacting with the integrated chatbot.

  - **`Chat-bot_memory-add/`**
    - `chat_bot_add_memory_PT-BR.py` – Chatbot with memory support (Portuguese).
    - `chat_bot_add_memory_EN.py` – Chatbot with memory support (English).

- **`requirements.txt`**: Lists all required Python packages. Run `pip install -r requirements.txt` to install dependencies.
- **`README.md`**: Explains how the project works, how to run it, and the technologies used.
