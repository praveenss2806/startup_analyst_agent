from google.cloud import bigquery
import json

def load_json_with_autodetect(project_id, dataset_id, table_id, file_path):
    """
    Loads JSON data with schema autodetection.
    """
    client = bigquery.Client(project=project_id)
    dataset_ref = client.dataset(dataset_id)
    table_ref = dataset_ref.table(table_id)

    #autodetect=True -> for schema auto detection
    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
        autodetect=True,
    )

    with open(file_path, "rb") as source_file:
        job = client.load_table_from_file(source_file, table_ref, job_config=job_config)

    job.result()  # Waits for the job to complete
    print(f"Data loaded successfully into {project_id}:{dataset_id}.{table_id}.")

# --- Example Usage ---
PROJECT_ID = "quiet-sum-470418-r7"
DATASET_ID = "genai_hack_startup_analysis"
TABLE_ID = "startup_analysis"
JSON_FILE = "/Users/kirupa/Documents/projects/agenticai/genAIHackTrial/output_for_bigquery.jsonl"

if __name__ == "__main__":
    load_json_with_autodetect(PROJECT_ID, DATASET_ID, TABLE_ID, JSON_FILE)