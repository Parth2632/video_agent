from core.llm_provider import get_llm
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

load_dotenv()

def build_chain(system_prompt: str):
    llm = get_llm()
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{transcript}")
    ])
    return prompt | llm | StrOutputParser()


def extract_insights(transcript: str) -> dict:
    chain = build_chain(
        "You are an expert meeting analyst. From the meeting transcript, extract the following:\n"
        "1. Action Items (Task, Owner, Deadline)\n"
        "2. Key Decisions\n"
        "3. Open Questions\n\n"
        "CRITICAL: You MUST include the exact timestamp (e.g., [02:35]) from the transcript next to EVERY single action item, decision, or question you extract so the user can validate it.\n\n"
        "IMPORTANT: Use the Video Title, Description, and User Provided Context (if any) provided at the start of the transcript "
        "for context. This helps correctly identify names, acronyms, topics, and cultural greetings.\n\n"
        "Return the result strictly in this format, with headers exactly as shown:\n"
        "ACTIONS:\n[List action items here, or say 'No action items found']\n\n"
        "DECISIONS:\n[List key decisions here, or say 'No key decisions found']\n\n"
        "QUESTIONS:\n[List questions here, or say 'No open questions found']"
    )
    result = chain.invoke({"transcript": transcript})
    
    actions = "No action items found."
    decisions = "No key decisions found."
    questions = "No open questions found."
    
    try:
        if "ACTIONS:" in result:
            actions_part = result.split("ACTIONS:")[1].split("DECISIONS:")[0].strip()
            if actions_part: actions = actions_part
        if "DECISIONS:" in result:
            decisions_part = result.split("DECISIONS:")[1].split("QUESTIONS:")[0].strip()
            if decisions_part: decisions = decisions_part
        if "QUESTIONS:" in result:
            questions_part = result.split("QUESTIONS:")[1].strip()
            if questions_part: questions = questions_part
    except Exception:
        pass
        
    return {
        "action_items": actions,
        "key_decisions": decisions,
        "questions": questions
    }

