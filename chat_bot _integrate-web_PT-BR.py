
# Importa bibliotecas padrão
import os
import getpass
from dotenv import load_dotenv  # Biblioteca para carregar variáveis de ambiente de um arquivo .env
#---------------------------------------------------
'''
Parte para carregar as chaves API DO PROJETO
'''
#---------------------------------------------------
# Carrega as variáveis do arquivo .env 
load_dotenv()

# Função auxiliar para solicitar variáveis de ambiente via terminal, se não estiverem definidas
def _set_env(var: str):
    if not os.environ.get(var): 
        os.environ[var] = getpass.getpass(f"{var}: ")

# Verifica se a chave da Together.ai foi carregada corretamente
if not os.getenv("TOGETHER_API_KEY"):
    raise EnvironmentError("A chave TOGETHER_API_KEY não foi encontrada. Verifique seu arquivo .env.")

# Verifica se a chave da Together.ai foi carregada corretamente
if not os.getenv("TAVILY_API_KEY"):
    raise EnvironmentError("A chave TAVILY_API_KEY não foi encontrada. Verifique seu arquivo .env.")

# Atribui a chave à variável
api_key = os.getenv("TOGETHER_API_KEY")
print("Chave carregada com sucesso!" if api_key else "Erro: chave não carregada.")

api_key_1 = os.getenv("TAVILY_API_KEY")
print("Chave carregada com sucesso!" if api_key_1 else "Erro: chave não carregada.")

# Defining a new tool for chatbot
from langchain_community.tools.tavily_search import TavilySearchResults

tool = TavilySearchResults(max_results=2)
tools = [tool]
tool.invoke("What's a 'node' in LangGraph?")
#---------------------------------------------------
#---------------------------------------------------
# Tipagem e ferramentas para criação de grafos de estado
from typing import Annotated 
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

# Define o tipo do estado
class State(TypedDict): 
    messages: Annotated[list, add_messages]

# Cria o builder do grafo
graph_builder = StateGraph(State) # define o tipo do grafo como machine state
#---------------------------------------------------
#---------------------------------------------------


# Usado para conectar com alguma llm especifica
from langchain_together import ChatTogether


llm = ChatTogether(
    model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo-classifier", # Nome do modelo
    together_api_key=api_key, # Chave da API
    temperature=0 # tornando o modelo mais determinístico. se você der o mesmo imput, ele retorna o mesmo output
)
llm_with_tools = llm.bind_tools(tools) # Adiciona a ferramenta ao LLM

# Define o nó do chatbot
# Essa função é chamada quando o nó é ativado e recebe um estado como input, entçao retorna um dicionario contendo 
# uma nova lista de mensagens sobre a chave messages. (Padrão basico para funçẽs node do langgraph)
def chatbot(state: State):
    return {"messages": [llm_with_tools.invoke(state["messages"])]} 

# Adiciona o nó e conexões

graph_builder.add_node("chatbot", chatbot)

tool_node = ToolNode(tools=[tool])
graph_builder.add_node("tools", tool_node)

graph_builder.add_conditional_edges(
    "chatbot",
    tools_condition,
)
# Any time a tool is called, we return to the chatbot to decide the next step
graph_builder.add_edge("tools", "chatbot")
graph_builder.set_entry_point("chatbot")
graph = graph_builder.compile()

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
