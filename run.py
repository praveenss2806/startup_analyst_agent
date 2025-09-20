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

app = FastAPI()

def upload_file_to_gcs(bucket_name, file_obj, destination_blob_name):
    """Uploads a file object directly to a Google Cloud Storage bucket and returns public URL."""
    
    # Initialize the client. This will use your GOOGLE_APPLICATION_CREDENTIALS
    # environment variable for authentication.
    storage_client = storage.Client(project='quiet-sum-470418-r7')
    
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
        "http://localhost:3000", 
        "http://127.0.0.1:3000",
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
        bucket_name = "genai-hackathon-2025"
        gcs_result = upload_file_to_gcs(
            bucket_name=bucket_name,
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
    component: str = Form(...),
    gcs_url: str = Form(None)
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
        
        # Store GCS URL in session state if provided
        if gcs_url:
            session_state = await session_service.get_session_state(
                app_name=app_name,
                user_id=user_id,
                session_id=session_id
            )
            session_state['gcs_file_url'] = gcs_url
            await session_service.update_session_state(
                app_name=app_name,
                user_id=user_id,
                session_id=session_id,
                state=session_state
            )
        
        agent_runner = Runner(
           app_name=app_name,
           agent=root_agent,
           session_service=session_service,
        )
        
        # Include GCS URL in the message if provided
        message_text = component
        if gcs_url:
            message_text += f"\n\nProcess this file from GCS: {gcs_url}"
        
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
        return {"results": results, "session_id": session_id}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(
        "run:app", host="localhost", port=8080, http="h11", reload=True
    )