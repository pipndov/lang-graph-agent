import json
import pathlib
import subprocess
import time
from typing import Tuple, Optional, TypedDict, Annotated, Literal

from dotenv import load_dotenv
from pydantic import BaseModel, Field, ConfigDict

from langchain_core.tools import tool
from langchain_anthropic import ChatAnthropic
from langchain.agents import create_agent

from langgraph.graph import StateGraph, add_messages
from langgraph.constants import END

load_dotenv()

# ---------------- CONSTANTS & SETUP ---------------- #

PROJECT_ROOT = pathlib.Path.cwd() / "generated_project"
llm = ChatAnthropic(model='claude-haiku-4-5')

# ---------------- STATE OUTPUT MODELS ---------------- #

class File(BaseModel):
    path: str = Field(description="The path to the file to be created or modified")
    purpose: str = Field(description="The purpose of the file, e.g. 'main application logic', 'data processing module', etc.")

class Plan(BaseModel):
    name: str = Field(description="The name of app to be built")
    description: str = Field(description="A one line description of the app to be built, e.g. 'A web application for managing personal finances'")
    techstack: str = Field(description="The tech stack to be used for the app, e.g. 'python', 'javascript', 'react', 'flask', etc.")
    features: list[str] = Field(description="A list of features that the app should have, e.g. 'user authentication', 'data visualization', etc.")
    files: list[File] = Field(description="A list of files to be created, each with a 'path' and 'purpose'")

class ImplementationTask(BaseModel):
    filepath: str = Field(description="The path to the file to be modified")
    task_description: str = Field(description="A detailed description of the task to be performed on the file, e.g. 'add user authentication', 'implement data processing logic', etc.")

class TaskPlan(BaseModel):
    implementation_steps: list[ImplementationTask] = Field(description="A list of steps to be taken to implement the task")
    model_config = ConfigDict(extra="allow")

class CoderState(BaseModel):
    task_plan: TaskPlan = Field(description="The plan for the task to be implemented")
    current_step_idx: int = Field(0, description="The index of the current step in the implementation steps")
    current_file_content: Optional[str] = Field(None, description="The content of the file currently being edited or created")

# ---------------- STATE SCHEMA ---------------- #

class GraphState(TypedDict, total=False):
    user_prompt: str
    plan: Plan
    task_plan: TaskPlan
    coder_state: CoderState
    status: str
    edit_request: Optional[str]
    previous_plan: Optional[Plan]
    previous_task_plan: Optional[TaskPlan]
    planner_approved: Optional[str]
    architect_approved: Optional[str]

# ---------------- FILE TOOLS ---------------- #

def safe_path_for_project(path: str) -> pathlib.Path:
    p = (PROJECT_ROOT / path).resolve()
    if PROJECT_ROOT.resolve() not in p.parents and PROJECT_ROOT.resolve() != p.parent and PROJECT_ROOT.resolve() != p:
        raise ValueError("Attempt to write outside project root")
    return p

