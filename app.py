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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
