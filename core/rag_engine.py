import os
from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from core.vector_store import load_vector_store, get_retriever, build_vector_store
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda, RunnablePassthrough


def get_llm():
    return ChatMistralAI(
        api_key=os.getenv("MISTRAL_API_KEY"),
        model="mistral-small-latest",
        temperature=0.2,
    )


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


def build_rag_chain(transcript: str):
    vector_store = build_vector_store(transcript)
    retriever = get_retriever(vector_store)
    llm = get_llm()

    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            """You are an expert meeting assistant. Answer the user's question
based ONLY on the meeting transcript context provided below.

If the answer is not found in the context, say:
"I could not find this information in the meeting transcript."

Always be concise and precise. If quoting someone, mention it clearly.

Context from meeting transcript:
{context}""",
        ),
        ("human", "{question}")
    ])

    rag_chain = (
        {
            "context": retriever | RunnableLambda(format_docs),
            "question": RunnablePassthrough()
        }
        | prompt
        | llm
        | StrOutputParser()
    )
    return rag_chain


def ask_question(rag_chain, question: str):
    return rag_chain.invoke(question)