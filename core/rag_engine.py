import os
from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from core.vector_store import load_vector_store, get_retriever, build_vector_store
from core.llm_provider import get_llm
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from operator import itemgetter




def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


def build_rag_chain(transcript: str):
    vector_store = build_vector_store(transcript)
    retriever = get_retriever(vector_store)
    llm = get_llm()

    condense_prompt = ChatPromptTemplate.from_messages([
        ("system", "Given the following chat history and a follow up question, rephrase the follow up question to be a standalone question. If it's already standalone, just return it. Do not answer it."),
        ("human", "Chat History:\n{chat_history}\n\nFollow up question: {question}")
    ])
    
    standalone_question_chain = condense_prompt | llm | StrOutputParser()
    
    def get_standalone_question(input_dict):
        if not input_dict.get("chat_history"):
            return input_dict["question"]
        return standalone_question_chain.invoke(input_dict)

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
        RunnablePassthrough.assign(standalone_question=RunnableLambda(get_standalone_question))
        | {
            "context": itemgetter("standalone_question") | retriever | RunnableLambda(format_docs),
            "question": itemgetter("question")
        }
        | prompt
        | llm
        | StrOutputParser()
    )
    return rag_chain


def ask_question(rag_chain, question: str, chat_history: str = ""):
    return rag_chain.invoke({"question": question, "chat_history": chat_history})