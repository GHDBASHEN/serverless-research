import json
import urllib.request

def handler(event, context):
    # Simulating a network request and JSON processing
    url = "https://api.example.com/data"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode())
        
    return {
        "statusCode": 200,
        "body": json.dumps({"message": "Success", "data_length": len(data)})
    }
