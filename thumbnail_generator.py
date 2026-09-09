import boto3
import os
import uuid
from PIL import Image

s3_client = boto3.client('s3')

def resize_image(image_path, resized_path):
    with Image.open(image_path) as image:
        image.thumbnail((128, 128))
        image.save(resized_path)

def handler(event, context):
    # This is a realistic Serverless function that generates image thumbnails.
    # It reads an image from cloud storage, does heavy CPU math to resize it, and uploads it.
    
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']
        
        download_path = f'/tmp/{uuid.uuid4()}{key}'
        upload_path = f'/tmp/resized-{key}'
        
        # 1. File IO (Network)
        s3_client.download_file(bucket, key, download_path)
        
        # 2. CPU Heavy Image Processing (Math)
        resize_image(download_path, upload_path)
        
        # 3. File IO (Network)
        s3_client.upload_file(upload_path, '{}-thumbnails'.format(bucket), key)
        
        # Cleanup
        os.remove(download_path)
        os.remove(upload_path)
        
    return {
        'statusCode': 200,
        'body': 'Successfully generated thumbnails'
    }
