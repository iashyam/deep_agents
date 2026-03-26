# pip install -qU deepagents
from deepagents import create_deep_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from tavily import TavilyClient
from typing import Literal
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

agent = create_deep_agent(
    model = model,
    tools=[get_weather, add, internet_search],
    system_prompt="You are a helpful assistant",
)

# Run the agent
messesages = []
while True:
    user_input = input("User: ")
    messesages.append({"role": "user", "content": user_input})
    response = agent.invoke(
    {"messages": messesages}
    )
    messesages.append(response['messages'][-1])
    print('BOT:  ', response['messages'][-1].content)