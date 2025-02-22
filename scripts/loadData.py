from qdrant_client import QdrantClient
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.core import SimpleDirectoryReader, SummaryIndex, VectorStoreIndex, Settings, StorageContext
from dotenv import load_dotenv
import os

load_dotenv()

Settings.llm = OpenAI(api_key=os.getenv("openai_api_key"), model="gpt-4o-mini")
Settings.chunk_size = 1000
Settings.chunk_overlap = 50
Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small", api_key=os.getenv("openai_api_key"))

qc = QdrantClient("http://localhost:6333")
vector_store = QdrantVectorStore(collection_name="llamaindex-docs",client=qc, enable_hybrid=True)
docs = SimpleDirectoryReader(input_dir="data", recursive=True).load_data()
storage_context = StorageContext.from_defaults(vector_store=vector_store)
v_index = VectorStoreIndex.from_documents(docs, storage_context=storage_context)
s_index = SummaryIndex.from_documents(docs)
s_index.storage_context.persist(persist_dir="summary")
