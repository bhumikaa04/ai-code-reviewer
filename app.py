import os
import gradio as gr
import asyncio
from env.code_env import CodeEnvironment

# Default code
init_code = "def add(a, b):\n    return a + b"

async def run_review(user_code, fix_suggestion):
    if not fix_suggestion.strip():
        return (
            user_code,
            "0.00",
            "⚠️ No fix provided",
            {"error": "Empty suggested fix"}
        )

    # Create fresh environment
    env = CodeEnvironment(code=user_code)
    await env.reset()

    # Mock action
    class MockAction:
        def __init__(self, fix):
            self.suggested_fix = fix

    action = MockAction(fix_suggestion)

    try:
        obs, reward, done, info = await env.step(action)

        return (
            obs.code,
            f"{reward:.2f}",
            "✅ Success" if done else "🔄 Iterating...",
            info
        )

    except Exception as e:
        return (
            user_code,
            "0.00",
            "❌ Error occurred",
            {"error": str(e)}
        )

# --- UI ---
with gr.Blocks(title="AI Code Reviewer (RL)", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🤖 AI Code Reviewer (Reinforcement Learning)")
    gr.Markdown("Fix buggy Python code and observe RL-based reward feedback 🚀")

    with gr.Row():
        with gr.Column():
            code_input = gr.Textbox(
                label="Original Code",
                value=init_code,
                lines=12
            )

            fix_input = gr.Textbox(
                label="Suggested Fix (Agent Action)",
                placeholder="Paste improved code here...",
                lines=12
            )

            btn = gr.Button("🚀 Run RL Step", variant="primary")

        with gr.Column():
            code_output = gr.Textbox(
                label="Updated Code (Observation)",
                lines=12,
                interactive=False
            )

            reward_output = gr.Textbox(label="Reward")
            status_output = gr.Textbox(label="Status")
            details_output = gr.JSON(label="Execution Details")

    btn.click(
        fn=run_review,
        inputs=[code_input, fix_input],
        outputs=[code_output, reward_output, status_output, details_output]
    )

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)