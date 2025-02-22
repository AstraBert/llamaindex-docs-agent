from qdrant_client import QdrantClient
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.core import SimpleDirectoryReader, SummaryIndex, VectorStoreIndex, Settings, StorageContext

f = open("/run/secrets/openai_key", "r")
openai_api_key: str = f.read()
f.close()

Settings.llm = OpenAI(api_key=openai_api_key, model="gpt-4o-mini")
Settings.chunk_size = 1000
Settings.chunk_overlap = 50
Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small", api_key=openai_api_key)

qc = QdrantClient(host="vector_db", port=6333)
vector_store = QdrantVectorStore(collection_name="llamaindex-docs",client=qc, enable_hybrid=True)
docs = SimpleDirectoryReader(input_dir="/app/data", recursive=True).load_data()
storage_context = StorageContext.from_defaults(vector_store=vector_store)
v_index = VectorStoreIndex.from_documents(docs, storage_context=storage_context)
s_index = SummaryIndex.from_documents(docs)
s_index.storage_context.persist(persist_dir="/app/summary")
