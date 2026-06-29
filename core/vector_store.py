from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document 

EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

def get_embeddings():
    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL_NAME,
        model_kwargs={"device": "cpu"},
    )

def build_vector_store(transcript:str)->Chroma:
    print("Building vector store...")

    text_splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n", ".", " "],
        chunk_size=500,
        chunk_overlap=50
    )
    chunks = text_splitter.split_text(transcript)
    print(f"Split {len(chunks)} chunks")

    docs = [
        Document(page_content=chunk, metadata={"source": "", "chunk_id": i})
        for i, chunk in enumerate(chunks)
    ]
    
    # Fully in-memory Chroma instance
    vector_store = Chroma.from_documents(
        documents=docs,
        embedding=get_embeddings()
    )

    return vector_store

def get_retriever(vector_store:Chroma, k:int=20):
    return vector_store.as_retriever(search_type="similarity",search_kwargs={"k":k})
