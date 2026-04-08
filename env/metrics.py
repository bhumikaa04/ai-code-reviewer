# contains the working of Multi-Metric Scoring 

import ast
import re

class CodeMetrics : 
    @staticmethod
    def syntax_score(code : str) -> float : 
        """0.0 = broken , 1.0 = perfect syntax"""
        try : 
            compile(code, "<string>" , "exec")
            return 1.0
        except : 
            return 0.0 
        
    @staticmethod
    def security_score(code: str) -> float:
        score = 1.0

        dangerous_patterns = [
            r"eval\s*\(",
            r"exec\s*\(",
            r"__import__\s*\(",
            r"os\.system\s*\(",
            r"subprocess\.call\s*\(",
            r"subprocess\.Popen\s*\(",
        ]

        for pattern in dangerous_patterns:
            if re.search(pattern, code):
                score -= 0.3

        return max(0.0, score)

    @staticmethod 
    def logic_score(code : str , test_cases : dict = None) -> float : 
        """Detect common Logic bugs"""
        score = 1.0 
        # Off-by-one errors
        if "range(len(" in code and "+ 1" not in code and "- 1" not in code:
            score -= 0.2
        
        # Missing return
        if "def " in code and "return" not in code:
            score -= 0.3
        
        # Infinite loop risk
        if "while True:" in code and "break" not in code:
            score -= 0.3
        
        # Uninitialized variable usage
        lines = code.split('\n')
        for line in lines:
            if '=' in line and '+' in line and '=' not in line.split('+')[0].strip():
                # Using variable before assignment pattern
                pass
        
        return max(0.0, score)

    @staticmethod 
    def style_score(code : str) -> float : 
        """PEP 8 style checks"""
        score = 1.0 

        # Indentation issues
        lines = code.split('\n')
        for line in lines:
            if line.strip() and not line.startswith(' ') and not line.startswith('\t'):
                if line.startswith('def ') or line.startswith('class '):
                    pass  # top-level is fine
                elif line.strip():
                    # Should be indented
                    pass
        
        # Line too long
        for line in lines:
            if len(line) > 79:
                score -= 0.05
        
        # Missing spaces around operators
        if re.search(r'[a-zA-Z0-9]\+[a-zA-Z0-9]', code):
            score -= 0.1
        
        return max(0.0, score)

    @staticmethod
    def total_score(code: str, test_cases: dict = None) -> dict:
        """Return comprehensive scoring"""
        return {
            "syntax": CodeMetrics.syntax_score(code),
            "security": CodeMetrics.security_score(code),
            "logic": CodeMetrics.logic_score(code),
            "style": CodeMetrics.style_score(code),
            "total": (
                CodeMetrics.syntax_score(code) * 0.3 +
                CodeMetrics.security_score(code) * 0.3 +
                CodeMetrics.logic_score(code) * 0.2 +
                CodeMetrics.style_score(code) * 0.2
            )
        }