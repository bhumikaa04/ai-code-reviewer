from env.metrics import CodeMetrics

def encode_state(code):
    metrics = CodeMetrics.total_score(code)

    state = []

    # Syntax
    if metrics["syntax"] == 1:
        state.append("syntax_ok")
    else:
        state.append("syntax_error")

    # Logic
    if "return" not in code:
        state.append("missing_return")

    if "range(len(" in code:
        state.append("loop_indexing")

    if "+1" in code:
        state.append("possible_off_by_one")

    # Security
    if "os.system" in code:
        state.append("command_injection")

    if "eval(" in code:
        state.append("dangerous_eval")

    # Style
    if any(len(line) > 79 for line in code.split("\n")):
        state.append("long_line")

    return tuple(sorted(state))