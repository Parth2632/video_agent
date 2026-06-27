import os
from dotenv import load_dotenv
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

_llm = ChatMistralAI(
    api_key=os.getenv("MISTRAL_API_KEY"),
    model="mistral-small-latest",
    temperature=0.2
)

_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert at summarizing transcripts. Write a concise summary while preserving the important information."),
    ("human", "Summarize the following transcript chunk.\n\nTranscript:\n{chunk}\n\nProvide:\n- A concise summary\n- Important points")
])

_splitter = RecursiveCharacterTextSplitter(
    chunk_size=2000,
    chunk_overlap=300,
    separators=["\n\n", "\n", ".", " "]
)

_chain = _prompt | _llm | StrOutputParser()

_final_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert at summarizing transcripts. Write a concise summary while preserving the important information."),
    ("human", "Below are summaries of different parts of a transcript. Combine them into one clean, concise final summary.\n\nSummaries:\n{summaries}")
])

_final_chain = _final_prompt | _llm | StrOutputParser()

def summarize(transcript: str) -> str:
    chunks = _splitter.split_text(transcript)
    summaries = [_chain.invoke({"chunk": chunk}) for chunk in chunks]
    combined = "\n\n".join(summaries)
    return _final_chain.invoke({"summaries": combined})

    