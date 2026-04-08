from pydantic import BaseModel
from typing import Tuple, Dict, Any
import traceback

class Observation(BaseModel):
    task_description: str
    code_snippet: str
    current_status: str

class Action(BaseModel):
    action_type: str # 'submit'
    payload: str     # The actual code

class CodeReviewEnv:
    def __init__(self, task_id: str = "easy-syntax"):
        self.task_id = task_id
        self.step_count = 0
        self.max_steps = 3
        
        # Real-world task setups
        self.tasks = {
            "easy-syntax": {
                "desc": "The 'calculate_discount' function has a bug. Fix it so it correctly applies a 20% discount.",
                "code": "def calculate_discount(price):\n  return price - (price * 20)"
            },
            "medium-refactor": {
                "desc": "Write a function 'extract_emails(text)' that uses the 're' module to return a list of all valid email addresses in a string.",
                "code": "import re\n\ndef extract_emails(text):\n  # Write code here\n  pass"
            },
            "hard-security": {
                "desc": "Write a function 'sanitize_sql_input(user_input)' that escapes single quotes to prevent SQL injection, returning the safe string.",
                "code": "def sanitize_sql_input(user_input):\n  # Write code here\n  pass"
            }
        }
        self.reset()

    def reset(self) -> Observation:
        self.step_count = 0
        self.current_code = self.tasks[self.task_id]["code"]
        return self.state()

    def state(self) -> Observation:
        return Observation(
            task_description=self.tasks[self.task_id]["desc"],
            code_snippet=self.current_code,
            current_status=f"Step {self.step_count}/{self.max_steps}"
        )

    def step(self, action: Action) -> Tuple[Observation, float, bool, Dict[str, Any]]:
        self.step_count += 1
        info = {"error": None}

        if self.step_count >= self.max_steps:
            return self.state(), -1.0, True, {"error": "Max steps reached"}

        if action.action_type == "submit":
            score, err = self._grade_task(action.payload)
            info["error"] = err
            return self.state(), score, True, info

        return self.state(), 0.0, False, info

    def _grade_task(self, final_code: str) -> Tuple[float, str]:
        """Dynamically executes the submitted code and runs hidden unit tests."""
        local_scope = {}
        try:
            # Execute the LLM's code safely into the local_scope dictionary
            exec(final_code, globals(), local_scope)
            
            if self.task_id == "easy-syntax":
                func = local_scope.get("calculate_discount")
                if not func: return 0.0, "Function calculate_discount not found."
                # Hidden tests
                if func(100) == 80.0 and func(50) == 40.0:
                    return 1.0, None
                return 0.0, "Fails mathematical logic tests."

            elif self.task_id == "medium-refactor":
                func = local_scope.get("extract_emails")
                if not func: return 0.0, "Function extract_emails not found."
                test_str = "Contact admin@meta.com or support@google.org for help."
                result = func(test_str)
                if result == ["admin@meta.com", "support@google.org"]:
                    return 1.0, None
                return 0.0, "Failed to extract correct emails."

            elif self.task_id == "hard-security":
                func = local_scope.get("sanitize_sql_input")
                if not func: return 0.0, "Function sanitize_sql_input not found."
                test_str = "O'Connor'; DROP TABLE users;--"
                expected = "O''Connor''; DROP TABLE users;--"
                if func(test_str) == expected:
                    return 1.0, None
                return 0.0, "Failed to escape single quotes properly."

        except Exception as e:
            return 0.0, f"Execution Error: {str(e)}"
            
        return 0.0, "Unknown failure."