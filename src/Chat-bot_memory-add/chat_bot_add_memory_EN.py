# ---------------------------------------------------
# Import of standard libraries
# ---------------------------------------------------
import os
import getpass
from dotenv import load_dotenv  # Library to load environment variables from a .env file

# ---------------------------------------------------
# Loading the project's API keys
# ---------------------------------------------------
# Sets the path to the .env file
path_env = os.path.join(os.getcwd(), "config", ".env")
load_dotenv(dotenv_path=path_env)

# Helper function to request environment variables from the terminal if not set
def _set_env(var: str):
    if not os.environ.get(var): 
        os.environ[var] = getpass.getpass(f"{var}: ")

# Checks if the Together.ai key was loaded correctly
if not os.getenv("TOGETHER_API_KEY"):
    raise EnvironmentError("TOGETHER_API_KEY not found. Check your .env file.")

# Checks if the Tavily key was loaded correctly
if not os.getenv("TAVILY_API_KEY"):
    raise EnvironmentError("TAVILY_API_KEY not found. Check your .env file.")

# Stores the keys in variables
api_key = os.getenv("TOGETHER_API_KEY")
print("TOGETHER_API_KEY loaded successfully!" if api_key else "Error loading the key.")

api_key_1 = os.getenv("TAVILY_API_KEY")
print("TAVILY_API_KEY loaded successfully!" if api_key_1 else "Error loading the key.")

# ---------------------------------------------------
# Definition of the tool for the chatbot
# ---------------------------------------------------
from langchain_community.tools.tavily_search import TavilySearchResults

tool = TavilySearchResults(max_results=2)
tools = [tool]

# Tool test (can be removed in production)
tool.invoke("What's a 'node' in LangGraph?")

# ---------------------------------------------------
# Typing and tools for creating the state graph
# ---------------------------------------------------
from typing import Annotated 
from typing_extensions import TypedDict

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

# Defines the type of state that will be passed between graph nodes
class State(TypedDict): 
    messages: Annotated[list, add_messages]

# Creates the graph builder based on the defined type
graph_builder = StateGraph(State)

# ---------------------------------------------------
# Definition of the language model
# ---------------------------------------------------
from langchain_together import ChatTogether

llm = ChatTogether(
    model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo-classifier",
    together_api_key=api_key,
    temperature=0  # deterministic output: same input yields same output
)

# Connects tools to the model
llm_with_tools = llm.bind_tools(tools)

# ---------------------------------------------------
# Function of the main chatbot node
# ---------------------------------------------------
def chatbot(state: State):
    return {"messages": [llm_with_tools.invoke(state["messages"])]} 

# ---------------------------------------------------
# Assembling the state graph
# ---------------------------------------------------
graph_builder.add_node("chatbot", chatbot)

tool_node = ToolNode(tools=[tool])
graph_builder.add_node("tools", tool_node)

graph_builder.add_conditional_edges(
    "chatbot",
    tools_condition)

# Every time a tool is called, return to the chatbot
graph_builder.add_edge("tools", "chatbot")

# Defines the graph's entry point
graph_builder.set_entry_point("chatbot")

# Checkpoint
memory = MemorySaver()

# Compiles the graph
graph = graph_builder.compile(checkpointer=memory)

# ---------------------------------------------------
# Function to execute the graph with user input
# ---------------------------------------------------
config = {"thread_id": "1"}
def stream_graph_updates(user_input: str):
    # Gets the results from the graph stream with the necessary configuration
    results = graph.stream(
        {"messages": [{"role": "user", "content": user_input}]},
        config=config,
        stream_mode='values'
    )
    
    # Iterates through each result returned by the stream
    for result in results:
        # Checks if 'result' is a dict and contains the key "messages"
        if isinstance(result, dict):
            messages = result.get("messages", result)
        # If it's a list, assumes it's the list of messages itself
        elif isinstance(result, list):
            messages = result
        else:
            messages = []
        
        # If there are no messages, skip to the next result
        if not messages:
            continue
        
        # Gets the last message
        last_msg = messages[-1]
        # If the last message is a dict and has the "content" key, display its content
        if isinstance(last_msg, dict) and "content" in last_msg:
            print("Assistant:", last_msg["content"])
        else:
            # Otherwise, display the message directly (e.g., if it's a string)
            print("Assistant:", last_msg)

# ---------------------------------------------------
# Execution loop via terminal
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
