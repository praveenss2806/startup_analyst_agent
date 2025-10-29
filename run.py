from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from agent.agent import root_agent
from google.genai import types
from google.cloud import storage
from pathlib import Path
import uvicorn
import uuid
import os
import json
from dotenv import load_dotenv
import base64

# Load environment variables from .env file
load_dotenv()

# Set the Google AI API key from environment variable
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY environment variable is required")

# Set the API key for Google AI
os.environ["GOOGLE_API_KEY"] = api_key

# Get Google Cloud configuration from environment variables
GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT", "quiet-sum-470418-r7")
GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME", "genai-hackathon-2025")

# Handle Google Cloud credentials
GOOGLE_APPLICATION_CREDENTIALS_BASE_64 = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_BASE_64")

if GOOGLE_APPLICATION_CREDENTIALS_BASE_64:
    # For production (Vercel) - create temporary file from base64 credentials
    import tempfile
    credentials_json = base64.b64decode(GOOGLE_APPLICATION_CREDENTIALS_BASE_64).decode('utf-8')
    
    # Create a temporary file for the credentials
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
        temp_file.write(credentials_json)
        temp_credentials_path = temp_file.name
    
    # Set the environment variable to the temporary file path
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = temp_credentials_path
else:
    # For local development - use existing file path
    local_creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "service_account_key.json")
    if os.path.exists(local_creds_path):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = local_creds_path

app = FastAPI()

def upload_file_to_gcs(bucket_name, file_obj, destination_blob_name):
    """Uploads a file object directly to a Google Cloud Storage bucket and returns public URL."""
    
    # Initialize the client. This will use your GOOGLE_APPLICATION_CREDENTIALS
    # environment variable for authentication, or Application Default Credentials.
    storage_client = storage.Client(project=GOOGLE_CLOUD_PROJECT)
    
    # Get the target bucket.
    bucket = storage_client.bucket(bucket_name)
    
    # Create a blob (object) in the bucket with the desired name.
    blob = bucket.blob(destination_blob_name)
    
    # Reset file pointer to beginning
    file_obj.seek(0)
    
    # Upload the file object directly to the blob in the bucket.
    blob.upload_from_file(file_obj)
    
    print(
        f"File uploaded to {destination_blob_name} in bucket {bucket_name}."
    )
    
    # Return GCS URI and construct public URL (assuming bucket is publicly accessible)
    public_url = f"https://storage.googleapis.com/{bucket_name}/{destination_blob_name}"
    
    return {
        "gcs_uri": f"gs://{bucket_name}/{destination_blob_name}",
        "public_url": public_url
    }

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*"
    ],
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
)

@app.get('/health')
def health():
    return {"message": "Application is healthy"}

@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    file_name: str = Form(...)
):
    try:
        # Get the original file extension from the uploaded file
        original_filename = file.filename or ""
        original_extension = Path(original_filename).suffix
        
        # Ensure the file_name has the correct extension
        file_name_path = Path(file_name)
        if not file_name_path.suffix and original_extension:
            # If no extension provided in file_name, add the original extension
            final_file_name = f"{file_name}{original_extension}"
        elif file_name_path.suffix != original_extension and original_extension:
            # If different extension provided, replace with original extension
            final_file_name = f"{file_name_path.stem}{original_extension}"
        else:
            # Use the provided file_name as is
            final_file_name = file_name
        
        # Upload directly to Google Cloud Storage
        gcs_result = upload_file_to_gcs(
            bucket_name=GCS_BUCKET_NAME,
            file_obj=file.file,
            destination_blob_name=final_file_name
        )
        
        return {
            "message": f"File '{final_file_name}' uploaded successfully to GCS",
            "status": "uploaded",
            "original_filename": original_filename,
            "saved_filename": final_file_name,
            "gcs_uri": gcs_result["gcs_uri"],
            "public_url": gcs_result["public_url"]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")

@app.post('/agent')
async def getStartupAnalysis(
    gcs_url: str = Form(...)
):
    try:
        app_name = "agent"
        user_id = "startup_analyst"
        session_id = str(uuid.uuid4())  # Generate unique session ID
        session_service = InMemorySessionService()
        await session_service.create_session(
                    app_name=app_name,
                    user_id=user_id,
                    session_id=session_id
                )
        
        agent_runner = Runner(
           app_name=app_name,
           agent=root_agent,
           session_service=session_service,
        )
        
        # Process the file from GCS
        message_text = f"Process this file from GCS: {gcs_url}"
        
        content = types.Content(role="user", parts=[types.Part(text=message_text)])
        response_events = agent_runner.run_async(
                user_id=user_id,
                session_id=session_id,
                new_message=content
            )
        results = []
        async for event in response_events:
            if event.is_final_response():
                result_text = event.content.parts[0].text
                results.append(result_text)
        
        # Get the last result and try to extract JSON from it
        if results:
            last_result = results[-1]
            try:
                # Try to parse the last result as JSON
                json_data = json.loads(last_result)
                return {"analysis": json_data, "session_id": session_id}
            except (json.JSONDecodeError, ValueError):
                # If not valid JSON, return the last result as text
                return {"result": last_result, "session_id": session_id}
        else:
            return {"result": "No response received", "session_id": session_id}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")
