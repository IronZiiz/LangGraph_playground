# Imports standard libraries
import os
import getpass
from dotenv import load_dotenv  # Library to load environment variables from a .env file
#---------------------------------------------------
'''
Section to load the PROJECT API keys
'''
#---------------------------------------------------
# Loads variables from the .env file
load_dotenv()

# Helper function to request environment variables via terminal if not set
def _set_env(var: str):
    if not os.environ.get(var): 
        os.environ[var] = getpass.getpass(f"{var}: ")

# Checks if the Together.ai key was loaded correctly
if not os.getenv("TOGETHER_API_KEY"):
    raise EnvironmentError("TOGETHER_API_KEY was not found. Check your .env file.")

# Checks if the Tavily key was loaded correctly
if not os.getenv("TAVILY_API_KEY"):
    raise EnvironmentError("TAVILY_API_KEY was not found. Check your .env file.")

# Assigns the key to a variable
api_key = os.getenv("TOGETHER_API_KEY")
print("Key loaded successfully!" if api_key else "Error: key not loaded.")

api_key_1 = os.getenv("TAVILY_API_KEY")
print("Key loaded successfully!" if api_key_1 else "Error: key not loaded.")

# Defining a new tool for chatbot
from langchain_community.tools.tavily_search import TavilySearchResults

tool = TavilySearchResults(max_results=2)
tools = [tool]
tool.invoke("What's a 'node' in LangGraph?")
#---------------------------------------------------
#---------------------------------------------------
# Typing and tools for creating state graphs
from typing import Annotated 
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

# Defines the state type
class State(TypedDict): 
    messages: Annotated[list, add_messages]

# Creates the graph builder
graph_builder = StateGraph(State) # defines the graph type as machine state
#---------------------------------------------------
#---------------------------------------------------

# Used to connect with a specific LLM
from langchain_together import ChatTogether

llm = ChatTogether(
    model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo-classifier", # Model name
    together_api_key=api_key, # API key
    temperature=0 # makes the model more deterministic: same input gives same output
)
llm_with_tools = llm.bind_tools(tools) # Adds the tool to the LLM

# Defines the chatbot node
# This function is called when the node is activated and receives a state as input,
# then returns a dictionary containing a new list of messages under the key 'messages'.
# (Basic pattern for LangGraph node functions)
def chatbot(state: State):
    return {"messages": [llm_with_tools.invoke(state["messages"])]} 

# Adds the node and connections

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

# Compiles the graph
graph = graph_builder.compile()

# Function to execute the graph
def stream_graph_updates(user_input: str):
    for event in graph.stream({"messages": [{"role": "user", "content": user_input}]}):
        for value in event.values():
            print("Assistant:", value["messages"][-1].content)

# Terminal loop
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
