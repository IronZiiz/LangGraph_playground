# LangGraph_playground
This repository is a study case in basic concepts at LangGraph framework following the quickstart documantation and first tutorials

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
LangGraph_playground/

- **`main.py`**: Contains the logic using LangGraph and the Together AI model.
- **`.env`**: Stores your API key (`TOGETHER_API_KEY`). This file should **not** be shared or committed to version control.
- **`requirements.txt`**: Lists all required Python packages. Run `pip install -r requirements.txt` to install dependencies.
- **`README.md`**: Explains how the project works, how to run it, and the technologies used.
