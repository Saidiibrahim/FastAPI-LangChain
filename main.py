import threading
import queue

import os
from dotenv import load_dotenv
from fastapi import FastAPI, Body
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from langchain.chat_models import ChatOpenAI
from langchain.callbacks.base import BaseCallbackManager
from langchain.schema import AIMessage, HumanMessage, SystemMessage
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

from typing import List, Dict

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

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
    messages: List[Dict[str, str]]
    model: str = ("gpt-3.5-turbo",)
    temperature: float | None = (0.7,)
    stream: bool | None = (False,)
    user: str | None = (None,)
    # description: str | None = None
    # price: float
    # tax: float | None = None


class ThreadedGenerator:
    def __init__(self):
        self.queue = queue.Queue()

    def __iter__(self):
        return self

    def __next__(self):
        item = self.queue.get()
        if item is StopIteration:
            raise item
        return item

    def send(self, data):
        self.queue.put(data)

    def close(self):
        self.queue.put(StopIteration)


class ChainStreamHandler(StreamingStdOutCallbackHandler):
    def __init__(self, gen):
        super().__init__()
        self.gen = gen

    def on_llm_new_token(self, token: str, **kwargs):
        self.gen.send(token)


def makeMessage(message: Dict[str, str]):
    if message["role"] == "system":
        return SystemMessage(content=message["content"])
    if message["role"] == "assistant":
        return AIMessage(content=message["content"])
    if message["role"] == "user":
        return HumanMessage(content=message["content"])
    else:
        return HumanMessage(content="unknown!")


def llm_thread(g: ThreadedGenerator, body: ChatInput):
    try:
        query = ChatOpenAI(
            openai_api_key=OPENAI_API_KEY,
            verbose=True,
            streaming=True,
            callback_manager=BaseCallbackManager([ChainStreamHandler(g)]),
            temperature=0,
            # temperature=0.7,
        )
        messageChain = list(map(makeMessage, body.messages))
        query(messageChain)

    finally:
        g.send("[DONE]")
        g.close()


def chat(body: ChatInput):
    g = ThreadedGenerator()
    threading.Thread(target=llm_thread, args=(g, body)).start()
    return g


@app.post("/chat/")  # Adding question as a path parameter
async def stream(body: ChatInput):
    return StreamingResponse(chat(body), media_type="text/event-stream")
    # Remove quotes and replace newline characters
    # content = resp.content.replace('"', "").replace("\n\n", "\n")
    # print(content)
    # return content
