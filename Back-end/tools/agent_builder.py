from typing import List
from storage.agent_registry import save_agent

def create_custom_agent(name: str, description: str, scope: str, restrictions: str, tools: List[str], theme: str = 'dark', icon: str = '🤖') -> int:
    """
    Creates and persists a new custom agent.
    """
    agent_data = {
        "name": name,
        "description": description,
        "scope": scope,
        "restrictions": restrictions,
        "tools": tools,
        "theme": theme,
        "icon": icon,
        "knowledge_base": None
    }
    return save_agent(agent_data)
