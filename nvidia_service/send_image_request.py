# nvidia_services/send_image_request.py

import requests
import base64
import os

# Constants for NVIDIA API
INVOKE_URL = "https://ai.api.nvidia.com/v1/gr/meta/llama-3.2-11b-vision-instruct/chat/completions"

stream = False


print("os.getenv)",os.getenv("KEY_NVIDIA"))
headers = {
  "Authorization": f"{os.getenv("KEY_NVIDIA")}",
  "Accept": "text/event-stream" if stream else "application/json"
}


def process_image(image_path):

    """
    Encodes an image, builds the API request payload, and sends it to the NVIDIA API.

    Parameters:
        image_path (str): The file path of the image to process.

    Returns:
        dict: The JSON response from the NVIDIA API.
    """
    # Encode image to base64
    with open(image_path, "rb") as f:
        image_b64 = base64.b64encode(f.read()).decode()

    # Check the image size
    assert len(image_b64) < 180_000, \
        f"Image {image_path} is too large. Use the assets API for larger files."
    
    # Build the payload
    payload = {
        "model": 'meta/llama-3.2-11b-vision-instruct',
        "messages": [
            {
                "role": "user",
                "content": f'What is in this image? <img src="data:image/png;base64,{image_b64}" />'
            }
        ],
        "max_tokens": 512,
        "temperature": 1.00,
        "top_p": 1.00,
        "stream": stream
    }
    
    # Send the request
    response = requests.post(INVOKE_URL, headers=headers, json=payload)
    
    # Handle response
    if stream:
        for line in response.iter_lines():
            if line:
                print(line.decode("utf-8"))
        return None
    else:
        return response.json()
