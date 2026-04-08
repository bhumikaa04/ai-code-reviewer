def fix_missing_colon(code : str) -> str : 
    return code.replace("def add(a, b)" , "def add (a, b) :")

def fix_return_statement(code : str) -> str : 
    return code.replace("a + b" , "return a + b")

def fix_syntax_error(code : str) -> str : 
    return code.replace("return a *" , "return a * b")

def fix_indentation_error(code : str) -> str :
    return code.replace("\nreturn" , "\n     return")

class BasicAgent : 
    def __init__(self):
        self.actions =  [
            fix_missing_colon , 
            fix_return_statement, 
            fix_indentation_error, 
            fix_syntax_error
        ]

    def act(self , code) : 
        return self.actions 
