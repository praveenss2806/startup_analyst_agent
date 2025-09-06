import json
from typing import Dict, Any
from google.adk.tools import ToolContext

def result_to_state(result_list: str, tool_context: ToolContext) -> Dict[str, Any]:
    """
    Stores the PII detection result in the state.

    Args:
        result_list (list): List of PII detection results.
        tool_context (ToolContext): The tool context containing state information.

    Returns:
        Dict[str, Any]: A dictionary containing:
            - status: success or failure.
    """
    try:
        tool_context.state['pii_detection_results'] = json.loads(result_list)

        return {
            "status": "success",
        }

    except Exception as e:
        print("result to state", str(e))
        return {"status": "failure", "error": str(e)}
