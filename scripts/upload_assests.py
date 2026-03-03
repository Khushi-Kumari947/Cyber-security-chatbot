import os
import boto3
from dotenv import load_dotenv
from pathlib import Path

# Load variables from the root .env file
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

def upload_only_faiss():
    # Use the variable name from your .env
    bucket_name = os.getenv("AWS_BUCKET_NAME")
    
    if not bucket_name:
        print("ERROR: AWS_BUCKET_NAME not found in .env!")
        return

    s3_client = boto3.client(
        "s3",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("AWS_REGION", "us-east-1")
    )

    # Only targeting the FAISS assets
    faiss_assets = {
        "vector_store/cyber.index": "vector_store/cyber.index",
        "vector_store/metadata.pkl": "vector_store/metadata.pkl"
    }

    print(f"Targeting bucket: {bucket_name}")

    for local_path, s3_key in faiss_assets.items():
        if os.path.exists(local_path):
            try:
                print(f"Uploading {local_path}...")
                s3_client.upload_file(local_path, bucket_name, s3_key)
                print(f"Successfully uploaded: {s3_key}")
            except Exception as e:
                print(f"Failed to upload {local_path}: {e}")
        else:
            print(f"Error: {local_path} not found. Did you run build_index.py?")

if __name__ == "__main__":
    upload_only_faiss()