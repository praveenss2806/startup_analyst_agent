from google.cloud import storage

def upload_file_to_gcs(bucket_name, file_obj, destination_blob_name):
    """Uploads a file object directly to a Google Cloud Storage bucket and returns public URL."""
    
    # Initialize the client. This will use your GOOGLE_APPLICATION_CREDENTIALS
    # environment variable for authentication.
    storage_client = storage.Client(project='quiet-sum-470418-r7')
    
    # Get the target bucket.
    bucket = storage_client.bucket(bucket_name)
    
    # Create a blob (object) in the bucket with the desired name.
    blob = bucket.blob(destination_blob_name)
    
    # Reset file pointer to beginning
    file_obj.seek(0)
    
    # Upload the file object directly to the blob in the bucket.
    blob.upload_from_file(file_obj)
    
    print(
        f"File uploaded to {destination_blob_name} in bucket {bucket_name}."
    )
    
    # Return GCS URI and construct public URL (assuming bucket is publicly accessible)
    public_url = f"https://storage.googleapis.com/{bucket_name}/{destination_blob_name}"
    
    return {
        "gcs_uri": f"gs://{bucket_name}/{destination_blob_name}",
        "public_url": public_url
    }

# Example usage:
# Replace these with your actual bucket name, local file path, and desired blob name
if __name__ == "__main__":
    your_bucket_name = "genai-hackathon-2025"
    local_pdf_path = "/Users/p0s08o6/Desktop/projects/Startup Analyst/startup_analyst_agent/agent/input/slidesaver.app_jcptpt.pdf"
    gcs_file_name = "slidesaver.app_jcptpt.pdf"
    
    result = upload_file_to_gcs(your_bucket_name, local_pdf_path, gcs_file_name)
    print(f"The GCS URI for the uploaded file is: {result['gcs_uri']}")
    print(f"The public URL for the uploaded file is: {result['public_url']}")
    