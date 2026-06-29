import os
from dotenv import load_dotenv

load_dotenv()

from utils.audio_processor import process_input, clear_downloads
from core.transcriber import transcribe_audio
from core.summarizer import summarize, create_title
from core.extractor import extract_insights
from core.rag_engine import build_rag_chain

def run():
    source = r"C:\Users\parth\Downloads\Telegram Desktop\Rick.and.Morty.S01E01.720p.BluRay.x264-GalaxyTV.mkv"
    language_choice = None
    
    print("\nCleaning up old session data...")
    clear_downloads()
    
    if os.path.exists("sample.txt"): os.remove("sample.txt")
    if os.path.exists("sample_en.txt"): os.remove("sample_en.txt")
    
    print("\nProcessing input...")
    media_path = process_input(source)
    print("Running Whisper transcription...")
    transcript = transcribe_audio(media_path, language_code=language_choice)
        
    with open("sample_en.txt", "w", encoding="utf-8") as f:
        f.write(transcript)

    print("\nGenerating summary...")
    summary = summarize(transcript)
    title = create_title(summary)
    
    print("Extracting insights...")
    insights = extract_insights(transcript)
    
    print("\n" + "="*50)
    print(f"TITLE: {title}")
    print("="*50)
    print("SUMMARY:")
    print(summary)
    print("\nACTION ITEMS:")
    print(insights.get("action_items", ""))
    print("\nKEY DECISIONS:")
    print(insights.get("key_decisions", ""))
    print("\nOPEN QUESTIONS:")
    print(insights.get("questions", ""))
    
    with open("summary.txt", "w", encoding="utf-8") as f:
        f.write(f"TITLE: {title}\n")
        f.write("="*50 + "\n")
        f.write("SUMMARY:\n")
        f.write(summary + "\n\n")
        f.write("ACTION ITEMS:\n")
        f.write(insights.get("action_items", "") + "\n\n")
        f.write("KEY DECISIONS:\n")
        f.write(insights.get("key_decisions", "") + "\n\n")
        f.write("OPEN QUESTIONS:\n")
        f.write(insights.get("questions", "") + "\n")
        
    print("\n[OK] Full report saved to summary.txt!")

if __name__ == "__main__":
    run()
