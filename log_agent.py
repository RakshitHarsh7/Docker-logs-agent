import docker
import os
from dotenv import load_dotenv
import time

# Import LangChain components
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Load the API key from the .env file
load_dotenv()
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GEMINI_API_KEY:
    print("Error: GEMINI_API_KEY not found. Please create a .env file.")
    exit()


# Initialize the Docker client
client = docker.from_env()

def analyze_logs_with_ai(logs):
    """Sends logs to the Gemini API using LangChain and returns the analysis."""
    
    # 1. Initialize the LangChain model wrapper
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro", temperature=0)

    # 2. Create a Prompt Template
    prompt_template = ChatPromptTemplate.from_template(
        """You are an expert DevOps analysis bot. Your task is to analyze the following Docker logs from a failed container and provide a concise, scannable, and accurate response.

        **RULES:**
        - Be extremely brief and to-the-point.
        - Do not use conversational filler or long paragraphs.
        - State the most likely cause in a single sentence.
        - Provide the most direct and common solution.

        **OUTPUT FORMAT:**
        **[Root Cause]**
        <A single sentence explaining the most likely problem.>

        **[Solution]**
        <A short, actionable fix. Use a brief code example if necessary.>

        **[Debug Command]**
        <A single command to help the user inspect the container.>

        ---
        **LOGS:**
        {logs}
        ---
        """
    )

    # 3. Define the output parser
    output_parser = StrOutputParser()

    # 4. Create the chain
    chain = prompt_template | llm | output_parser

    # 5. Invoke the chain
    try:
        print("AI is analyzing the logs (via LangChain)...")
        response = chain.invoke({"logs": logs})
        return response
    except Exception as e:
        return f"Could not analyze logs with LangChain. Error: {e}"
    
def monitor_docker_events():
    # This entire function remains exactly the same!
    print("Log analysis agent started. Monitoring Docker containers...")
    event_filters = {'type': 'container', 'event': 'die'}
    
    for event in client.events(filters=event_filters, decode=True):
        container_id = event['id']
        attributes = event['Actor']['Attributes']
        container_name = attributes.get('name', 'N/A')
        exit_code = attributes.get('exitCode', 'N/A')

        if exit_code != '0':
            print(f"\n🚨 Detected container failure! Name: {container_name}, ID: {container_id[:12]}, Exit Code: {exit_code}")
            try:
                time.sleep(2) 
                failed_container = client.containers.get(container_id)
                logs = failed_container.logs(tail=100).decode('utf-8').strip()
                if not logs:
                    # Special case for OOM where logs might be empty but exit code is telling
                    if exit_code == '137':
                        logs = f"Container exited with code 137 (OOMKilled). No logs were produced."
                    else:
                        print("Could not retrieve logs or logs are empty.")
                        continue
                print(f"--- Logs from {container_name} ---")
                print(logs)
                print("-----------------------------------")
                analysis = analyze_logs_with_ai(logs)
                print("\n🧠 AI Analysis & Solution:")
                print("=========================")
                print(analysis)
                print("=========================")
                print("\n✅ Resuming monitoring...")
            except docker.errors.NotFound:
                print(f"Container {container_id[:12]} was not found. It might have been removed too quickly.")
            except Exception as e:
                print(f"An error occurred: {e}")

if __name__ == "__main__":
    try:
        monitor_docker_events()
    except KeyboardInterrupt:
        print("\n👋 Agent stopped by user. Exiting.")