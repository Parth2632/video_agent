from core.vector_store import get_retriever, build_vector_store
from core.llm_provider import get_llm
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from operator import itemgetter


import re

def get_time_in_seconds(mm, ss):
    return int(mm) * 60 + int(ss)

def extract_time_window(query: str, transcript: str):
    # Look for "X minute(s)", "X-minute", or "X min"
    match = re.search(r'(\d+)[\s\-_]*(?:minute|min|m)', query.lower())
    target_seconds = None
    if match:
        target_seconds = int(match.group(1)) * 60
    else:
        # look for MM:SS
        match = re.search(r'(\d+):(\d{2})', query)
        if match:
            target_seconds = int(match.group(1)) * 60 + int(match.group(2))
            
    if target_seconds is None:
        return None
        
    pattern = r'\[(\d{2}):(\d{2})\]'
    matches = list(re.finditer(pattern, transcript))
    if not matches:
        return None
        
    # Determine total meeting length from the last timestamp
    last_match = matches[-1]
    total_seconds = get_time_in_seconds(last_match.group(1), last_match.group(2))
    
    # Dynamic window size
    if total_seconds < 10 * 60: # Less than 10 mins
        window_size = 30
    elif total_seconds < 30 * 60: # Less than 30 mins
        window_size = 60
    else: # 30 mins or more
        window_size = 120
        
    start_idx = None
    end_idx = len(transcript)
    
    prev_match = None
    for m in matches:
        sec = get_time_in_seconds(m.group(1), m.group(2))
        
        # If we enter the start of our target window
        if sec > target_seconds - window_size and start_idx is None:
            # Start from the previous timestamp chunk to ensure we don't miss text
            if prev_match:
                start_idx = prev_match.start()
            else:
                start_idx = m.start()
                
        # If we pass the end of our target window
        if sec > target_seconds + window_size:
            end_idx = m.start()
            break
            
        prev_match = m
            
    if start_idx is None or start_idx == end_idx:
        return None
        
    context_prefix = transcript[:matches[0].start()]
    window_text = transcript[start_idx:end_idx]
    return context_prefix + "\n\n" + window_text


def format_docs(docs):
    sorted_docs = sorted(docs, key=lambda d: d.metadata.get("chunk_id", 0))
    return "\n\n".join(doc.page_content for doc in sorted_docs)


def build_rag_chain(transcript: str):
    if len(transcript) >= 25000:
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

    def get_context(input_dict):
        # We must use the ORIGINAL user question for regex, 
        # because the LLM might rewrite "2 minutes" into something like "the second minute" in the standalone_question!
        original_q = input_dict["question"]
        
        # If the user asked a chronological question, extract that exact time window!
        window = extract_time_window(original_q, transcript)
        if window:
            return window
            
        # Otherwise, fall back to our normal logic
        if len(transcript) < 25000:
            return transcript
        else:
            docs = retriever.invoke(input_dict["standalone_question"])
            return format_docs(docs)

    rag_chain = (
        RunnablePassthrough.assign(standalone_question=RunnableLambda(get_standalone_question))
        | {
            "context": RunnableLambda(get_context),
            "question": itemgetter("question")
        }
        | prompt
        | llm
        | StrOutputParser()
    )
    return rag_chain


def ask_question(rag_chain, question: str, chat_history: str = ""):
    return rag_chain.invoke({"question": question, "chat_history": chat_history})