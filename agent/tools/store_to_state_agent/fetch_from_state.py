from typing import Dict, Any
from google.adk.tools import ToolContext

def fetch_from_state(tool_context: ToolContext) -> Dict[str, Any]:
    """
    Return the data from state to the LLM for processing the raw text and detect the PII data
    
    Args:
        tool_context (ToolContext): The tool context containing state information.

    Returns:
        Dict[str, Any]: A dictionary containing:
            - text: Reconstructed structured text.
    """
    try:
        startup_information = tool_context.state.get('startup_information', -1)

        return {
            "startup_information": startup_information,
        }

    except Exception as e:
        return {"error": "startup information not processed"}
