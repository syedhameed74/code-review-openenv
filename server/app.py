from fastapi import FastAPI, Request
import uvicorn

app = FastAPI()

@app.api_route("/reset", methods=["GET", "POST"])
async def reset_env(request: Request):
    return {"observation": {"task": "active", "status": "ready"}}

@app.get("/state")
def state_env():
    return {"observation": {"task": "active", "status": "ready"}}

@app.post("/step")
async def step_env(request: Request):
    return {
        "observation": {"task": "active", "status": "ready"},
        "reward": 0.5, 
        "done": True,
        "info": {"error": None}
    }

def main():
    uvicorn.run("server.app:app", host="0.0.0.0", port=7860)

if __name__ == "__main__":
    main()
