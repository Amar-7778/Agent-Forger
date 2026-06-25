import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv


load_dotenv()

def get_llm(temperature=0.3):
    """
    Returns an LLM instance. 
    Primary is Google Gemini (gemini-2.5-flash).
    Backup/Fallback is Groq (llama-3.3-70b-versatile).
    """
    gemini_key = os.getenv("GEMINI_API_KEY")
    groq_key = os.getenv("GROQ_API_KEY")
    
    primary = None
    fallback = None
    
    if gemini_key and gemini_key.strip():
        primary = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=gemini_key,
            temperature=temperature
        )
        
    if groq_key and groq_key.strip() and groq_key != "GROQ_API_KEY":
        fallback = ChatOpenAI(
            model="llama-3.3-70b-versatile",
            api_key=groq_key,
            base_url="https://api.groq.com/openai/v1",
            temperature=temperature
        )
        
    if primary and fallback:
        return primary.with_fallbacks([fallback])
    elif primary:
        return primary
    elif fallback:
        return fallback
    else:
        raise ValueError("Neither GEMINI_API_KEY nor GROQ_API_KEY is configured in .env. Please set them in settings.")

def get_structured_llm(schema, temperature=0.1):
    """
    Returns an LLM instance that returns structured output conforming to the schema.
    Primary is Google Gemini (gemini-2.5-flash).
    Backup/Fallback is Groq (llama-3.3-70b-versatile).
    """
    gemini_key = os.getenv("GEMINI_API_KEY")
    groq_key = os.getenv("GROQ_API_KEY")
    
    primary = None
    fallback = None
    
    if gemini_key and gemini_key.strip():
        primary = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=gemini_key,
            temperature=temperature
        )
        
    if groq_key and groq_key.strip() and groq_key != "GROQ_API_KEY":
        fallback = ChatOpenAI(
            model="llama-3.3-70b-versatile",
            api_key=groq_key,
            base_url="https://api.groq.com/openai/v1",
            temperature=temperature
        )
        
    if primary and fallback:
        primary_structured = primary.with_structured_output(schema)
        fallback_structured = fallback.with_structured_output(schema)
        return primary_structured.with_fallbacks([fallback_structured])
    elif primary:
        return primary.with_structured_output(schema)
    elif fallback:
        return fallback.with_structured_output(schema)
    else:
        raise ValueError("Neither GEMINI_API_KEY nor GROQ_API_KEY is configured in .env. Please set them in settings.")
