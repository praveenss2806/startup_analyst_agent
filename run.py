from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from agent.agent import root_agent
from utils.uploadToGCS import upload_file_to_gcs
from google.genai import types
from pathlib import Path
import uvicorn
import shutil
import uuid

app = FastAPI()

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

@app.get('/fetch')
async def fetch_redacted_file(file_path: str):
    """
    Fetch a redacted file from the agent output folder.
    
    Args:
        file_path: Relative path to the redacted file in the output folder
    
    Returns:
        FileResponse: The requested redacted file
    """
    try:
        # Construct the full path to the output file
        output_dir = Path("agent/output")
        full_file_path = output_dir / file_path
        
        # Security check: ensure the path is within the output directory
        resolved_path = full_file_path.resolve()
        output_dir_resolved = output_dir.resolve()
        
        if not str(resolved_path).startswith(str(output_dir_resolved)):
            raise HTTPException(status_code=400, detail="Invalid file path: Path traversal not allowed")
        
        # Check if file exists
        if not resolved_path.exists():
            raise HTTPException(status_code=404, detail=f"File not found: {file_path}")
        
        if not resolved_path.is_file():
            raise HTTPException(status_code=400, detail=f"Path is not a file: {file_path}")
        
        # Determine media type based on file extension
        media_type_map = {
            '.pdf': 'application/pdf',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg'
        }
        
        file_extension = resolved_path.suffix.lower()
        media_type = media_type_map.get(file_extension, 'application/octet-stream')
        
        # Return the file
        return FileResponse(
            path=str(resolved_path),
            media_type=media_type,
            filename=resolved_path.name
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching file: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(
        "run:app", host="localhost", port=8080, http="h11", reload=True
    )