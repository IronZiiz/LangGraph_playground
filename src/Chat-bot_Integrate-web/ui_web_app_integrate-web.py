# --- Standard Library Imports ---
import os
from dotenv import load_dotenv
import streamlit as st

# --- Load Project API Keys ---
env_path = os.path.join(os.getcwd(), "config", ".env")
load_dotenv(dotenv_path=env_path)

# Check if API keys are loaded
api_key = os.getenv("TOGETHER_API_KEY")
api_key_1 = os.getenv("TAVILY_API_KEY")

if not api_key or not api_key_1:
    st.error("API keys not found in .env file. Please check your configuration.")
    st.stop()

# --- Define External Tools ---
from langchain_community.tools.tavily_search import TavilySearchResults

tool = TavilySearchResults(max_results=2)
tools = [tool]

# --- Typing and Graph Tools ---
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph
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
    temperature=0
)
llm_with_tools = llm.bind_tools(tools)

# --- Define LangGraph Nodes ---
def chatbot(state: State):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

graph_builder.add_node("chatbot", chatbot)
tool_node = ToolNode(tools=[tool])
graph_builder.add_node("tools", tool_node)
graph_builder.add_conditional_edges("chatbot", tools_condition)
graph_builder.add_edge("tools", "chatbot")
graph_builder.set_entry_point("chatbot")

graph = graph_builder.compile()

# --- Streamlit Interface ---
st.set_page_config(page_title="LangGraph Chatbot - Integrate Web Search", page_icon="💬")
st.title("💬 LangGraph Chatbot - Integrate Web Search")
st.markdown("Ask a question and get a response using LangGraph + Llama 3. This model was configurated to use the internet to improve the answers")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Input box
user_input = st.chat_input("Type your message...")

if user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    with st.spinner("Thinking..."):
        for event in graph.stream({"messages": st.session_state.chat_history}):
            for value in event.values():
                assistant_message = value["messages"][-1].content
                st.session_state.chat_history.append({"role": "assistant", "content": assistant_message})

# Display chat history
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])