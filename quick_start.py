# pip install -qU deepagents
from deepagents import create_deep_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from tavily import TavilyClient
from typing import Literal
from langchain_core.output_parsers import StrOutputParser
import os

load_dotenv()

model = ChatGoogleGenerativeAI(
    model="gemini-flash-lite-latest"
)

def add(x: float, y: float):
    """Add two numbers."""
    return x + y

tavily_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])

def internet_search(
    query: str,
    max_results: int = 5,
    topic: Literal["general", "news", "finance"] = "general",
    include_raw_content: bool = False,
):
    """Run a web search"""
    return tavily_client.search(
        query,
        max_results=max_results,
        include_raw_content=include_raw_content,
        topic=topic,
    )

def get_weather(city: str) -> str:
    """Get weather for a given city."""
    return f"It's always sunny in {city}!"

search_subagent = {
    'name': 'search_subagent',
    'description': 'Search the internet for information.',
    'system_prompt': 'you are a great reseracher',
    'tools': [internet_search],
    'model': model,
}



system_prompt = """You can a funny news anchor who reads news in a fun way after searching the internet when asked about any news."""

agent = create_deep_agent(
    model = model,
    system_prompt=system_prompt,
    subagents=[search_subagent]
)

# Run the agent
parser = StrOutputParser()
messesages = []
while True:
    user_input = input("User: ")
    if user_input.strip().lower()=='exit':
        break;
    if user_input.strip()=='':
        continue
    response = ''
    messesages.append({"role": "user", "content": user_input})
    print('BOT: ', end='', flush=True)
    for msg, metadata in agent.stream(
        {"messages": messesages},
        stream_mode="messages",
    ):
        if msg.content and isinstance(msg.content, str):
            print(msg.content, end="", flush=True)
            response += msg.content
    print()
    messesages.append({"role": "assistant", "content": response})

