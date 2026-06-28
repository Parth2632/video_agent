from dotenv import load_dotenv
load_dotenv()

from utils.audio_processor import process_input
from core.transcriber import transcribe_all
from core.summarizer import summarize, create_title
from core.extractor import extract_action_items, extract_key_decisions, extract_questions
from core.rag_engine import build_rag_chain, ask_question
def run_pipeline(source: str):
    print("Starting AI Meeting Assistant...")

    chunks = process_input(source)
    transcript = transcribe_all(chunks)
    summary = summarize(transcript)
    title = create_title(summary)

    actions = extract_action_items(transcript)
    questions = extract_questions(transcript)
    decisions = extract_key_decisions(transcript)
    rag_chain = build_rag_chain(transcript)

    return {
        "title": title,
        "summary": summary,
        "action_items": actions,
        "questions": questions,
        "key_decisions": decisions,
        "rag_chain": rag_chain
    }


if __name__ == "__main__":
    source = input("Enter video/audio file path or YouTube URL: ").strip()

    results = run_pipeline(source)

    print("\n" + "=" * 60)
    print(f"Title: {results['title']}")
    print("=" * 60)

    print("\nSUMMARY:")
    print(results["summary"])

    print("\nACTION ITEMS:")
    print(results["action_items"])

    print("\nKEY DECISIONS:")
    print(results["key_decisions"])

    print("\nOPEN QUESTIONS:")
    print(results["questions"])

    print("\n" + "=" * 60)
    print("Q&A Mode — ask anything about the meeting (type 'exit' to quit)")
    print("=" * 60)

    rag_chain = results["rag_chain"]
    while True:
        question = input("\nYou: ").strip()
        if question.lower() in ("exit", "quit", "q"):
            print("Goodbye!")
            break
        if not question:
            continue
        answer = ask_question(rag_chain, question)
        print(f"Assistant: {answer}")