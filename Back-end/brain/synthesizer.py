import os
from dotenv import load_dotenv
from brain.llm_factory import get_llm

load_dotenv()

def synthesize_response(user_input: str, context: str, mode: str) -> str:
    prompt = f"""
    You are AgentForge, an AI Operations Director. 
    You are running a business operation. Your responses must be Direct, Short, Actionable, and Clear.
    Avoid long explanations, technical jargon, repetition, and marketing language.

    User Input: {user_input}
    Execution Mode: {mode}
    Context/Results: {context}

    Based on the context/results provided above, construct the final response to the user.
    """
    try:
        llm = get_llm(temperature=0.3)
        response = llm.invoke(prompt)
        return response.content
    except Exception as e:
        return f"System error generating response. Context was: {context}. Error: {e}"
