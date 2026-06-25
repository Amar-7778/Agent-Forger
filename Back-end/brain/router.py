from brain.classifier import classify_intent
from brain.synthesizer import synthesize_response
from tools.rag_tool import query_knowledge_base

def route_request(user_input: str) -> str:
    intent = classify_intent(user_input)
    mode = intent.mode
    
    context = ""
    
    if mode == "MODE_A":
        # External Intelligence
        context = "Placeholder: External search using MCP (Tavily) would execute here."
    elif mode == "MODE_B":
        # Company Knowledge
        context = query_knowledge_base(user_input)
    elif mode == "MODE_C":
        # Workflow Execution
        context = "Placeholder: Workflow execution via MCP would happen here."
    elif mode == "MODE_D":
        # Agent Creation
        context = "Please direct the user to use the Agent Builder tab in the UI to create a custom agent with specific scopes."
    elif mode == "MODE_E":
        # Multi-Step Operations
        context = "Placeholder: LangGraph multi-step operation would execute here."
    elif mode == "MODE_F":
        # Conversation
        context = "Acknowledge the user directly and concisely."
    elif mode == "MODE_G":
        # Scheduled Automation
        context = "Please direct the user to use the Scheduled Agents tab in the UI to configure recurring tasks."
    else:
        context = "Unknown intent mode."

    final_response = synthesize_response(user_input, context, mode)
    return final_response
