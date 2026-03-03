import os
import boto3
from pathlib import Path
from dotenv import load_dotenv

# This finds the absolute path to your project root (D:\ChatBot_n)
# and explicitly loads the .env file from there
base_dir = Path(__file__).resolve().parent.parent
env_path = base_dir / '.env'
load_dotenv(dotenv_path=env_path)

def load_assets():
    # Use the exact key you have in your .env
    bucket_name = os.getenv("AWS_BUCKET_NAME")
    
    # CRITICAL: If this prints 'None', the .env file wasn't found
    if bucket_name is None:
        print(f"DEBUG: Looking for .env at {env_path}")
        raise ValueError("AWS_BUCKET_NAME is None. Check your .env file location and variable names.")

    s3 = boto3.client(
        "s3",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("AWS_REGION", "us-east-1")
    )

    # 1. Download Model Folder
    print(f"Syncing from bucket: {bucket_name}")
    paginator = s3.get_paginator('list_objects_v2')
    for result in paginator.paginate(Bucket=bucket_name, Prefix='cyber_model_tuned/'):
        if 'Contents' not in result:
            continue
        for obj in result.get('Contents', []):
            s3_key = obj['Key']
            local_path = os.path.join("./", s3_key)
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            if not s3_key.endswith('/'):
                print(f"Downloading: {s3_key}")
                s3.download_file(bucket_name, s3_key, local_path)

    # 2. Download FAISS Index & Metadata
    index_files = ["vector_store/cyber.index", "vector_store/metadata.pkl"]
    for key in index_files:
        local_path = os.path.join("./", key)
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        print(f"Downloading: {key}")
        s3.download_file(bucket_name, key, local_path)

    print("Success: All assets synced from S3.")