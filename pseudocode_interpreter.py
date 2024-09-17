import re

class PseudocodeInterpreter:
    def __init__(self):
        self.variables = {}
        self.functions = {}

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
        elif line.startswith('FUNCTION'):
            return self.function_definition(lines, i)
        elif line.startswith('CALL'):
            return self.function_call(line), i
        elif line.startswith('ARRAY'):
            return self.array_declaration(line), i
        else:
            raise ValueError(f"Unsupported command: {line}")

    def print_statement(self, line):
        match = re.match(r'PRINT\s+(.+)', line)
        if match:
            content = match.group(1)
            if content.startswith('"') and content.endswith('"'):
                return content[1:-1]  # Remove quotes for string literals
            elif any(op in content for op in ['+', '-', '*', '/', '<', '>', '<=', '>=', '==', '!=']):
                return str(self.evaluate_expression(content))
            else:
                return content  # Return as-is for non-expression content
        raise ValueError(f"Invalid PRINT statement: {line}")

    def assignment(self, line):
        variable, expression = map(str.strip, line.split('='))
        if '[' in variable:  # Array assignment
            array_name, index = re.match(r'(\w+)\[(.+)\]', variable).groups()
            index = int(self.evaluate_expression(index))
            if array_name not in self.variables or not isinstance(self.variables[array_name], list):
                raise ValueError(f"Array '{array_name}' is not defined or is not an array")
            if index < 0 or index >= len(self.variables[array_name]):
                raise ValueError(f"Index {index} is out of bounds for array '{array_name}'")
            self.variables[array_name][index] = self.evaluate_expression(expression)
        else:
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
        match = re.match(r'FOR\s+(\w+)\s+FROM\s+(.+)\s+TO\s+(.+)\s+DO', lines[i])
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
        
        start_value = int(self.evaluate_expression(start))
        end_value = int(self.evaluate_expression(end))
        output = []
        for j in range(start_value, end_value + 1):
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

    def function_definition(self, lines, i):
        match = re.match(r'FUNCTION\s+(\w+)\s*\((.*?)\)', lines[i])
        if not match:
            raise ValueError(f"Invalid function definition on line {i + 1}: {lines[i]}")
        
        func_name, params = match.groups()
        params = [p.strip() for p in params.split(',') if p.strip()]
        i += 1
        func_body = []
        
        while i < len(lines) and not lines[i].strip().startswith('ENDFUNCTION'):
            func_body.append(lines[i])
            i += 1
        
        if i < len(lines) and lines[i].strip().startswith('ENDFUNCTION'):
            i += 1
        else:
            raise ValueError(f"Function not properly closed with ENDFUNCTION, starting from line {i + 1}")
        
        self.functions[func_name] = {
            'params': params,
            'body': func_body
        }
        
        return None, i - 1

    def function_call(self, line):
        match = re.match(r'CALL\s+(\w+)\s*\((.*?)\)', line)
        if not match:
            raise ValueError(f"Invalid function call: {line}")
        
        func_name, args = match.groups()
        args = [self.evaluate_expression(arg.strip()) for arg in args.split(',') if arg.strip()]
        
        if func_name not in self.functions:
            raise ValueError(f"Function '{func_name}' is not defined")
        
        func = self.functions[func_name]
        if len(args) != len(func['params']):
            raise ValueError(f"Function '{func_name}' expects {len(func['params'])} arguments, but {len(args)} were given")
        
        # Create a new scope for the function
        old_variables = self.variables.copy()
        self.variables.update(dict(zip(func['params'], args)))
        
        result = self.interpret('\n'.join(func['body']))
        
        # Restore the old scope
        self.variables = old_variables
        
        return result

    def array_declaration(self, line):
        match = re.match(r'ARRAY\s+(\w+)\s*\[(\d+)\]', line)
        if not match:
            raise ValueError(f"Invalid array declaration: {line}")
        
        array_name, size = match.groups()
        self.variables[array_name] = [0] * int(size)

    def evaluate_expression(self, expression):
        try:
            # Handle string literals
            if expression.startswith('"') and expression.endswith('"'):
                return expression[1:-1]  # Remove quotes for string literals
            
            # Handle array access
            array_access = re.match(r'(\w+)\[(.+)\]', expression)
            if array_access:
                array_name, index = array_access.groups()
                index = int(self.evaluate_expression(index))
                if array_name not in self.variables:
                    raise ValueError(f"Array '{array_name}' is not defined")
                if not isinstance(self.variables[array_name], list):
                    raise ValueError(f"'{array_name}' is not an array")
                if index < 0 or index >= len(self.variables[array_name]):
                    raise ValueError(f"Index {index} is out of bounds for array '{array_name}'")
                return self.variables[array_name][index]
            
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
