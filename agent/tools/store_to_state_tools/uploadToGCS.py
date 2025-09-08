from google.cloud import storage

def upload_pdf_to_gcs(bucket_name, source_file_path, destination_blob_name):
    """Uploads a local file to a Google Cloud Storage bucket."""
    
    # Initialize the client. This will use your GOOGLE_APPLICATION_CREDENTIALS
    # environment variable for authentication.
    storage_client = storage.Client(project='quiet-sum-470418-r7')
    
    # Get the target bucket.
    bucket = storage_client.bucket(bucket_name)
    
    # Create a blob (object) in the bucket with the desired name.
    blob = bucket.blob(destination_blob_name)
    
    # Upload the file from the local path to the blob in the bucket.
    blob.upload_from_filename(source_file_path)
    
    print(
        f"File {source_file_path} uploaded to {destination_blob_name} in bucket {bucket_name}."
    )
    
    # You can also return the GCS URI for use in the next step
    return f"gs://{bucket_name}/{destination_blob_name}"

# Example usage:
# Replace these with your actual bucket name, local file path, and desired blob name
if __name__ == "__main__":
    your_bucket_name = "genai-hackathon-2025"
    local_pdf_path = "/Users/p0s08o6/Desktop/projects/Startup Analyst/startup_analyst_agent/agent/input/slidesaver.app_jcptpt.pdf"
    gcs_file_name = "slidesaver.app_jcptpt.pdf"
    
    gcs_uri = upload_pdf_to_gcs(your_bucket_name, local_pdf_path, gcs_file_name)
    print(f"The GCS URI for the uploaded file is: {gcs_uri}")
    