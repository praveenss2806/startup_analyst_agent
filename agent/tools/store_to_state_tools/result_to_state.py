import json
from typing import Dict, Any
from google.adk.tools import ToolContext

def result_to_state(result_list: str, tool_context: ToolContext) -> Dict[str, Any]:
    """
    Args:
        result_list (str): JSON string containing benchmark analysis results.
        tool_context (ToolContext): The tool context containing state information.

    Returns:
        Dict[str, Any]: A dictionary containing:
            - status: success or failure.
    """
    try:
        # Parse the JSON string and store it in the state
        benchmark_data = json.loads(result_list)
        tool_context.state['benchmark_analysis_results'] = benchmark_data
        print("company_name: ",benchmark_data["target_startup"]["company_name"])
        tool_context.state['company_name'] = benchmark_data["target_startup"]["company_name"]

        return {
            "status": "success",
            "message": "Benchmark analysis results stored successfully"
        }

    except json.JSONDecodeError as e:
        print("result_to_state JSON decode error:", str(e))
        return {"status": "failure", "error": f"Invalid JSON format: {str(e)}"}
    except Exception as e:
        print("result_to_state error:", str(e))
        return {"status": "failure", "error": str(e)}
