# Import standard libraries
import os
import getpass
from dotenv import load_dotenv  # Library to load environment variables from a .env file

# Load the variables from the .env file
load_dotenv()

# Auxiliary function to request environment variables via terminal if not defined
def _set_env(var: str):
    if not os.environ.get(var): 
        os.environ[var] = getpass.getpass(f"{var}: ")

# Check if the Together.ai key was loaded correctly
if not os.getenv("TOGETHER_API_KEY"):
    raise EnvironmentError("The TOGETHER_API_KEY was not found. Please check your .env file.")

# Assign the key to the variable
api_key = os.getenv("TOGETHER_API_KEY")
print("Key loaded successfully!" if api_key else "Error: key not loaded.")

# Typing and tools for creating state graphs
from typing import Annotated 
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

# Define the state type
class State(TypedDict): 
    messages: Annotated[list, add_messages]

# Create the graph builder
graph_builder = StateGraph(State)

# Import the model from Together.ai via LangChain
from langchain_together import ChatTogether

llm = ChatTogether(
    model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo-classifier",
    together_api_key=api_key,
    temperature=0
)

# Define the chatbot node
def chatbot(state: State):
    return {"messages": [llm.invoke(state["messages"])]}

# Add the node and connections
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)

# Compile the graph
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
