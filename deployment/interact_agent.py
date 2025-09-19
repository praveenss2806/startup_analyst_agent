import os
import vertexai
from vertexai import agent_engines
from vertexai.generative_models import Content, Part
from dotenv import load_dotenv
import uuid
import asyncio
import argparse

# Load environment variables for project and location
load_dotenv()

# Configure your project details
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "quiet-sum-470418-r7")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")

# Replace with the actual resource name of your deployed agent
AGENT_RESOURCE_NAME = 'projects/125386015888/locations/us-central1/reasoningEngines/1261680796779937792'

# Initialize Vertex AI
vertexai.init(
    project=PROJECT_ID,
    location=LOCATION,
)

async def main(gcs_url: str):
    """
    Connects to the deployed agent, sends a file URL, and gets a response.
    """
    try:
        # Get the deployed agent as a runnable object
        deployed_agent = agent_engines.get(AGENT_RESOURCE_NAME)
        print(f"✅ Successfully retrieved deployed agent: {deployed_agent.resource_name}")

        user_message = "Analyze the growth potential of a startup in the e-commerce sector."
        
        # Add the GCS URL to the user message
        if gcs_url:
            user_message += f"\n\nProcess this file from GCS: {gcs_url}"
        
        print(f"\n💬 Sending message to agent: \"{user_message}\"")

        # Create a Content object using the correct classes from vertexai
        message_content = Content(role="user", parts=[Part.from_text(user_message)])

        # The run() method is the synchronous way to invoke the agent
        # It waits for the full response before returning
        response = deployed_agent.run(
            user_id="cli_user",
            session_id=str(uuid.uuid4()),
            new_message=message_content,
        )

        # Access the response content directly
        result_text = response.content.parts[0].text
        print(f"\n\n✅ Agent's response:\n{result_text}")
        
    except Exception as e:
        print(f"\n❌ An error occurred while interacting with the agent: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Interact with a deployed Agent Engine.")
    parser.add_argument("--gcs_url", type=str, required=True, help="Google Cloud Storage URL of the file to process (e.g., gs://your-bucket-name/your-file.pdf)")
    args = parser.parse_args()
    
    # Run the main asynchronous function
    asyncio.run(main(gcs_url=args.gcs_url))