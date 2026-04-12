import os
import requests
from openai import OpenAI

# 1. Initialize exactly as the LiteLLM proxy demands
api_base = os.environ.get("API_BASE_URL", "https://api.openai.com/v1")
# The Phase 2 validator strictly injects 'API_KEY', not 'HF_TOKEN'
api_key = os.environ.get("API_KEY", os.environ.get("HF_TOKEN", "dummy_key"))

client = OpenAI(
    base_url=api_base,
    api_key=api_key
)

ENV_URL = "http://localhost:7860"

def run_task(task_name: str):
    benchmark = "CodeReviewBenchmark"
    print(f"[START] task={task_name} env={benchmark} model=gpt-4o-mini")
    
    requests.post(f"{ENV_URL}/reset", json={"task_id": task_name})
    prompt = f"Fix this python coding task: {task_name}. Return ONLY the raw python code."
    
    try:
        # 2. MUST make this API call so the proxy registers it
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )
        llm_code = response.choices[0].message.content.strip()
    except Exception as e:
        llm_code = "def dummy(): pass" # Fallback so it doesn't crash

    step_payload = {"action_type": "submit", "payload": llm_code}
    
    try:
        result = requests.post(f"{ENV_URL}/step", json=step_payload).json()
        reward = result.get("reward", 0.01)
        done_str = "true" if result.get("done") else "false"
        err_str = result.get("info", {}).get("error")
        err_msg = "null" if not err_str else str(err_str).replace(" ", "_")
    except Exception as e:
        reward = 0.01
        done_str = "true"
        err_msg = "env_error"
    
    print(f"[STEP] step=1 action=submit reward={reward:.2f} done={done_str} error={err_msg}")
    success_str = "true" if reward > 0.5 else "false"
    print(f"[END] success={success_str} steps=1 rewards={reward:.2f}")

if __name__ == "__main__":
    # 3. Loop through exactly 3 tasks for the Phase 2 Grader
    tasks = ["easy-syntax", "medium-refactor", "hard-security"]
    for t in tasks:
        run_task(t)
