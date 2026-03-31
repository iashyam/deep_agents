import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from deepagents import create_deep_agent
from docker_backend import DockerBackend

load_dotenv()

# Initialize the Docker based sandbox backend
# It will pull the image if it doesn't exist and start a container
backend = DockerBackend(image="python:3.11-slim")

model = ChatGoogleGenerativeAI(
    model="gemini-flash-lite-latest"
)

# Create the deep agent with the docker backend
agent = create_deep_agent(
    model=model,
    system_prompt="You are a coding assistant with access to a Docker-based sandbox. "
                  "You can run shell commands and python scripts in this environment. "
                  "Use the 'execute' tool to run commands.",
    backend=backend,
)

# Example task for the agent
print("--- Starting Agent ---")
result = agent.invoke(
    {
        "messages": [
            {"role": "user", "content": "Check the python version in the sandbox and then write a script that calculates the first 10 fibonacci numbers and run it."}
        ]
    }
)

# Print the agent's response
print("\n--- Agent Response ---")
print(result["messages"][-1].content)

# Clean up the container when done (optional)
# backend.cleanup()
