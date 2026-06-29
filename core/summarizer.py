from dotenv import load_dotenv
from core.llm_provider import get_llm
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

# ── LLM ──────────────────────────────────────────────────────────────────────

_llm = get_llm()

# ── Text splitter ─────────────────────────────────────────────────────────────

_splitter = RecursiveCharacterTextSplitter(
    chunk_size=15000,
    chunk_overlap=1000,
    separators=["\n\n", "\n", ".", " "],
)

# ── Chunk summarization chain ─────────────────────────────────────────────────

_chunk_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are an expert at summarizing transcripts. "
        "Write a concise summary while preserving the important information. "
        "IMPORTANT: Use the Video Title, Description, and User Provided Context (if any) provided at the start of the transcript "
        "for context. This helps correctly identify names, acronyms, topics, and cultural greetings.",
    ),
    (
        "human",
        "Summarize the following transcript chunk.\n\n"
        "Transcript:\n{chunk}\n\n"
        "Provide:\n- A concise summary\n- Important points\n\n"
        "CRITICAL INSTRUCTION: You MUST format your important points like this: '[MM:SS] - Point description'. Use the exact timestamps from the transcript to allow the user to validate your claims.",
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
        "Combine them into one clean, concise final summary. Ensure that you preserve the timestamps for all important points so the user can cross-reference the original media.\n\n"
        "CRITICAL INSTRUCTION: Keep the exact timestamp (e.g., [12:34]) next to every important point, action item, or decision in your final output!\n\n"
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
    chunk_summaries = _chunk_chain.batch([{"chunk": chunk} for chunk in chunks], config={"max_concurrency": 1})
    combined = "\n\n".join(chunk_summaries)
    if len(chunks) == 1:
        return combined
    return _merge_chain.invoke({"summaries": combined})


def create_title(summary: str) -> str:
    """Generate a video title from an existing summary."""
    return _title_chain.invoke({"summary": summary}).strip()