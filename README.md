# 🚀 CodeReviewEnv: OpenEnv Hackathon Submission

**CodeReviewEnv** is a real-world Reinforcement Learning (RL) environment designed to evaluate an AI agent's ability to perform automated code review, debugging, and secure refactoring. 

This project was built for the **Meta OpenEnv Hackathon** and fully implements the OpenEnv specification, including a FastAPI server runtime, typed Pydantic models, and programmatic grading via dynamic code execution.

---

## 📖 Environment Overview and Motivation

The hackathon explicitly requires tasks that humans actually perform in real settings (no games or toy problems). Code review and automated pull-request remediation are critical bottlenecks in modern software engineering. 

**CodeReviewEnv** simulates this real-world workflow. The agent is presented with a buggy, inefficient, or insecure code snippet and a description of the desired outcome. The agent must rewrite the code and submit it. The environment then safely executes the agent's code in a sandboxed runtime against hidden unit tests to deterministically grade its correctness, logic, and security.

---

## 🔍 Definitions of Action and Observation Spaces

The environment uses strictly typed Pydantic models to define how the agent perceives and interacts with the sandbox.

### Observation Space
The observation space provides the agent with the context needed to fix the code.
* `task_description` (string): Human-readable instructions explaining the bug or feature request.
* `code_snippet` (string): The current state of the python code that needs to be fixed.
* `status` (string): The current step count (e.g., "Step 1/3") to provide temporal awareness.

### Action Space
The agent interacts with the environment by submitting newly written code.
* `action_type` (string): The type of action being taken (currently strictly `"submit"`).
* `payload` (string): The complete, executable Python code authored by the LLM.

---

## 📋 Task Descriptions & Difficulty Levels

The environment features three built-in tasks that scale sequentially in difficulty. Each task uses a programmatic execution grader that outputs a reward strictly between `0.0` and `1.0`.

1. **`easy-syntax` (Easy)**
   * **Objective:** Identify and fix a mathematical logic error in a simple discount calculation function.
   * **Grader:** Executes the function and runs hidden mathematical unit tests `(e.g., func(100) == 80.0)`.
2. **`medium-refactor` (Medium)**
   * **Objective:** Refactor an empty function to extract valid email addresses from a string using the `re` module.
   * **Grader:** Passes a complex hidden string to the agent's function and verifies the exact list output.
3. **`hard-security` (Hard)**
   * **Objective:** Patch a vulnerable SQL query builder by writing a function that properly escapes single quotes to prevent SQL injection.
   * **Grader:** Tests the agent's function against a known malicious SQL injection string `(O'Connor'; DROP TABLE users;--)` to ensure safe string escaping.

---

## 🛠 Setup and Usage Instructions

This environment is fully containerized and deployable on Hugging Face Spaces.

### 1. Environment Variables
To run the baseline inference script, you must provide your OpenAI credentials.
```bash
export API_BASE_URL="[https://api.openai.com/v1](https://api.openai.com/v1)"
export MODEL_NAME="gpt-4o-mini"
export HF_TOKEN="your_openai_api_key_here"
