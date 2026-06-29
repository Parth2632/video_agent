import os 
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document 

CHROMA_DIR = "vector_db"
COLLECTION_NAME = "meeting_transcript"
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

def clear_vector_store():
    import shutil
    import os
    if os.path.exists(CHROMA_DIR):
        shutil.rmtree(CHROMA_DIR, ignore_errors=True)


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
        Document(page_content=chunk, metadata={"source": ""})
        for chunk in chunks
    ]
    
    vector_store = Chroma.from_documents(
        documents=docs,
        embedding=get_embeddings(),
        collection_name=COLLECTION_NAME,
        persist_directory=CHROMA_DIR
    )

    return vector_store

def load_vector_store()->Chroma:
    return Chroma(
        embedding=get_embeddings(),
        collection_name = COLLECTION_NAME,
        persist_directory=CHROMA_DIR
    )

def get_retriever(vector_store:Chroma, k:int=4):
    return vector_store.as_retriever(search_type="similarity",search_kwargs={"k":k})
    
