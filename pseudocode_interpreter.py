import re

class PseudocodeInterpreter:
    def __init__(self):
        self.variables = {}

    def interpret(self, pseudocode):
        lines = pseudocode.split('\n')
        output = []
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if line and not line.startswith('#'):  # Ignore empty lines and comments
                try:
                    result, i = self.execute_line(lines, i)
                    if result is not None:
                        output.append(result)
                except Exception as e:
                    output.append(f"Error on line {i + 1}: {str(e)}")
            i += 1
        return '\n'.join(output)

    def execute_line(self, lines, i):
        line = lines[i].strip()
        if line.startswith('PRINT'):
            return self.print_statement(line), i
        elif '=' in line:
            return self.assignment(line), i
        elif line.startswith('IF'):
            return self.if_statement(lines, i)
        elif line.startswith('FOR'):
            return self.for_loop(lines, i)
        elif line.startswith('WHILE'):
            return self.while_loop(lines, i)
        else:
            raise ValueError(f"Unsupported command: {line}")

    def print_statement(self, line):
        match = re.match(r'PRINT\s+(.+)', line)
        if match:
            content = match.group(1)
            if content.startswith('"') and content.endswith('"'):
                return content[1:-1]  # Remove quotes for string literals
            else:
                # Treat text without quotes as string literal
                return content
        raise ValueError(f"Invalid PRINT statement: {line}")

    def assignment(self, line):
        variable, expression = map(str.strip, line.split('='))
        self.variables[variable] = self.evaluate_expression(expression)

    def if_statement(self, lines, i):
        condition_match = re.match(r'IF\s+(.+)\s+THEN', lines[i])
        if not condition_match:
            raise ValueError(f"Invalid IF statement on line {i + 1}: {lines[i]}")
        
        condition = condition_match.group(1)
        i += 1
        true_block = []
        false_block = []
        
        while i < len(lines) and not lines[i].strip().startswith('ELSE') and not lines[i].strip().startswith('ENDIF'):
            true_block.append(lines[i])
            i += 1
        
        if i < len(lines) and lines[i].strip().startswith('ELSE'):
            i += 1
            while i < len(lines) and not lines[i].strip().startswith('ENDIF'):
                false_block.append(lines[i])
                i += 1
        
        if i < len(lines) and lines[i].strip().startswith('ENDIF'):
            i += 1
        else:
            raise ValueError(f"IF statement not properly closed with ENDIF, starting from line {i + 1}")
        
        if self.evaluate_expression(condition):
            result = self.interpret('\n'.join(true_block))
        else:
            result = self.interpret('\n'.join(false_block))
        
        return result, i - 1

    def for_loop(self, lines, i):
        match = re.match(r'FOR\s+(\w+)\s+FROM\s+(\d+)\s+TO\s+(\d+)\s+DO', lines[i])
        if not match:
            raise ValueError(f"Invalid FOR loop on line {i + 1}: {lines[i]}")
        
        var, start, end = match.groups()
        i += 1
        loop_block = []
        
        while i < len(lines) and not lines[i].strip().startswith('ENDFOR'):
            loop_block.append(lines[i])
            i += 1
        
        if i < len(lines) and lines[i].strip().startswith('ENDFOR'):
            i += 1
        else:
            raise ValueError(f"FOR loop not properly closed with ENDFOR, starting from line {i + 1}")
        
        output = []
        for j in range(int(start), int(end) + 1):
            self.variables[var] = j
            result = self.interpret('\n'.join(loop_block))
            if result:
                output.append(result)
        
        return '\n'.join(output), i - 1

    def while_loop(self, lines, i):
        condition_match = re.match(r'WHILE\s+(.+)', lines[i])
        if not condition_match:
            raise ValueError(f"Invalid WHILE statement on line {i + 1}: {lines[i]}")
        
        condition = condition_match.group(1)
        i += 1
        loop_block = []
        
        while i < len(lines) and not lines[i].strip().startswith('ENDWHILE'):
            loop_block.append(lines[i])
            i += 1
        
        if i < len(lines) and lines[i].strip().startswith('ENDWHILE'):
            i += 1
        else:
            raise ValueError(f"WHILE loop not properly closed with ENDWHILE, starting from line {i + 1}")
        
        output = []
        while self.evaluate_expression(condition):
            result = self.interpret('\n'.join(loop_block))
            if result:
                output.append(result)
        
        return '\n'.join(output), i - 1

    def evaluate_expression(self, expression):
        try:
            # Handle string literals
            if expression.startswith('"') and expression.endswith('"'):
                return expression[1:-1]  # Remove quotes for string literals
            
            # Replace variable names with their values
            for var, value in self.variables.items():
                expression = re.sub(r'\b' + var + r'\b', str(value), expression)
            
            # Evaluate basic arithmetic operations and comparisons
            return eval(expression, {"__builtins__": None}, {
                "+": lambda x, y: x + y,
                "-": lambda x, y: x - y,
                "*": lambda x, y: x * y,
                "/": lambda x, y: x / y,
                "<": lambda x, y: x < y,
                ">": lambda x, y: x > y,
                "<=": lambda x, y: x <= y,
                ">=": lambda x, y: x >= y,
                "==": lambda x, y: x == y,
                "!=": lambda x, y: x != y,
            })
        except Exception as e:
            raise ValueError(f"Invalid expression: {expression}. Error: {str(e)}")
