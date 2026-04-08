import os
import requests
from openai import OpenAI

API_BASE_URL = os.getenv("API_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")
HF_TOKEN = os.getenv("HF_TOKEN")

if HF_TOKEN is None:
    raise ValueError("HF_TOKEN environment variable is required")

client = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN)
ENV_URL = "http://localhost:7860"

def run_evaluation():
    task_name = "easy-syntax"
    benchmark = "CodeReviewBenchmark"
    
    print(f"[START] task={task_name} env={benchmark} model={MODEL_NAME}")
    requests.post(f"{ENV_URL}/reset")
    
    prompt = "Fix this python syntax error and return only the code: 'def add(a, b)\\n  return a + b'"
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )
        llm_code = response.choices[0].message.content.replace("```python", "").replace("```", "").strip()
    except Exception as e:
        print(f"[STEP] step=1 action=llm_call reward=0.00 done=true error=API_Error")
        print("[END] success=false steps=1 rewards=0.00")
        return

    step_payload = {"action_type": "submit", "payload": llm_code}
    result = requests.post(f"{ENV_URL}/step", json=step_payload).json()
    
    reward = result["reward"]
    done_str = "true" if result["done"] else "false"
    err_str = result["info"].get("error")
    err_msg = "null" if not err_str else str(err_str).replace(" ", "_")
    
    print(f"[STEP] step=1 action=submit reward={reward:.2f} done={done_str} error={err_msg}")
    
    success_str = "true" if reward == 1.0 else "false"
    print(f"[END] success={success_str} steps=1 rewards={reward:.2f}")

if __name__ == "__main__":
    run_evaluation()