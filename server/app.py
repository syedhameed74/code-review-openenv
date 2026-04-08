from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, Any
import uvicorn

app = FastAPI()

class Action(BaseModel):
    action_type: str
    payload: str

current_task = "easy-syntax"
step_count = 0

@app.get("/")
def health_check():
    return {"status": "ok"}

@app.post("/reset")
def reset_env():
    global step_count
    step_count = 0
    return state_env()

@app.get("/state")
def state_env():
    code_snippet = "def add(a, b)\n  return a + b" if current_task == "easy-syntax" else "# Other task code"
    return {
        "observation": {
            "task": current_task,
            "code_snippet": code_snippet,
            "status": f"Step {step_count}/3"
        }
    }

@app.post("/step")
def step_env(action: Action):
    global step_count
    step_count += 1
    
    reward = 0.0
    done = False
    error = None

    if step_count >= 3:
        done = True
        error = "Max steps reached"
    elif action.action_type == "submit":
        done = True
        if "def add(a, b):" in action.payload:
            reward = 1.0
        else:
            error = "Failed syntax check"

    return {
        "observation": state_env()["observation"],
        "reward": reward,
        "done": done,
        "info": {"error": error}
    }

# --- Added this section to satisfy the openenv validator! ---
def main():
    uvicorn.run("server.app:app", host="0.0.0.0", port=7860)

if __name__ == "__main__":
    main()
