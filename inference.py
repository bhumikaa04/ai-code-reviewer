
import asyncio
import os
from openai import OpenAI
from env.code_env import CodeEnvironment, CodeAction

# =========================
# ENV VARIABLES
# =========================
API_KEY = os.getenv("HF_TOKEN")
API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-Coder-7B-Instruct")

MAX_STEPS = 5
MAX_TOTAL_REWARD = 5.0
SUCCESS_THRESHOLD = 0.8

# =========================
# LOGGING (STRICT FORMAT)
# =========================
def log_start(task):
    print(f"[START] task={task} env=CodeEnv model={MODEL_NAME}", flush=True)

def log_step(step, reward, done):
    print(f"[STEP] step={step} reward={reward:.2f} done={str(done).lower()}", flush=True)

def log_end(success, steps, score, rewards):
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(f"[END] success={str(success).lower()} steps={steps} score={score:.2f} rewards={rewards_str}", flush=True)

# =========================
# CLEAN LLM OUTPUT
# =========================
def clean_code(text):
    if "`" in text:
        parts = text.split("`")
        # Handle cases like ```python code ``` or `code`
        if len(parts) >= 2:
            # If it starts with ```python, the code is in the 2nd part
            text = parts[1] if parts[1] else parts[2]
        text = text.replace("python", "")
    return text.strip()

# =========================
# LLM CALL
# =========================
def get_llm_fix(client, code):
    prompt = f"""
You are a code repair agent.
Fix the following Python code.
Return ONLY the corrected code.
Do NOT include explanations.
Code:
{code}
"""
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = response.choices[0].message.content or ""
        return clean_code(raw)
    except Exception as e:
        print(f"[DEBUG] LLM error: {e}", flush=True)
        return code

# =========================
# RUN TASK
# =========================
async def run_task(task_name, code, test_cases):
    client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)
    env = CodeEnvironment(code, test_cases=test_cases)

    log_start(task_name)

    obs = await env.reset()
    total_reward = 0.0
    steps_taken = 0
    done = False
    rewards = []

    while not done and steps_taken < MAX_STEPS:
        steps_taken += 1

        # Generate fix using LLM
        suggested_code = get_llm_fix(client, obs.code)

        obs, reward, done, info = await env.step(
            CodeAction(suggested_fix=suggested_code)
        )

        total_reward += reward
        rewards.append(reward)

        log_step(steps_taken, reward, done)

    score = min(max(total_reward / MAX_TOTAL_REWARD, 0.0), 1.0)
    success = any(step_reward >= 1.0 for step_reward in rewards) or (score >= SUCCESS_THRESHOLD)

    log_end(success, steps_taken, score, rewards)

# =========================
# TASKS (EASY → MEDIUM → HARD)
# =========================
TASKS = [
    {
        "name": "Easy",
        "code": "def add(a,b):\n    return a+b", # Fixed missing colon for initialization
        "tests": [
            {"func": "add", "input": [2, 3], "output": 5},
            {"func": "add", "input": [1, 1], "output": 2},
        ],
    },
    {
        "name": "Medium",
        "code": "def sum_list(lst):\n    s = 0\n    for i in range(len(lst)):\n        s += lst[i]",
        "tests": [
            {"func": "sum_list", "input": [[1, 2, 3]], "output": 6},
        ],
    },
    {
        "name": "Hard",
        "code": "import os\ndef dangerous(x):\n    return eval(x)",
        "tests": [
            {"func": "dangerous", "input": ["2+3"], "output": 5},
        ],
    }
]

# =========================
# MAIN
# =========================
async def main():
    for task in TASKS:
        await run_task(task["name"], task["code"], task["tests"])

if __name__ == "__main__":
    asyncio.run(main())