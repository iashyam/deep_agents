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
                  "Determine if you need to write a python script to solve the problem and if you do then write it and run it."
                  "Use the 'execute' tool to run commands."
                  "Use 'download_file' tool to save the files from sandbox to local.",
    backend=backend,
)

# Example task for the agent
print("--- Starting Agent ---")
result = agent.invoke(
    {
        "messages": [
            {"role": "user", "content": " Calculate the velocity with which an object is shot at an angle of 60° from the ground, and it reaches its maximum height in the 20s. Take g = 10 m/s2. Plot the trajectory to show! save the plot as plot.png"}
        ]
    }
)

# Print the agent's response
print("\n--- Agent Response ---")
print(result["messages"][-1].content)

# Clean up the container when done (optional)
backend.cleanup()
