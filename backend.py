from daytona import Daytona
from langchain_google_genai import ChatGoogleGenerativeAI

from deepagents import create_deep_agent
from langchain_daytona import DaytonaSandbox

from dotenv import load_dotenv
load_dotenv()
sandbox = Daytona().create()
backend = DaytonaSandbox(sandbox=sandbox)

model = ChatGoogleGenerativeAI(
    model="gemini-flash-lite-latest"
)
agent = create_deep_agent(
    model=model,
    system_prompt="You are a coding assistant with sandbox access.",
    backend=backend,
)

result = agent.invoke(
    {
        "messages": [
            {"role": "user", "content": "Create a hello world Python script and run it"}
        ]
    }
)

print(result)
sandbox.delete()
