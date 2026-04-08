import re

class FixLibrary:
    @staticmethod
    def fix_missing_colon(code: str) -> str:
        """Add missing colon after function definition"""
        lines = code.split('\n')
        fixed = []
        for line in lines:
            if 'def ' in line and ':' not in line and line.strip().endswith(')'):
                fixed.append(line + ':')
            else:
                fixed.append(line)
        return '\n'.join(fixed)
    
    @staticmethod
    def fix_missing_return(code: str) -> str:
        """Add missing return statement"""
        lines = code.split('\n')
        for i, line in enumerate(lines):
            if 'def ' in line and 'return' not in code:
                # Find the last line before next function
                for j in range(i+1, len(lines)):
                    if lines[j].strip().startswith('def '):
                        break
                else:
                    # Add return at the end
                    lines.insert(len(lines)-1, '    return None')
                break
        return '\n'.join(lines)
    
    @staticmethod
    def fix_command_injection(code: str) -> str:
        """Replace dangerous system calls with safe alternatives"""
        # Replace os.system with subprocess.run with list args
        code = re.sub(
            r'os\.system\s*\(\s*["\']([^"\']+)["\']\s*\+',
            r'subprocess.run(["\1"].split(), shell=False) +',
            code
        )
        
        # Add import if needed
        if 'subprocess' not in code and ('os.system' in code or 'eval' in code):
            code = 'import subprocess\n' + code
        
        # Replace eval with ast.literal_eval
        code = re.sub(r'eval\s*\(', 'ast.literal_eval(', code)
        
        return code
    
    @staticmethod
    def fix_off_by_one(code: str) -> str:
        """Fix common off-by-one errors"""
        # Fix range(len(list)) patterns
        code = re.sub(
            r'for\s+(\w+)\s+in\s+range\(len\((\w+)\)\):\s*\n\s+(\w+)\s*\+\=\s*\1\[\1\]',
            r'for \1 in range(len(\2)-1):\n    \3 += \2[\1]',
            code
        )
        
        # Fix list[i+1] when i is the index
        lines = code.split('\n')
        fixed = []
        for line in lines:
            if 'range(len(' in line and 'i+1' in code:
                # This is complex - simple fix for demo
                fixed.append(line.replace('i+1', 'i'))
            else:
                fixed.append(line)
        
        return '\n'.join(fixed)
    
    @staticmethod
    def fix_sql_injection(code: str) -> str:
        """Replace string concatenation with parameterized queries"""
        # Pattern: cursor.execute("SELECT ... " + variable)
        pattern = r'cursor\.execute\s*\(\s*["\']([^"\']+)["\']\s*\+\s*(\w+)'
        
        def replacer(match):
            query = match.group(1)
            param = match.group(2)
            return f'cursor.execute("{query}?", ({param},))'
        
        code = re.sub(pattern, replacer, code)
        
        # Add placeholder for multiple params
        code = re.sub(
            r'cursor\.execute\s*\(\s*f["\']([^"\']+)["\']',
            r'cursor.execute("\1", params)',
            code
        )
        
        return code
    
    @staticmethod
    def fix_infinite_loop(code: str) -> str:
        """Add safety to while loops"""
        lines = code.split('\n')
        fixed = []
        for line in lines:
            if 'while True:' in line:
                fixed.append('    counter = 0')
                fixed.append('    while counter < 1000:  # Safety limit')
                fixed.append('        counter += 1')
            else:
                fixed.append(line)
        return '\n'.join(fixed)
    
    @staticmethod
    def fix_typo(code: str) -> str:
        """Fix common variable typos"""
        # reslt -> result
        code = code.replace('reslt', 'result')
        # retun -> return
        code = code.replace('retun', 'return')
        # lenght -> length
        code = code.replace('lenght', 'length')
        
        return code
    
    @staticmethod
    def add_error_handling(code: str) -> str:
        """Add try-except blocks"""
        if 'try:' not in code and 'except' not in code:
            lines = code.split('\n')
            indented = []
            for line in lines:
                if line.strip() and not line.startswith('def ') and not line.startswith('import '):
                    indented.append('    ' + line)
                else:
                    indented.append(line)
            
            # Insert try-except wrapper
            try_block = ['try:']
            try_block.extend(indented)
            try_block.append('except Exception as e:')
            try_block.append('    print(f"Error: {e}")')
            try_block.append('    return None')
            
            return '\n'.join(try_block)
        
        return code

# List of all available fixes
ALL_FIXES = [
    FixLibrary.fix_missing_colon,
    FixLibrary.fix_missing_return,
    FixLibrary.fix_command_injection,
    FixLibrary.fix_off_by_one,
    FixLibrary.fix_sql_injection,
    FixLibrary.fix_infinite_loop,
    FixLibrary.fix_typo,
    FixLibrary.add_error_handling,
]