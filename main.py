from fastapi import FastAPI, Body
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from langchain.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate
)
from langchain.chains import ConversationChain
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory

prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(
        "The following is a friendly conversation between a human and an AI. The AI is talkative and "
        "provides lots of specific details from its context. If the AI does not know the answer to a "
        "question, it truthfully says it does not know."
    ),
    MessagesPlaceholder(variable_name="history"),
    HumanMessagePromptTemplate.from_template("{input}")
])


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

# openai_api_key="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"


@app.get("/")
async def root():
    return {"message": "Hello World"}


class ChatInput(BaseModel):
    question: str


@app.get("/chat/{question}")  # Adding question as a path parameter
async def chat(question: str):
    llm = ChatOpenAI(
        openai_api_key="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",
        temperature=0
    )
    memory = ConversationBufferMemory(return_messages=True)
    conversation = ConversationChain(memory=memory, prompt=prompt, llm=llm)
    resp = conversation.predict(input=question)
    return resp
