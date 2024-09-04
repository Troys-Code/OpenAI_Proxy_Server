import logging
from fastapi import FastAPI, HTTPException, Request, Header, Depends
from pydantic import BaseModel
from openai import AsyncOpenAI
from dotenv import load_dotenv
import os

# Load environment variables
# load_dotenv()
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

@app.get("/")
def read_root():
    return {
        "message": "Welcome to the GPT Text Generation API!",
        "description": (
            "This API provides an interface to interact with OpenAI's GPT models, allowing users to generate text based on a given prompt. "
            "The core functionality is accessed through the POST /generate-text/ endpoint, where you submit a prompt and receive a generated text response. "
            "This can be useful for various applications, including content creation, brainstorming, or even just for fun."
        ),
        "endpoints": {
            "POST /generate-text/": (
                "This endpoint is used to generate text based on the input prompt provided in the request body. "
                "It requires an API key, which must be included in the request header. The prompt should be passed as a JSON object with a 'prompt' field."
            )
        },
        "usage_instructions": {
            "API Key": (
                "The API requires authentication via an API key, which should be passed in the 'x-api-key' header of your requests. "
                "Ensure that you have the correct API key, which is set as an environment variable (PROXY_API_KEY) on the server."
            ),
            "Request Example": (
                "To use the API, you can send a POST request with the following structure:"
            ),
            "curl_example": (
                "curl -X POST https://gpt-proxy-fugqcpatf7esb6a9.westus-01.azurewebsites.net/generate-text/ "
                "-H 'Content-Type: application/json' "
                "-H 'x-api-key: Jayesh' "
                "-d '{\"prompt\": \"Tell me a short story about a brave knight.\"}'"
            ),
            "Response": (
                "The API will respond with a JSON object containing the generated text under the 'response' key. "
                "If any error occurs, you will receive an appropriate HTTP error status code along with an error message."
            )
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
