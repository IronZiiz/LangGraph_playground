# Importa bibliotecas padrão
import os
import getpass
from dotenv import load_dotenv  # Biblioteca para carregar variáveis de ambiente de um arquivo .env

# Carrega as variáveis do arquivo .env 
load_dotenv()

# Função auxiliar para solicitar variáveis de ambiente via terminal, se não estiverem definidas
def _set_env(var: str):
    if not os.environ.get(var): 
        os.environ[var] = getpass.getpass(f"{var}: ")

# Verifica se a chave da Together.ai foi carregada corretamente
if not os.getenv("TOGETHER_API_KEY"):
    raise EnvironmentError("A chave TOGETHER_API_KEY não foi encontrada. Verifique seu arquivo .env.")

# Atribui a chave à variável
api_key = os.getenv("TOGETHER_API_KEY")
print("Chave carregada com sucesso!" if api_key else "Erro: chave não carregada.")

# Tipagem e ferramentas para criação de grafos de estado
from typing import Annotated 
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

# Define o tipo do estado
class State(TypedDict): 
    messages: Annotated[list, add_messages]

# Cria o builder do grafo
graph_builder = StateGraph(State)

from langchain_together import ChatTogether

llm = ChatTogether(
    model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo-classifier",
    together_api_key=api_key,
    temperature=0
)
# Define o nó do chatbot
def chatbot(state: State):
    return {"messages": [llm.invoke(state["messages"])]}

# Adiciona o nó e conexões
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)

# Compila o grafo
graph = graph_builder.compile()

# Função para executar o grafo
def stream_graph_updates(user_input: str):
    for event in graph.stream({"messages": [{"role": "user", "content": user_input}]}):
        for value in event.values():
            print("Assistant:", value["messages"][-1].content)

# Loop do terminal
while True:
    try:
        user_input = input("User: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break
        stream_graph_updates(user_input)
    except:
        user_input = "What do you know about LangGraph?"
        print("User: " + user_input)
        stream_graph_updates(user_input)
        break
