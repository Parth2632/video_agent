from langchain_ollama import ChatOllama

def get_llm():
    # Using a local Ollama model. Make sure you have run `ollama run llama3` first!
    return ChatOllama(
        model="llama3",
        temperature=0.2,
    )
