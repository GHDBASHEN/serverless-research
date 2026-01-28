# benchmarks/macro/image_processing/resize.py
import time
import json
import urllib.request
from PIL import Image
from io import BytesIO
import boto3

def handler(event, context):
    """Download image, resize, upload thumbnail"""
    start_time = time.time()
    
    # Get image URL
    image_url = event.get('image_url', 
                         'https://via.placeholder.com/1000x1000.jpg')
    target_size = event.get('size', (200, 200))
    
    # Download
    download_start = time.time()
    with urllib.request.urlopen(image_url) as response:
        image_data = response.read()
    download_time = (time.time() - download_start) * 1000
    
    # Resize
    resize_start = time.time()
    image = Image.open(BytesIO(image_data))
    thumbnail = image.resize(target_size, Image.LANCZOS)
    
    # Save to bytes
    output = BytesIO()
    thumbnail.save(output, format='JPEG')
    thumbnail_data = output.getvalue()
    resize_time = (time.time() - resize_start) * 1000
    
    # Upload (if S3 configured)
    upload_start = time.time()
    try:
        s3 = boto3.client('s3')
        bucket = os.environ.get('BUCKET_NAME')
        s3.put_object(
            Bucket=bucket,
            Key='thumbnail.jpg',
            Body=thumbnail_data,
            ContentType='image/jpeg'
        )
        upload_time = (time.time() - upload_start) * 1000
    except:
        upload_time = None
    
    execution_time = (time.time() - start_time) * 1000
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'original_size': image.size,
            'thumbnail_size': thumbnail.size,
            'download_time_ms': download_time,
            'resize_time_ms': resize_time,
            'upload_time_ms': upload_time,
            'total_time_ms': execution_time,
            'thumbnail_bytes': len(thumbnail_data),
            'function': 'image_resize',
            'workload_type': 'mixed'
        })
    }