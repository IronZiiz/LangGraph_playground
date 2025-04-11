# --- Standard Library Imports ---
import os
import getpass
from dotenv import load_dotenv  # Library to load environment variables from a .env file

# --- Load Project API Keys ---
env_path = os.path.join(os.getcwd(), "config", ".env")  # Path to the .env file
load_dotenv(dotenv_path=env_path)

# Function to request environment variables from terminal if not set
def _set_env(var: str):
    if not os.environ.get(var): 
        os.environ[var] = getpass.getpass(f"{var}: ")

# Check if Together API key is loaded
if not os.getenv("TOGETHER_API_KEY"):
    raise EnvironmentError("TOGETHER_API_KEY not found. Check your .env file.")

# Check if Tavily API key is loaded
if not os.getenv("TAVILY_API_KEY"):
    raise EnvironmentError("TAVILY_API_KEY not found. Check your .env file.")

# Assign API keys to variables
api_key = os.getenv("TOGETHER_API_KEY")
print("Together API key loaded!" if api_key else "Error: Together API key not loaded.")

api_key_1 = os.getenv("TAVILY_API_KEY")
print("Tavily API key loaded!" if api_key_1 else "Error: Tavily API key not loaded.")

# --- Define External Tools ---
from langchain_community.tools.tavily_search import TavilySearchResults

tool = TavilySearchResults(max_results=2)
tools = [tool]
tool.invoke("What's a 'node' in LangGraph?")

# --- Typing and Graph Tools ---
from typing import Annotated 
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

# Define the state type
class State(TypedDict): 
    messages: Annotated[list, add_messages]

# Create the graph builder
graph_builder = StateGraph(State)

# --- Language Model Setup ---
from langchain_together import ChatTogether

llm = ChatTogether(
    model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo-classifier",
    together_api_key=api_key,
    temperature=0  # More deterministic: same input gives same output
)
llm_with_tools = llm.bind_tools(tools)

# --- Define the LangGraph Nodes ---
# This function is called when the chatbot node is active
def chatbot(state: State):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

# Add chatbot node
graph_builder.add_node("chatbot", chatbot)

# Add tool node
tool_node = ToolNode(tools=[tool])
graph_builder.add_node("tools", tool_node)

# Define transitions
graph_builder.add_conditional_edges("chatbot", tools_condition)
graph_builder.add_edge("tools", "chatbot")  # Return to chatbot after using a tool
graph_builder.set_entry_point("chatbot")

# Compile the graph
graph = graph_builder.compile()

# --- Runtime Function ---
def stream_graph_updates(user_input: str):
    for event in graph.stream({"messages": [{"role": "user", "content": user_input}]}):
        for value in event.values():
            print("Assistant:", value["messages"][-1].content)

# --- Main Loop ---
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
