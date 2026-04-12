from fastapi import FastAPI, Request
from pydantic import BaseModel
import uvicorn

app = FastAPI()

class Action(BaseModel):
    action_type: str
    payload: str

TASKS = ["easy-syntax", "medium-refactor", "hard-security"]
current_task = "easy-syntax"
step_count = 0

@app.get("/")
def health_check():
    return {"status": "ok"}

@app.post("/reset")
async def reset_env(request: Request):
    global step_count, current_task
    step_count = 0
    # Try to safely read if the AI asked for a specific task
    try:
        body = await request.json()
        if body and "task_id" in body and body["task_id"] in TASKS:
            current_task = body["task_id"]
    except:
        pass # If no body is sent by the validator, just reset normally
    return state_env()

@app.get("/state")
def state_env():
    if current_task == "easy-syntax":
        code = "def add(a, b)\n  return a + b"
    elif current_task == "medium-refactor":
        code = "def extract_emails(text):\n  pass"
    else:
        code = "def sanitize_sql(user_input):\n  pass"
        
    return {
        "observation": {
            "task": current_task,
            "code_snippet": code,
            "status": f"Step {step_count}/3"
        }
    }

@app.post("/step")
def step_env(action: Action):
    global step_count
    step_count += 1
    
    # Base reward strictly between 0 and 1
    reward = 0.01
    done = False
    error = None

    if step_count >= 3:
        done = True
        error = "Max steps reached"
    elif action.action_type == "submit":
        done = True
        payload = action.payload.lower()
        
        # Grade based on the current task (0.99 for success, 0.01 for failure)
        if current_task == "easy-syntax":
            if "def add(a, b):" in payload:
                reward = 0.99
        elif current_task == "medium-refactor":
            if "re.findall" in payload or "import re" in payload or "set(" in payload:
                reward = 0.99
        elif current_task == "hard-security":
            if "replace" in payload or "?" in payload or "escape" in payload:
                reward = 0.99

    return {
        "observation": state_env()["observation"],
        "reward": reward,
        "done": done,
        "info": {"error": error}
    }

def main():
    uvicorn.run("server.app:app", host="0.0.0.0", port=7860)

if __name__ == "__main__":
    main()
