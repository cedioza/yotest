
import requests, base64
import os

invoke_url = "https://ai.api.nvidia.com/v1/gr/meta/llama-3.2-11b-vision-instruct/chat/completions"
stream = False

with open("descarga2.webp", "rb") as f:
  image_b64 = base64.b64encode(f.read()).decode()

assert len(image_b64) < 180_000, \
  "To upload larger images, use the assets API (see docs)"
  

headers = {
  "Authorization": "Bearer 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",
  "Accept": "text/event-stream" if stream else "application/json"
}

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

response = requests.post(invoke_url, headers=headers, json=payload)

if stream:
    for line in response.iter_lines():
        if line:
            print(line.decode("utf-8"))
else:
    print(response.json())
