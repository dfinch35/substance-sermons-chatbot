from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb
from llama_index.embeddings.openai import OpenAIEmbedding
from dotenv import load_dotenv
from llama_index.core import SimpleDirectoryReader

load_dotenv()

# Combine all documents
blog_docs = SimpleDirectoryReader("data/blogs").load_data()
sermon_docs = SimpleDirectoryReader("data/sermons").load_data()
all_docs = blog_docs + sermon_docs

# Vector store
db = chromadb.PersistentClient(path="./chroma_db")
chroma_collection = db.get_or_create_collection("substance_knowledge")
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
storage_context = StorageContext.from_defaults(vector_store=vector_store)

embed_model = OpenAIEmbedding(model="text-embedding-3-large")

index = VectorStoreIndex.from_documents(
    all_docs,
    storage_context=storage_context,
    embed_model=embed_model,
    show_progress=True
)

print("✅ Index built and persisted!")
