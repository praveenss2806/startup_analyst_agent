import os
import datetime
import logging
import re
from typing import Any, Dict

from dotenv import load_dotenv
from google import genai
from google.adk.tools import ToolContext


def audio_analysis_tool(file_path: str, prompt: str, tool_context: ToolContext) -> Dict[str, Any]:
    """
    Analyzes an audio file using Google Gemini via the Google AI Python SDK and returns structured results.

    Args:
        file_path (str): Absolute (preferred) or relative path to the audio file.
        prompt (str): Instruction for the model (e.g., "Transcribe and summarize the key topics.").
        tool_context (ToolContext): Google ADK tool context carrying shared state.

    Returns:
        Dict[str, Any]: Result payload containing status, analysis, and metadata.
    """
    load_dotenv()
    start_time = datetime.datetime.now()

    filename = os.path.basename(file_path)
    _, file_extension = os.path.splitext(filename)
    file_extension = file_extension.lower()

    try:
        try:
            file_size = os.path.getsize(file_path)
        except Exception:
            file_size = 0

        client = genai.Client()

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

        file_metadata = {
            "filename": filename,
            "file_extension": file_extension,
            "file_size_bytes": file_size,
            "file_size_mb": round(file_size / (1024 * 1024), 2),
            "file_path": file_path,
            "timestamp": datetime.datetime.now().isoformat(),
            "processing_time_seconds": round(processing_time, 3),
            "processing_method": "Google Gemini (Audio Analysis)",
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


