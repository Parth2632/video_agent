import os
from dotenv import load_dotenv

load_dotenv()

from utils.audio_processor import process_input, clear_downloads
from core.transcriber import transcribe_audio
from core.summarizer import summarize, create_title
from core.extractor import extract_insights
from core.rag_engine import build_rag_chain, ask_question

def main():
    print("========================================")
    print("* AI Meeting Assistant (Terminal Mode)")
    print("========================================")
    
    source = input("Enter video/audio file path or YouTube URL: ").strip()
    
    print("\nLanguage Options:")
    print("1: Auto-detect (English default)")
    print("2: Hindi/Hinglish (Forces Whisper to Hindi mode)")
    lang_choice = input("Select language [1/2]: ").strip()
    language_choice = "hi" if lang_choice == "2" else None

    print("\nOptional Context:")
    user_context = input("Enter any helpful context about this meeting (or press Enter to skip): ").strip()

    print("\nCleaning up old session data...")
    clear_downloads()
    
    if os.path.exists("sample.txt"): os.remove("sample.txt")
    if os.path.exists("sample_en.txt"): os.remove("sample_en.txt")
    
    is_youtube = source.startswith("http://") or source.startswith("https://")
    
    transcript = ""
    metadata_str = ""

    if is_youtube:
        print("\nFetching YouTube metadata...")
        try:
            import yt_dlp
            ydl_opts = {'quiet': True, 'skip_download': True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(source, download=False)
                v_title = info.get('title', '')
                channel = info.get('uploader', '')
                description = info.get('description', '')
                if v_title or channel or description:
                    metadata_str = f"Video Title: {v_title}\nChannel: {channel}\nDescription: {description}\n\n---\n\nTranscript:\n"
        except Exception:
            pass

        print("Fetching YouTube transcript directly if available...")
        from youtube_transcript_api import YouTubeTranscriptApi
        if "v=" in source:
            video_id = source.split("v=")[1].split("&")[0]
        elif "youtu.be/" in source:
            video_id = source.split("youtu.be/")[1].split("?")[0]
        else:
            video_id = source
            
        try:
            transcript_list = YouTubeTranscriptApi().list(video_id)
            try:
                transcript_obj = transcript_list.find_transcript(['en'])
                transcript_data = transcript_obj.fetch()
                transcript = " ".join(f"[{int(chunk['start'])//60:02d}:{int(chunk['start'])%60:02d}] {chunk['text']}" for chunk in transcript_data)
                print("Found native English transcript!")
            except Exception:
                transcript_obj = transcript_list.find_transcript(['hi'])
                try:
                    translated_obj = transcript_obj.translate('en')
                    transcript_data = translated_obj.fetch()
                    transcript = " ".join(f"[{int(chunk['start'])//60:02d}:{int(chunk['start'])%60:02d}] {chunk['text']}" for chunk in transcript_data)
                    print("Found Hindi transcript and translated via YouTube!")
                except Exception:
                    print("No translatable transcript found on YouTube. Falling back to Whisper...")
                    pass
        except Exception as e:
            print(f"Could not fetch YouTube transcript API: {e}")
            print("Falling back to audio download + Whisper transcription...")
            transcript = ""
            
    if not transcript:
        print("\nProcessing input...")
        media_path = process_input(source)
        print("Running Whisper transcription...")
        transcript = transcribe_audio(media_path, language_code=language_choice)
        
    if metadata_str and transcript:
        transcript = metadata_str + transcript
        
    if user_context and transcript:
        transcript = f"User Provided Context:\n{user_context}\n\n---\n\n" + transcript
        
    with open("sample_en.txt", "w", encoding="utf-8") as f:
        f.write(transcript)

    print("\nGenerating summary...")
    summary = summarize(transcript)
    title = create_title(summary)
    
    print("Extracting insights...")
    insights = extract_insights(transcript)
    
    print("Building vector store for Q&A...")
    rag_chain = build_rag_chain(transcript)
    
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
    print("\nPipeline complete! Enter a question (or type 'exit' to quit):")
    chat_history = []
    while True:
        try:
            q = input("\nYou: ")
            if q.lower() in ['exit', 'quit']:
                break
            ans = ask_question(rag_chain, q, str(chat_history))
            print(f"Assistant: {ans}")
            chat_history.extend([("human", q), ("assistant", ans)])
        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    main()
