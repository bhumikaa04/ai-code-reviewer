from pydantic import BaseModel
from env.evaluator import evaluate_code, get_detailed_score


class CodeObservation(BaseModel):
    code: str


class CodeAction(BaseModel):
    suggested_fix: str


class CodeEnvironment:

    def __init__(self, code, max_steps=5, test_cases=None):
        self.original_code = code
        self.current_code = code
        self.test_cases = test_cases or []
        self.max_steps = max_steps
        self.steps_taken = 0

    def state(self):
        return {"code": self.current_code}

    def safe_execute(self, code):
        try:
            local_env = {}
            exec(code, {}, local_env)

            if not self.test_cases:
                return 0.5

            passed = 0
            for test in self.test_cases:
                if test["func"] not in local_env:
                    return 0.0

                result = local_env[test["func"]](*test["input"])
                if result == test["output"]:
                    passed += 1

            return passed / len(self.test_cases)

        except Exception as e:
            print(f"[DEBUG] Execution error: {e}")
            return 0.0

    async def step(self, action: CodeAction):
        self.steps_taken += 1

        old_score = evaluate_code(self.current_code)
        old_details = get_detailed_score(self.current_code)

        new_code = action.suggested_fix

        new_score = evaluate_code(new_code)
        new_details = get_detailed_score(new_code)

        exec_score = self.safe_execute(new_code)

        reward = (new_score - old_score)
        reward += 0.5 * exec_score
        reward += 0.1 * (new_details["security"] - old_details["security"])

        if new_score == old_score:
            reward -= 0.1

        reward -= 0.02
        reward = max(min(reward, 1.0), -1.0)

        self.current_code = new_code

        done = (exec_score == 1.0) or (self.steps_taken >= self.max_steps)

        info = {
            "old_score": old_score,
            "new_score": new_score,
            "exec_score": exec_score,
            "details": new_details,
            "steps_used": self.steps_taken
        }

        return CodeObservation(code=self.current_code), reward, done, info

    async def reset(self):
        self.current_code = self.original_code
        self.steps_taken = 0
        return CodeObservation(code=self.current_code)
      
