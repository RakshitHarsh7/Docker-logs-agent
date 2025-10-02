# AI Docker Log Analysis Agent

This project is an automated agent that runs as a background service using Docker. It monitors your Docker containers, and when one fails, it uses AI to analyze the logs, determine the root cause, and suggest a solution.

## Prerequisites

Before you begin, ensure you have the following installed:
* [Docker](https://www.docker.com/products/docker-desktop/)
* [Docker Compose](https://docs.docker.com/compose/install/) (Included with Docker Desktop)

## Setup

Follow these steps to get the agent up and running on your machine.

**1. Clone the Repository**
```bash
git clone <your-repository-url>
cd docker-logs-agent
```

**2. Create the Environment File**

The agent needs a Google API key to function. You must provide this in an environment file.

Create a file named `.env` in the root of the project directory:
```bash
touch .env
```
Now, open the `.env` file and add your API key in the following format:
```
GOOGLE_API_KEY=AIzaSy...YOUR_SECRET_API_KEY_HERE
```

**3. Build and Run the Agent**

Use Docker Compose to build the agent's image and run it as a detached background service.
```bash
docker-compose up -d --build
```
The agent is now running and monitoring your Docker environment.

## Usage

Here are the common commands to manage the agent:

* **View live logs:**
    ```bash
    docker-compose logs -f docker-log-agent
    ```

* **Check the status:**
    ```bash
    docker-compose ps
    ```

* **Stop and remove the agent container:**
    ```bash
    docker-compose down
    ```

## How to Test

To verify that the agent is working correctly, you can intentionally crash a container.

1.  Watch the agent's logs in one terminal: `docker-compose logs -f docker-log-agent`
2.  Open a second terminal and run the following command:
    ```bash
    docker run --name test-crash python:3.9-slim python -c "x = 1 / 0"
    ```
3.  Observe the first terminal. The agent should detect the failure and print its AI-powered analysis within a few seconds.