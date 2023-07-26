from langchain.chat_models import ChatOpenAI
from langchain.schema import (
    HumanMessage,
)

from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
chat = ChatOpenAI(
    openai_api_key="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",
    streaming=True,
    callbacks=[StreamingStdOutCallbackHandler()],
    temperature=0)


resp = chat([HumanMessage(content="Who is Elon Musk?")])
