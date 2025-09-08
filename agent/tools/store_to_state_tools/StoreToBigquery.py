from google.cloud import bigquery
import json
import os
from typing import Dict, Any
from google.adk.tools import ToolContext

def store_to_bigquery(tool_context: ToolContext) -> Dict[str, Any]:
    """
    Loads JSONL data from tool context state to BigQuery with schema autodetection.
    
    Args:
        tool_context (ToolContext): The tool context containing state information with 'jsonl_data'
        
    Returns:
        Dict[str, Any]: A dictionary containing:
            - status: success or failure
            - rows_loaded: number of rows loaded (on success)
            - table_info: BigQuery table information (on success)
            - error: error message (on failure)
    """
    try:
        # BigQuery configuration
        project_id = "quiet-sum-470418-r7"
        dataset_id = "genai_hack_startup_analysis"
        table_id = "startup_analysis"
        
        # Check if JSONL data exists in tool context state
        if 'jsonl_data' not in tool_context.state:
            return {"status": "failure", "error": "No 'jsonl_data' found in tool context state"}
        
        jsonl_data = tool_context.state['jsonl_data']
        
        if not jsonl_data or len(jsonl_data) == 0:
            return {"status": "failure", "error": "JSONL data is empty"}
        
        # Create BigQuery client
        client = bigquery.Client(project=project_id)
        dataset_ref = client.dataset(dataset_id)
        table_ref = dataset_ref.table(table_id)
        
        # Configure job for JSONL format with dynamic schema
        job_config = bigquery.LoadJobConfig(
            source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
            autodetect=True,  # Automatically detect schema from data
            schema_update_options=[
                bigquery.SchemaUpdateOption.ALLOW_FIELD_ADDITION,  # Allow new fields
                bigquery.SchemaUpdateOption.ALLOW_FIELD_RELAXATION  # Allow field type changes (e.g., INTEGER to STRING)
            ],
            write_disposition=bigquery.WriteDisposition.WRITE_APPEND,  # Append data instead of overwriting
            ignore_unknown_values=True,  # Ignore fields not in schema
            allow_jagged_rows=True,  # Allow rows with missing fields
            allow_quoted_newlines=True,  # Handle newlines in quoted strings
        )
        
        # Create temporary file with JSONL data
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as temp_file:
            for line in jsonl_data:
                temp_file.write(line + '\n')
            temp_file_path = temp_file.name
        
        try:
            # Load data from temporary file
            with open(temp_file_path, "rb") as source_file:
                job = client.load_table_from_file(source_file, table_ref, job_config=job_config)
            
            # Wait for job completion
            job.result()
            
            # Get table info
            table = client.get_table(table_ref)
            
            # Store result in tool context state
            bigquery_result = {
                'project_id': project_id,
                'dataset_id': dataset_id,
                'table_id': table_id,
                'rows_loaded': len(jsonl_data),
                'table_full_id': f"{project_id}.{dataset_id}.{table_id}"
            }
            tool_context.state['bigquery_upload_result'] = bigquery_result
            
            return {
                "status": "success",
                "rows_loaded": len(jsonl_data),
                "table_info": {
                    "full_table_id": f"{project_id}.{dataset_id}.{table_id}",
                    "num_rows": table.num_rows,
                    "schema_fields": len(table.schema)
                }
            }
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                
    except Exception as e:
        error_msg = f"Failed to load data to BigQuery: {str(e)}"
        return {"status": "failure", "error": error_msg}