@tool
def write_file(path: str, content: str) -> str:
    """Writes content to a file at the specified path within the project root."""
    p = safe_path_for_project(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(content)
    return f"WROTE:{p}"

@tool
def read_file(path: str) -> str:
    """Reads content from a file at the specified path within the project root."""
    p = safe_path_for_project(path)
    if not p.exists():
        return ""
    with open(p, "r", encoding="utf-8") as f:
        return f.read()

@tool
def get_current_directory() -> str:
    """Returns the current working directory."""
    return str(PROJECT_ROOT)

@tool
def list_files(directory: str = ".") -> str:
    """Lists all files in the specified directory within the project root."""
    p = safe_path_for_project(directory)
    if not p.is_dir():
        return f"ERROR: {p} is not a directory"
    files = [str(f.relative_to(PROJECT_ROOT)) for f in p.glob("**/*") if f.is_file()]
    return "\n".join(files) if files else "No files found."

@tool
def run_cmd(cmd: str, cwd: str = None, timeout: int = 30) -> Tuple[int, str, str]:
    """Runs a shell command in the specified directory and returns the result."""
    cwd_dir = safe_path_for_project(cwd) if cwd else PROJECT_ROOT
    res = subprocess.run(cmd, shell=True, cwd=str(cwd_dir), capture_output=True, text=True, timeout=timeout)
    return res.returncode, res.stdout, res.stderr

def init_project_root():
    PROJECT_ROOT.mkdir(parents=True, exist_ok=True)
    return str(PROJECT_ROOT)

# ---------------- PROMPTS ---------------- #

def planner_prompt(user_prompt: str) -> str:
    return f"""
    You are the PLANNER agent. Convert the user prompt into a COMPLETE engineering project plan
    User request: {user_prompt}
    """

def architect_prompt(plan: str) -> str:
    return f"""
    You are the ARCHITECT agent. Given this project plan, break it down into explicit engineering tasks.

    RULES:
        - For each FILE in the plan, create one or more IMPLEMENTATION TASKS.
        - In each task description:
            * Specify exactly what to implement.
            * Name the variables, functions, classes, and components to be defined.
            * Mention how this task depends on or will be used by previous tasks.
            * Include integration details: imports, expected function signatures, data flow.
        - Order tasks so that dependencies are implemented first.
        - Each step must be SELF-CONTAINED but also carry FORWARD the relevant context from earlier tasks.

    Project Plan:
    {plan}
    """

def coder_system_prompt() -> str:
    return """
        You are the CODER agent.
        You are implementing a specific engineering task.
        You have access to tools to read and write files.

        Always:
        - Review all existing files to maintain compatibility.
        - Implement the FULL file content, integrating with other modules.
        - Maintain consistent naming of variables, functions, and imports.
        - When a module is imported from another file, ensure it exists and is implemented as described.
    """

# ---------------- AGENT NODES ---------------- #

def planner_agent(state: GraphState) -> GraphState:
    """
    Converts user prompt into a structured Plan.
    Supports new plans and edits to an existing plan.
    """
    user_prompt = state.get("user_prompt")
    edit_request = state.get("edit_request")
    previous_plan = state.get("previous_plan")

    if edit_request and previous_plan:
        prompt = f"""
        You previously created this project plan:

        {json.dumps(previous_plan.model_dump(), indent=2)}

        The user wants to make the following edits:

        {edit_request}

        Revise the plan accordingly. Keep as much of the original plan as possible.
        Do not generate a completely new project.
        """
    else:
        prompt = planner_prompt(user_prompt)

    message = llm.with_structured_output(Plan).invoke(prompt)

    if message is None:
        raise ValueError("Planner did not return a valid response.")

    print("[PLANNER] Plan created/revised successfully.")

    return {
        "plan": message,
        "user_prompt": user_prompt,
        "edit_request": None,
        "previous_plan": None
    }

def architect_agent(state: GraphState) -> GraphState:
    """
    Creates or edits a task plan based on the project plan.
    Supports editing existing task plans.
    """
    plan: Plan = state["plan"]
    edit_request = state.get("edit_request")
    previous_task_plan = state.get("previous_task_plan")

    if edit_request and previous_task_plan:
        prompt = f"""
        You previously created this task plan:

        {json.dumps(previous_task_plan.model_dump(), indent=2)}

        The user wants to make the following edits:

        {edit_request}

        Revise the task plan accordingly. Keep as much of the original task plan as possible.
        The project plan is:

        {plan.model_dump_json()}
        """
    else:
        prompt = architect_prompt(plan=plan.model_dump_json())

    message = llm.with_structured_output(TaskPlan).invoke(prompt)
    
    if message is None:
        raise ValueError("Architect did not return a valid response.")
    
    print(f"[ARCHITECT] Created/revised {len(message.implementation_steps)} implementation steps.")
    message.plan = plan

    return {
        "task_plan": message,
        "edit_request": None,
        "previous_task_plan": None
    }

def coder_agent(state: GraphState) -> GraphState:
    """LangGraph tool-using coder agent."""
    coder_state: CoderState = state.get("coder_state")
   
    if coder_state is None:
        coder_state = CoderState(task_plan=state["task_plan"], current_step_idx=0)

    steps = coder_state.task_plan.implementation_steps
    total_steps = len(steps)

    if coder_state.current_step_idx >= total_steps:
        print("\n[CODER] All steps completed.")
        return {"coder_state": coder_state, "status": "DONE"}

    current_task = steps[coder_state.current_step_idx]
    step_num = coder_state.current_step_idx + 1
    print(f"\n[CODER] Step {step_num}/{total_steps}: {current_task.filepath}")
    print(f"Task: {current_task.task_description[:120]}...")

    existing_content = read_file.run(current_task.filepath)

    system_prompt = coder_system_prompt()
    user_prompt = (
        f"Task: {current_task.task_description}\n"
        f"File: {current_task.filepath}\n"
        f"Existing content:\n{existing_content}\n"
        "Use write_file(path, content) to save your changes."
    )

    coder_tools = [read_file, write_file, list_files, get_current_directory]
    react_agent = create_agent(llm, coder_tools)

    start_time = time.time()
    TIMEOUT_SECONDS = 120

    try:
        react_agent.invoke({
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        })
    except Exception as e:
        print(f"[CODER] Error during step: {e}")

    elapsed = time.time() - start_time
    print(f"[CODER] Step completed in {elapsed:.1f}s")

    coder_state.current_step_idx += 1

    if elapsed > TIMEOUT_SECONDS:
        print("[CODER] Timeout exceeded. Exiting early.")
        return {"coder_state": coder_state, "status": "DONE"}

    return {"coder_state": coder_state}

# ---------------- APPROVAL NODES ---------------- #

def approval_planner_node(state: GraphState) -> GraphState:
    plan = state.get("plan")

    print("\n--- PLANNER PLAN REVIEW ---")
    try:
        print(json.dumps(plan.model_dump(), indent=2))
    except Exception:
        print(plan)

    print("\nApprove this project plan? (yes/edit): ", end="", flush=True)
    approved = input().strip().lower()

    if approved == "edit":
        print("What would you like to edit? ", end="", flush=True)
        edit_instructions = input().strip()
        
        if not edit_instructions:
            print("No edits provided. Keeping existing plan.")
            return {"planner_approved": "yes"}

        print(f"Applying edits: {edit_instructions}")
        return {
            "planner_approved": "edit",
            "edit_request": edit_instructions,
            "previous_plan": plan
        }

    return {"planner_approved": "yes"}

def approval_architect_node(state: GraphState) -> GraphState:
    task_plan = state.get("task_plan")

    print("\n--- ARCHITECT TASK PLAN REVIEW ---")
    for i, step in enumerate(task_plan.implementation_steps, 1):
        print(f"\nStep {i}: {step.filepath}")
        print(f"  Description: {step.task_description[:300]}...")

    print("\nApprove this task plan? (yes/edit): ", end="", flush=True)
    approved = input().strip().lower()

    if approved == "edit":
        print("What would you like to edit? ", end="", flush=True)
        edit_instructions = input().strip()

        if not edit_instructions:
            print("No edits provided. Keeping existing task plan.")
            return {"architect_approved": "yes"}

        print(f"Applying edits: {edit_instructions}")
        return {
            "architect_approved": "edit",
            "edit_request": edit_instructions,
            "previous_task_plan": task_plan
        }

    return {"architect_approved": "yes"}

# ---------------- ROUTING FUNCTIONS ---------------- #

def route_planner_approval(state: GraphState) -> Literal["architect", "planner"]:
    """Route based on planner approval decision."""
    if state.get("planner_approved") == "edit":
        return "planner"
    return "architect"

def route_architect_approval(state: GraphState) -> Literal["coder", "architect"]:
    """Route based on architect approval decision."""
    if state.get("architect_approved") == "edit":
        return "architect"
    return "coder"

def route_coder(state: GraphState) -> Literal["coder", "__end__"]:
    """Route coder - continue looping or end."""
    if state.get("status") == "DONE":
        return "__end__"
    return "coder"

# ---------------- GRAPH SETUP ---------------- #

graph = StateGraph(GraphState)

# Add all nodes
graph.add_node("planner", planner_agent)
graph.add_node("approval_planner", approval_planner_node)
graph.add_node("architect", architect_agent)
graph.add_node("approval_architect", approval_architect_node)
graph.add_node("coder", coder_agent)

# Define edges
graph.add_edge("planner", "approval_planner")
graph.add_edge("architect", "approval_architect")

# Add conditional edges with routing functions
graph.add_conditional_edges(
    "approval_planner",
    route_planner_approval,
    {
        "architect": "architect",
        "planner": "planner"
    }
)

graph.add_conditional_edges(
    "approval_architect",
    route_architect_approval,
    {
        "coder": "coder",
        "architect": "architect"
    }
)

graph.add_conditional_edges(
    "coder",
    route_coder,
    {
        "coder": "coder",
        "__end__": END
    }
)

graph.set_entry_point("planner")
agent = graph.compile()

# ---------------- GRAPH VISUALIZATION ---------------- #

def display_graph():
    print("\n3. Saving as PNG image:")
    try:
        img_data = agent.get_graph().draw_mermaid_png()
        with open("graph_visualization.png", "wb") as f:
            f.write(img_data)
        print(" Graph saved as 'graph_visualization.png'")
    except ImportError:
        print(" PNG export requires: pip install pygraphviz or pip install graphviz")
    except Exception as e:
        print(f" PNG export failed: {e}")
    
    print("\n" + "="*50 + "\n")

# ---------------- MAIN LOOP ---------------- #

def main():
    init_project_root()
    
    print("Multi-agent Software Developer is ready.")
    print("Type 'exit' to quit, or 'graph' to visualize the workflow.\n")
    print("What would you like to create!")

    while True:
        user_input = input("\nUser: ").strip()
        
        if user_input.lower() in ["exit", "end", "quit"]:
            print("Goodbye!")
            break
        
        if user_input.lower() == "graph":
            display_graph()
            continue

        try:
            result = agent.invoke({"user_prompt": user_input})
            print("\nProject generation complete!")
        except Exception as e:
            print(f"\n Error during execution: {e}")

if __name__ == "__main__":
    main()
