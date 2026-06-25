import os
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from brain.llm_factory import get_llm, get_structured_llm

load_dotenv()

class IntentClassification(BaseModel):
    mode: str = Field(description="The classified mode (MODE_A, MODE_B, MODE_C, MODE_D, MODE_E, MODE_F, MODE_G)")
    reasoning: str = Field(description="Reasoning for the classification")

def classify_intent(user_input: str) -> IntentClassification:
    prompt = f"""
    You are the AgentForge Intent Classifier.
    Determine the user's intent based on these modes:
    
    MODE_A - External Intelligence: Gather info outside company (news, research).
    MODE_B - Company Knowledge: Answer using internal company data (refund policy, docs).
    MODE_C - Workflow Execution: Perform one-off actions (email, Slack, CRM).
    MODE_D - Agent Creation: Create a new specialized AI worker (build a bot).
    MODE_E - Multi-Step Operations: Complex tasks requiring multiple steps/tools.
    MODE_F - Conversation: Greetings, ambiguous chat.
    MODE_G - Scheduled Automation: Recurring tasks (daily report, monitor).

    User Input: {user_input}
    """
    
    try:
        structured_llm = get_structured_llm(IntentClassification, temperature=0.1)
        result = structured_llm.invoke(prompt)
        return result
    except Exception as e:
        print(f"Classification error: {e}")
        return IntentClassification(mode="MODE_F", reasoning=f"Error: {e}")
