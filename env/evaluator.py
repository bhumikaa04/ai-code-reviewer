# gives the score to the code 
from env.metrics import CodeMetrics

def evaluate_code(code : str) -> float : 
    metrics = CodeMetrics.total_score(code)
    
    return metrics["total"]

def get_detailed_score(code : str) -> dict : 
    """breakdown of the code for debugging """
    return CodeMetrics.total_score(code)