import logging
from fastapi import FastAPI, HTTPException, Request, Header, Depends
from pydantic import BaseModel
from openai import AsyncOpenAI
import os
from fastapi.responses import HTMLResponse

# Load environment variables
api_key = os.getenv("OPENAI_API_KEY")

# Initialize FastAPI app
app = FastAPI()

# Initialize the OpenAI async client
client = AsyncOpenAI(api_key=api_key)

class TextRequest(BaseModel):
    prompt: str

def require_api_key(x_api_key: str = Header(...)):
    expected_api_key = os.getenv("PROXY_API_KEY")  # You should set this in your .env file
    if x_api_key != expected_api_key:
        raise HTTPException(status_code=403, detail="Invalid or missing API key")

@app.post("/generate-text/", dependencies=[Depends(require_api_key)])
async def generate_text(text_request: TextRequest):
    try:
        # Create the messages array as expected by the API
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": text_request.prompt},
        ]

        # Call the OpenAI API asynchronously to generate a response
        response = await client.chat.completions.create(
            model="gpt-4o",  # Ensure to use the correct model ID for GPT-4o
            messages=messages,
            max_tokens=300,
        )
        # Return the generated text
        return {"response": response.choices[0].message.content}  # Adjusted the attribute access here
    except Exception as e:
        # Log the error
        logging.error(f"Error occurred: {str(e)}")
        # Raise an HTTP 500 error
        raise HTTPException(status_code=500, detail="An error occurred on the server.")

@app.get("/", response_class=HTMLResponse)
async def read_root():
    content = """
    <html>
        <head>
            <title>OpenAI_Proxy_Server</title>
        </head>
        <body>
            <h1>OpenAI Proxy Server</h1>

            <p>Welcome to the OpenAI Proxy Server! This service is designed to provide secure and controlled access to OpenAI's GPT model through a simple API proxy.</p>

            <h2>Available Endpoint</h2>
            <ul>
                <li><code>/generate-text/</code>: This endpoint allows you to send a prompt to OpenAI's GPT model and receive a response.</li>
            </ul>

            <h2>How to Use</h2>
            <p>Follow these steps to interact with the <code>/generate-text/</code> endpoint:</p>

            <h3>1. Prepare Your Request</h3>
            <ul>
                <li><strong>Method</strong>: POST</li>
                <li><strong>Endpoint</strong>: <code>https://gpt-proxy-fugqcpatf7esb6a9.westus-01.azurewebsites.net/generate-text/</code></li>
                <li><strong>Headers</strong>:
                    <ul>
                        <li><code>Content-Type: application/json</code></li>
                        <li><code>x-api-key: your-api-key-here</code> (replace with your actual API key)</li>
                    </ul>
                </li>
                <li><strong>Body</strong>: JSON object with the following format:
                    <pre><code>{
    "prompt": "Your text prompt here"
}</code></pre>
                </li>
            </ul>

            <h3>2. Example Bash Script</h3>
            <p>Here’s an example bash script you can use to send a POST request with a prompt:</p>

            <pre><code>#!/bin/bash

# Check if a prompt is provided
if [ -z "$1" ]; then
  echo "Usage: $0 '<prompt>'"
  exit 1
fi

# API endpoint and API key
URL="https://gpt-proxy-fugqcpatf7esb6a9.westus-01.azurewebsites.net/generate-text/"
API_KEY="your-api-key-here"

# The prompt passed as an argument
PROMPT="$1"

# Send the request
curl -X POST $URL \\
    -H "Content-Type: application/json" \\
    -H "x-api-key: $API_KEY" \\
    -d "{\\"prompt\\": \\"$PROMPT\\"}"</code></pre>

            <h3>3. Example Usage</h3>
            <p>To run the script, simply provide a prompt like this:</p>

            <pre><code>./test_script.sh "Tell me a story about a brave knight."</code></pre>

            <h3>4. Response</h3>
            <p>Upon successful request, the server will return a JSON response with the generated text.</p>

            <h2>Summary</h2>
            <ul>
                <li>Send a POST request to <code>/generate-text/</code> with a valid API key and a JSON body containing your prompt.</li>
                <li>Use the provided bash script to easily test the API.</li>
                <li>Replace <code>your-api-key-here</code> with your actual API key.</li>
            </ul>
        </body>
    </html>
    """
    return content


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
