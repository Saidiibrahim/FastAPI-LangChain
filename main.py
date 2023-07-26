import os
from dotenv import load_dotenv
from fastapi import FastAPI, Body
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from langchain.chat_models import ChatOpenAI
from langchain.schema import (
    HumanMessage,
)
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

load_dotenv()
OPENAI_API_KEY =os.getenv("OPENAI_API_KEY")


app = FastAPI()

# Add CORS middleware
origins = [
    "http://localhost:3000",  # The origin for your Next.js app, adjust if needed
    # Add any other origins if necessary
]

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


@app.get("/")
async def root():
    return {"message": "Hello World"}


class ChatInput(BaseModel):
    question: str


@app.get("/chat/{question}")  # Adding question as a path parameter
async def chat(question: str):
    query = ChatOpenAI(
        openai_api_key=OPENAI_API_KEY,
        streaming=False,
        callbacks=[StreamingStdOutCallbackHandler()],
        temperature=0)
    resp = query([HumanMessage(content=question)])
    # Remove quotes and replace newline characters
    content = resp.content.replace('"', '').replace('\n\n', '\n')
    print(content)
    return content
