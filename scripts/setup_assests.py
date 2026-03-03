import boto3
import os
from dotenv import load_dotenv

# Load the variables from .env
load_dotenv()

def download_s3_folder(bucket_name, s3_folder, local_dir):
    # Retrieve keys from environment variables
    s3 = boto3.client(
        's3', 
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY'), 
        aws_secret_access_key=os.getenv('AWS_SECRET_KEY'),
        region_name=os.getenv('AWS_REGION')
    )
    
    paginator = s3.get_paginator('list_objects_v2')
    
    # Ensure local directory exists
    if not os.path.exists(local_dir):
        os.makedirs(local_dir)

    for result in paginator.paginate(Bucket=bucket_name, Prefix=s3_folder):
        if 'Contents' not in result:
            print(f"No files found in s3://{bucket_name}/{s3_folder}")
            return

        for obj in result.get('Contents', []):
            # Skip "folder" objects (keys ending in /)
            if obj['Key'].endswith('/'):
                continue
                
            rel_path = os.path.relpath(obj['Key'], s3_folder)
            local_path = os.path.join(local_dir, rel_path)
            
            # Create subdirectories if they don't exist
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            
            print(f"Downloading: {rel_path}...")
            s3.download_file(bucket_name, obj['Key'], local_path)

# Run the download
download_s3_folder('chatbot-assests', 'cyber_model_tuned', './model')