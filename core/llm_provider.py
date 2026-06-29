import os
from dotenv import load_dotenv
from langchain_mistralai import ChatMistralAI

load_dotenv()

def get_llm():
    return ChatMistralAI(
        model="mistral-large-latest",
        temperature=0.2,
        max_retries=2,
        api_key=os.environ.get("MISTRAL_API_KEY")
    )
