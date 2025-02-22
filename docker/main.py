from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
import gradio as gr
from qdrant_client import QdrantClient
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.core import VectorStoreIndex, Settings, StorageContext, load_index_from_storage
from llama_index.core.tools import QueryEngineTool, FunctionTool
from pydantic import BaseModel, Field
from llama_index.core.query_engine import RouterQueryEngine
from llama_index.core.selectors import PydanticSingleSelector
from llama_index.core.agent import ReActAgent
from llama_index.core.llms import ChatMessage
from tavily import TavilyClient
import requests


f = open("/run/secrets/openai_key", "r")
openai_api_key: str = f.read()
f.close()
f = open("/run/secrets/tavily_key", "r")
tavily_api_key: str = f.read()
f.close()

tavily_client = TavilyClient(api_key=tavily_api_key)
Settings.llm = OpenAI(api_key=openai_api_key, model="gpt-4o-mini")
Settings.chunk_size = 1000
Settings.chunk_overlap = 50
Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small", api_key=openai_api_key)
qc = QdrantClient(host="vector_db", port=6333)
vector_store = QdrantVectorStore(client=qc, collection_name="llamaindex-docs", enable_hybrid=True)
v_index = VectorStoreIndex.from_vector_store(vector_store=vector_store)
s_context = StorageContext.from_defaults(persist_dir="/app/summary")
s_index = load_index_from_storage(storage_context=s_context)
v_engine = v_index.as_query_engine()
s_engine = s_index.as_query_engine()

def tavily_search(query: str = Field("Query to search the web for information about LlamaIndex"))-> str:
    """Search the web to find information about LLamaIndex: it might be information related to errors, common or specific questions, tutorials and examples"""

    response = tavily_client.search(
        query=query,
        include_answer="basic"
    )

    return response["answer"]

list_tool = QueryEngineTool.from_defaults(
    query_engine=s_engine,
    description=(
        "Useful for summarization questions related to LlamaIndex Documentation"
    ),
)

vector_tool = QueryEngineTool.from_defaults(
    query_engine=v_engine,
    description=(
        "Useful for retrieving specific context from LlamaIndex Documentation"
    ),
)

router_engine = RouterQueryEngine(
    selector=PydanticSingleSelector.from_defaults(),
    query_engine_tools=[
        list_tool,
        vector_tool,
    ],
)

router_tool =  QueryEngineTool.from_defaults(
    query_engine=router_engine,
    description=(
        "A query engine based on a router: the router can select either from a summarization index or from a vector index. It retrieves useful information about LlamaIndex docs"
    ),
)

web_search_tool = FunctionTool.from_defaults(
    fn = tavily_search
)

chat_history = [ChatMessage.from_str("You are a useful assistant for developers. Your task is to help them providing useful information about LlamaIndex, a popular AI framework with countless integrations. You should rely on the contextual information you can find from the documentation database and, if that is not sufficient, search the internet. The documentation retrieved from the database is sufficient when it does not only provide vague guidance, but when it actually answers the user's question: to be deemed sufficient, it would be important (but not essential) that the retrieved information contains code snippets.", role="system")]

agent = ReActAgent.from_tools(tools=[router_tool, web_search_tool], chat_history=chat_history, verbose=True)

app = FastAPI(default_response_class=ORJSONResponse)

class Message(BaseModel):
    message: str = Field(description="Message from the user")

@app.get("/")
async def read_main():
    return {"message": "This is your main app"}
@app.post("/message/")
async def read_message(message: Message) -> Message:
    response = agent.chat(message.message)
    msg = Message(message=str(response))
    return msg

def reply(message, history):
    if message == "" or message is None:
        res = "You should provide me with a message"
        r = ""
        for char in res:
            r+=char
            yield r
    else:
        req = requests.post("http://localhost:8000/message", json={"message": message})
        response = req.json()
        res = response["message"]
        r = ""
        for char in res:
            r+=char
            yield r

io = gr.ChatInterface(reply, title="Chat with LlamaIndex docs!🦙", examples=["How do I install LlamaIndex?", "What is a workflow and how can I implement it?", "How can I build advanced retrieval with LlamaIndex?"])
app = gr.mount_gradio_app(app, io, path="/gradio")
