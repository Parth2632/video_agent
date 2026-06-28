import os
from dotenv import load_dotenv
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

# ── LLM ──────────────────────────────────────────────────────────────────────

_llm = ChatMistralAI(
    api_key=os.getenv("MISTRAL_API_KEY"),
    model="mistral-small-latest",
    temperature=0.2,
)

# ── Text splitter ─────────────────────────────────────────────────────────────

_splitter = RecursiveCharacterTextSplitter(
    chunk_size=2000,
    chunk_overlap=300,
    separators=["\n\n", "\n", ".", " "],
)

# ── Chunk summarization chain ─────────────────────────────────────────────────

_chunk_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are an expert at summarizing transcripts. "
        "Write a concise summary while preserving the important information.",
    ),
    (
        "human",
        "Summarize the following transcript chunk.\n\n"
        "Transcript:\n{chunk}\n\n"
        "Provide:\n- A concise summary\n- Important points",
    ),
])

_chunk_chain = _chunk_prompt | _llm | StrOutputParser()

# ── Final merge chain ─────────────────────────────────────────────────────────

_merge_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are an expert at summarizing transcripts. "
        "Write a concise summary while preserving the important information.",
    ),
    (
        "human",
        "Below are summaries of different parts of a transcript. "
        "Combine them into one clean, concise final summary.\n\n"
        "Summaries:\n{summaries}",
    ),
])

_merge_chain = _merge_prompt | _llm | StrOutputParser()

# ── Title chain ───────────────────────────────────────────────────────────────

_title_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are an expert at creating concise, engaging titles for videos.",
    ),
    (
        "human",
        "Create a title for the video based on the following summary.\n\n"
        "Summary:\n{summary}\n\n"
        "Return only the title, nothing else.",
    ),
])

_title_chain = _title_prompt | _llm | StrOutputParser()

# ── Public API ────────────────────────────────────────────────────────────────

def summarize(transcript: str) -> str:
    """Chunk, summarize, and merge a transcript into a single summary."""
    chunks = _splitter.split_text(transcript)
    chunk_summaries = [_chunk_chain.invoke({"chunk": chunk}) for chunk in chunks]
    combined = "\n\n".join(chunk_summaries)
    return _merge_chain.invoke({"summaries": combined})


def create_title(summary: str) -> str:
    """Generate a video title from an existing summary."""
    return _title_chain.invoke({"summary": summary}).strip()


def summarize_and_title(transcript: str) -> tuple[str, str]:
    """
    Summarize a transcript and generate a title in one call.
    Returns (summary, title) — summary is computed once and reused for the title.
    """
    summary = summarize(transcript)
    title = create_title(summary)
    return summary, title
    