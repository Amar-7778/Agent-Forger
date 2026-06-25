from typing import Dict, Any, List
from langgraph.graph import StateGraph, START, END

# Define state
class WorkflowState(dict):
    task: str
    research_data: str
    analysis: str
    final_report: str

def node_research(state: WorkflowState):
    # Simulated research step
    task = state.get("task", "")
    return {"research_data": f"Researched information about: {task}"}

def node_analyze(state: WorkflowState):
    data = state.get("research_data", "")
    return {"analysis": f"Analysis of the data: {data} looks promising."}

def node_report(state: WorkflowState):
    analysis = state.get("analysis", "")
    return {"final_report": f"Final Report\n---\n{analysis}"}

def build_workflow_graph():
    workflow = StateGraph(WorkflowState)
    
    workflow.add_node("research", node_research)
    workflow.add_node("analyze", node_analyze)
    workflow.add_node("report", node_report)
    
    workflow.add_edge(START, "research")
    workflow.add_edge("research", "analyze")
    workflow.add_edge("analyze", "report")
    workflow.add_edge("report", END)
    
    return workflow.compile()

def run_workflow(task: str) -> str:
    app = build_workflow_graph()
    initial_state = {"task": task}
    final_state = app.invoke(initial_state)
    return final_state.get("final_report", "Error executing workflow.")
