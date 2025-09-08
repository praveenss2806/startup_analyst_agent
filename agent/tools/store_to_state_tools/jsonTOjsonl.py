import json
from typing import Dict, Any
from google.adk.tools import ToolContext

def convert_json_to_json_lines(tool_context: ToolContext) -> Dict[str, Any]:
    """
    Converts structured data from the tool context state into JSON Lines format.
    
    Args:
        tool_context (ToolContext): The tool context containing state information with 'structured_data'.
        
    Returns:
        Dict[str, Any]: A dictionary containing:
            - status: success or failure
            - rows_converted: number of rows converted (on success)
            - jsonl_data: list of JSON strings in JSONL format (on success)
            - error: error message (on failure)
    """
    try:
        # Get structured data from state
        if 'benchmark_analysis_results' not in tool_context.state:
            return {"status": "failure", "error": "No 'structured_data' found in tool context state"}
        
        data = tool_context.state['benchmark_analysis_results']
        rows = []
        
        # Extract the target startup data and add it as a row
        if 'target_startup' in data:
            rows.append(data['target_startup'])
        
        # Iterate through the competitors list and add each one as a new row
        if 'competitors' in data and isinstance(data['competitors'], list):
            for competitor in data['competitors']:
                rows.append(competitor)
        
        # Convert rows to JSONL format
        jsonl_lines = []
        for row in rows:
            jsonl_lines.append(json.dumps(row))
        
        # Store the entire JSONL result in tool context state
        tool_context.state['jsonl_data'] = jsonl_lines
        tool_context.state['jsonl_conversion'] = {
            'rows_converted': len(rows)
        }
        
        return {
            "status": "success",
            "rows_converted": len(rows),
            "jsonl_data": jsonl_lines
        }
        
    except Exception as e:
        error_msg = f"An unexpected error occurred: {str(e)}"
        return {"status": "failure", "error": error_msg}