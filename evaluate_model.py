import sys
import os
import subprocess

sys.path.append(r"C:\Users\parth\OneDrive\Desktop\video_agent")

from core.transcriber import transcribe_audio
from core.rag_engine import build_rag_chain

media_path = r"C:\Users\parth\OneDrive\Desktop\Recording.m4a"
wav_path = media_path + ".wav"

print("Converting to WAV...")
try:
    subprocess.run(["ffmpeg", "-y", "-i", media_path, "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le", wav_path], check=True, capture_output=True)
except Exception as e:
    print("ffmpeg failed:", e)

print("Transcribing...")
transcript = transcribe_audio(wav_path, "en")
print(f"Transcript length: {len(transcript)} chars")

print("Building RAG chain...")
rag_chain = build_rag_chain(transcript)

questions = [
    "What was discussed at the 2 minute mark?",
    "What happened after the frontend update?",
    "What are all the action items and their owners?",
    "What decisions were finalized in this meeting?",
    "What blockers were mentioned?",
    "What is the status of the recommendation engine?",
    "When is the Nexus Corp demo and what needs to be ready for it?",
    "What are the risks going into this sprint?"
]

print("Running QA...")
with open("eval_results.txt", "w", encoding="utf-8") as f:
    for q in questions:
        print(f"Asking: {q}")
        res = rag_chain.invoke({"question": q, "chat_history": []})
        f.write(f"Q: {q}\n")
        f.write(f"A: {res}\n\n")

print("Done! Check eval_results.txt")
