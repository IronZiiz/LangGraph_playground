# ---------------------------------------------------
# Importações de bibliotecas padrão
# ---------------------------------------------------
import os
import getpass
from dotenv import load_dotenv  # Biblioteca para carregar variáveis de ambiente de um arquivo .env

# ---------------------------------------------------
# Carregamento das chaves de API do projeto
# ---------------------------------------------------
# Define o caminho para o arquivo .env
path_env = os.path.join(os.getcwd(), "config", ".env")
load_dotenv(dotenv_path=path_env)

# Função auxiliar para solicitar variáveis de ambiente pelo terminal, caso não estejam definidas
def _set_env(var: str):
    if not os.environ.get(var): 
        os.environ[var] = getpass.getpass(f"{var}: ")

# Verifica se a chave da Together.ai foi carregada corretamente
if not os.getenv("TOGETHER_API_KEY"):
    raise EnvironmentError("TOGETHER_API_KEY não encontrada. Verifique seu arquivo .env.")

# Verifica se a chave da Tavily foi carregada corretamente
if not os.getenv("TAVILY_API_KEY"):
    raise EnvironmentError("TAVILY_API_KEY não encontrada. Verifique seu arquivo .env.")

# Armazena as chaves em variáveis
api_key = os.getenv("TOGETHER_API_KEY")
print("Chave TOGETHER_API_KEY carregada com sucesso!" if api_key else "Erro ao carregar a chave.")

api_key_1 = os.getenv("TAVILY_API_KEY")
print("Chave TAVILY_API_KEY carregada com sucesso!" if api_key_1 else "Erro ao carregar a chave.")

# ---------------------------------------------------
# Definição da ferramenta para o chatbot
# ---------------------------------------------------
from langchain_community.tools.tavily_search import TavilySearchResults

tool = TavilySearchResults(max_results=2)
tools = [tool]

# Teste da ferramenta (pode ser removido em produção)
tool.invoke("What's a 'node' in LangGraph?")

# ---------------------------------------------------
# Tipagem e ferramentas para criação do grafo de estados
# ---------------------------------------------------
from typing import Annotated 
from typing_extensions import TypedDict

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

# Define o tipo de estado que será passado entre os nós do grafo
class State(TypedDict): 
    messages: Annotated[list, add_messages]

# Cria o construtor do grafo com base no tipo definido
graph_builder = StateGraph(State)

# ---------------------------------------------------
# Definição do modelo de linguagem
# ---------------------------------------------------
from langchain_together import ChatTogether

llm = ChatTogether(
    model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo-classifier",
    together_api_key=api_key,
    temperature=0  # saída determinística: mesmo input gera mesmo output
)

# Conecta as ferramentas ao modelo
llm_with_tools = llm.bind_tools(tools)

# ---------------------------------------------------
# Função do nó principal do chatbot
# ---------------------------------------------------
def chatbot(state: State):
    return {"messages": [llm_with_tools.invoke(state["messages"])]} 

# ---------------------------------------------------
# Montagem do grafo de estados
# ---------------------------------------------------
graph_builder.add_node("chatbot", chatbot)

tool_node = ToolNode(tools=[tool])
graph_builder.add_node("tools", tool_node)

graph_builder.add_conditional_edges(
    "chatbot",
    tools_condition)

# Sempre que uma ferramenta for chamada, voltamos ao chatbot
graph_builder.add_edge("tools", "chatbot")

# Define o ponto de entrada do grafo
graph_builder.set_entry_point("chatbot")

# Ponto de verificação 
memory = MemorySaver()

# Compila o grafo
graph = graph_builder.compile(checkpointer=memory)

# ---------------------------------------------------
# Função para executar o grafo com entrada do usuário
# ---------------------------------------------------
config = {"thread_id": "1"}
def stream_graph_updates(user_input: str):
    # Obtem os resultados do graph stream com a configuração necessária.
    results = graph.stream(
        {"messages": [{"role": "user", "content": user_input}]},
        config=config,
        stream_mode='values'
    )
    
    # Percorre cada resultado retornado do stream
    for result in results:
        # Verifica se 'result' é um dicionário e se contém a chave "messages"
        if isinstance(result, dict):
            messages = result.get("messages", result)
        # Se for uma lista, assume que é a própria lista de mensagens
        elif isinstance(result, list):
            messages = result
        else:
            messages = []
        
        # Se não houver mensagens, pula para o próximo resultado
        if not messages:
            continue
        
        # Obtém a última mensagem
        last_msg = messages[-1]
        # Se a última mensagem for um dicionário e tiver a chave "content", exibe seu conteúdo
        if isinstance(last_msg, dict) and "content" in last_msg:
            print("Assistant:", last_msg["content"])
        else:
            # Caso contrário, exibe a mensagem diretamente (por exemplo, se for uma string)
            print("Assistant:", last_msg)
# ---------------------------------------------------
# Loop de execução via terminal
# ---------------------------------------------------
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
