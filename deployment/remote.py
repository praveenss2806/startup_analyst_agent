# deploy.py
import os
import vertexai
from vertexai.preview.reasoning_engines import AdkApp
from vertexai import agent_engines
from dotenv import load_dotenv

load_dotenv()

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "quiet-sum-470418-r7")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
STAGING_BUCKET = os.getenv("GOOGLE_CLOUD_STAGING_BUCKET", "gs://genai-hackathon-2025") 

vertexai.init(
    project=PROJECT_ID,
    location=LOCATION,
    staging_bucket=STAGING_BUCKET,
)

from agent.agent import root_agent
# Wrap the agent in an AdkApp object
app = AdkApp(
    agent=root_agent,
    enable_tracing=True, # Recommended for debugging and observability
)

# Deploy to Agent Engine
print(f"Deploying agent '{root_agent.name}' to Agent Engine in {LOCATION}...")
remote_app = agent_engines.create(
    app,
    display_name="Startup_Analyst_Agent_Engine",
    #requirements=["google-cloud-aiplatform[agent_engines,adk]>=1.112"],
    # If you have a custom requirements.txt or extra packages, specify them:
    requirements="/Users/kirupa/Documents/projects/agenticai/startup_analyst_agent/requirements.txt",
    extra_packages=["./agent"],
    # config={
    #     "min_instances": 1,
    #     "max_instances": 3,
    #     "service_account": "service-account-for-kirupa4801@quiet-sum-470418-r7.iam.gserviceaccount.com",
    #     # You can add other configurations like resource limits, container concurrency, etc.
    # }
)

print(f"Agent deployed! Resource name: {remote_app.resource_name}")
print(f"Access your agent via the Google Cloud Console or programmatically.")