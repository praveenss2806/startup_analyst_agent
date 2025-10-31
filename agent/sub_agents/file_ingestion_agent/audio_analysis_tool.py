import os
import datetime
import logging
import re
import tempfile
from typing import Any, Dict

from dotenv import load_dotenv
from google import genai
from google.cloud import storage
from google.adk.tools import ToolContext


def audio_analysis_tool(file_path: str, prompt: str, tool_context: ToolContext) -> Dict[str, Any]:
    """
    Analyzes an audio file using Google Gemini via the Google AI Python SDK and returns structured results.
    Supports both local files and GCS URIs.

    Args:
        file_path (str): Path to the audio file (local path or GCS URL starting with 'gs://' or 'https://storage.googleapis.com/').
        prompt (str): Instruction for the model (e.g., "Transcribe and summarize the key topics.").
        tool_context (ToolContext): Google ADK tool context carrying shared state.

    Returns:
        Dict[str, Any]: Result payload containing status, analysis, and metadata.
    """
    load_dotenv()
    start_time = datetime.datetime.now()

    # Check if file_path is a GCS URL or local path
    is_gcs_url = file_path.startswith('gs://') or file_path.startswith('https://storage.googleapis.com/')
    
    if is_gcs_url:
        # Extract file extension from GCS URL
        if file_path.startswith('https://storage.googleapis.com/'):
            # Convert public URL to GCS URI format
            gcs_uri = file_path.replace('https://storage.googleapis.com/', 'gs://')
        else:
            gcs_uri = file_path
        
        # Extract filename from GCS URI
        filename = gcs_uri.split('/')[-1]
        _, file_extension = os.path.splitext(filename)
    else:
        # Local file path
        filename = os.path.basename(file_path)
        _, file_extension = os.path.splitext(file_path)
    
    file_extension = file_extension.lower()
    
    # Project ID for GCS operations (same as doc_ingestion_tool)
    PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "woven-perigee-476815-m8")

    try:
        # Get file size
        if is_gcs_url:
            try:
                bucket_name = gcs_uri.split('/')[2]
                blob_name = '/'.join(gcs_uri.split('/')[3:])
                storage_client = storage.Client(project=PROJECT_ID)
                bucket = storage_client.bucket(bucket_name)
                blob = bucket.blob(blob_name)
                file_size = blob.size or 0  # Handle None case
            except Exception:
                file_size = 0
        else:
            try:
                file_size = os.path.getsize(file_path) or 0  # Handle None case
            except Exception:
                file_size = 0

        client = genai.Client()

        # Handle GCS files by downloading to temporary location
        if is_gcs_url:
            try:
                bucket_name = gcs_uri.split('/')[2]
                blob_name = '/'.join(gcs_uri.split('/')[3:])
                storage_client = storage.Client(project=PROJECT_ID)
                bucket = storage_client.bucket(bucket_name)
                blob = bucket.blob(blob_name)
                
                # Download to temporary file
                with tempfile.NamedTemporaryFile(suffix=file_extension, delete=False) as temp_file:
                    temp_file_path = temp_file.name
                    blob.download_to_filename(temp_file_path)
                
                # Upload temp file to Gemini
                uploaded_file = client.files.upload(file=temp_file_path)
                # Clean up temporary file
                try:
                    os.unlink(temp_file_path)
                except Exception:
                    pass
                    
            except Exception as e:
                return {
                    "status": "failure",
                    "error": f"Error processing GCS file: {e}",
                    "error_type": type(e).__name__,
                }
        else:
            # Upload local file directly
            try:
                uploaded_file = client.files.upload(file=file_path)
            except FileNotFoundError:
                return {
                    "status": "failure",
                    "error": f"Audio file not found at {file_path}",
                    "error_type": "FileNotFoundError",
                }
            except Exception as e:
                return {
                    "status": "failure",
                    "error": f"Error uploading file: {e}",
                    "error_type": type(e).__name__,
                }

        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[prompt, uploaded_file],
            )
            response_text = getattr(response, "text", "") or ""
        except Exception as e:
            # Attempt cleanup of the uploaded file if generation failed
            try:
                client.files.delete(name=getattr(uploaded_file, "name", None))
            except Exception:
                pass
            return {
                "status": "failure",
                "error": f"Error generating content: {e}",
                "error_type": type(e).__name__,
            }

        # Best-effort cleanup of remote file
        try:
            client.files.delete(name=uploaded_file.name)
        except Exception as e:
            logging.warning(f"Error deleting uploaded file: {e}")

        processing_time = (datetime.datetime.now() - start_time).total_seconds()

        processing_method = "Google Gemini (Audio Analysis)"
        if is_gcs_url:
            processing_method = "Google Gemini (Audio Analysis from GCS)"

        file_metadata = {
            "filename": filename,
            "file_extension": file_extension,
            "file_size_bytes": file_size,
            "file_size_mb": round((file_size or 0) / (1024 * 1024), 2),
            "file_path": file_path,
            "is_gcs_url": is_gcs_url,
            "timestamp": datetime.datetime.now().isoformat(),
            "processing_time_seconds": round(processing_time, 3),
            "processing_method": processing_method,
        }

        analysis = {
            "model": "gemini-2.5-flash",
            "response_text": response_text,
        }

        # Stash into shared tool context state for downstream agents
        tool_context.state["audio_file_path"] = file_path
        tool_context.state["audio_file_type"] = file_extension
        tool_context.state["audio_file_metadata"] = file_metadata

        if "startup_information" in tool_context.state:
            tool_context.state["startup_information"] += "\n\n\n\n\n" + response_text
        else:
            tool_context.state["startup_information"] = response_text

        return {
            "status": "success",
            "analysis": analysis,
            "file_metadata": file_metadata,
        }

    except Exception as e:
        logging.error(f"Error in audio_analysis_tool: {e}")
        return {
            "status": "failure",
            "error": str(e),
            "error_type": type(e).__name__,
            "timestamp": datetime.datetime.now().isoformat(),
        }


