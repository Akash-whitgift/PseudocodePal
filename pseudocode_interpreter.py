import re

class Scope:
    def __init__(self, parent=None):
        self.variables = {}
        self.parent = parent

    def get(self, name):
        if name in self.variables:
            return self.variables[name]
        elif self.parent:
            return self.parent.get(name)
        raise ValueError(f"Variable '{name}' is not defined")

    def set(self, name, value):
        self.variables[name] = value

class PseudocodeInterpreter:
    def __init__(self):
        self.global_scope = Scope()
        self.scope_stack = [self.global_scope]
        self.functions = {}
        self.execution_steps = []
        self.current_step = 0
        self.output = []
        self.loop_stack = []
        self.current_line = 0

    @property
    def current_scope(self):
        return self.scope_stack[-1]

    def push_scope(self):
        self.scope_stack.append(Scope(self.current_scope))

    def pop_scope(self):
        if len(self.scope_stack) > 1:
            self.scope_stack.pop()

    def interpret(self, pseudocode):
        self.execution_steps = []
        self.current_step = 0
        self.output = []
        self.loop_stack = []
        self.scope_stack = [self.global_scope]
        self.current_line = 0
        lines = pseudocode.split('\n')
        i = 0
        while i < len(lines):
            self.current_line = i + 1
            line = lines[i].strip()
            if line and not line.startswith('#'):  # Ignore empty lines and comments
                try:
                    result, i = self.execute_line(lines, i)
                    if result is not None:
                        self.output.append(result)
                except Exception as e:
                    error_msg = self.format_error(str(e), i)
                    self.output.append(error_msg)
                    self.execution_steps.append({
                        'line': line,
                        'variables': self.get_all_variables(),
                        'output': error_msg
                    })
            i += 1
        return '\n'.join(self.output)

    def execute_line(self, lines, i):
        line = lines[i].strip()
        self.execution_steps.append({
            'line': line,
            'variables': self.get_all_variables(),
            'output': None
        })
        
        if line.startswith('PRINT'):
            result = self.print_statement(line)
            self.execution_steps[-1]['output'] = result
            return result, i
        elif '=' in line:
            self.assignment(line)
            return None, i
        elif line.startswith('IF'):
            return self.if_statement(lines, i)
        elif line.startswith('FOR'):
            return self.for_loop(lines, i)
        elif line.startswith('WHILE'):
            return self.while_loop(lines, i)
        elif line.startswith('FUNCTION'):
            return self.function_definition(lines, i)
        elif line.startswith('CALL'):
            result = self.function_call(line)
            self.execution_steps[-1]['output'] = result
            return result, i
        elif line.startswith('ARRAY'):
            self.array_declaration(line)
            return None, i
        elif line in ['ENDFOR', 'ENDWHILE', 'ENDIF', 'ENDFUNCTION']:
            if self.loop_stack and self.loop_stack[-1][0] == line[3:]:
                self.loop_stack.pop()
            self.pop_scope()
            return None, i
        else:
            raise ValueError(f"Unsupported command: {line}")

    def print_statement(self, line):
        match = re.match(r'PRINT\s+(.+)', line)
        if match:
            content = match.group(1)
            if content.startswith('"') and content.endswith('"'):
                return content[1:-1]  # Remove quotes for string literals
            else:
                return str(self.evaluate_expression(content))
        raise ValueError(f"Invalid PRINT statement: {line}")

    def assignment(self, line):
        variable, expression = map(str.strip, line.split('='))
        if '[' in variable:  # Array assignment
            array_name, index = re.match(r'(\w+)\[(.+)\]', variable).groups()
            index = int(self.evaluate_expression(index))
            array = self.get_variable(array_name)
            if not isinstance(array, list):
                raise ValueError(f"'{array_name}' is not an array")
            if index < 0 or index >= len(array):
                raise ValueError(f"Index {index} is out of bounds for array '{array_name}'")
            array[index] = self.evaluate_expression(expression)
        else:
            self.current_scope.set(variable, self.evaluate_expression(expression))

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
        
        self.push_scope()
        
        if self.evaluate_expression(condition):
            result = self.interpret('\n'.join(true_block))
        else:
            result = self.interpret('\n'.join(false_block))
        
        self.pop_scope()
        return result, i - 1

    def for_loop(self, lines, i):
        match = re.match(r'FOR\s+(\w+)\s+FROM\s+(.+)\s+TO\s+(.+)\s+DO', lines[i])
        if not match:
            raise ValueError(f"Invalid FOR loop on line {i + 1}: {lines[i]}")
        
        var, start, end = match.groups()
        i += 1
        loop_block = []
        loop_depth = 1
        
        while i < len(lines):
            if lines[i].strip().startswith('FOR'):
                loop_depth += 1
            elif lines[i].strip() == 'ENDFOR':
                loop_depth -= 1
                if loop_depth == 0:
                    i += 1
                    break
            loop_block.append(lines[i])
            i += 1
        
        if loop_depth > 0:
            raise ValueError(f"FOR loop not properly closed with ENDFOR, starting from line {i + 1}")
        
        start_value = int(self.evaluate_expression(start))
        end_value = int(self.evaluate_expression(end))
        output = []
        
        for j in range(start_value, end_value + 1):
            self.push_scope()
            self.current_scope.set(var, j)
            self.loop_stack.append(('FOR', var, j))
            result = self.interpret('\n'.join(loop_block))
            if result:
                output.append(result)
            self.loop_stack.pop()
            self.pop_scope()
        
        return '\n'.join(output), i - 1

    def while_loop(self, lines, i):
        condition_match = re.match(r'WHILE\s+(.+)', lines[i])
        if not condition_match:
            raise ValueError(f"Invalid WHILE statement on line {i + 1}: {lines[i]}")
        
        condition = condition_match.group(1)
        i += 1
        loop_block = []
        loop_depth = 1
        
        while i < len(lines):
            if lines[i].strip().startswith('WHILE'):
                loop_depth += 1
            elif lines[i].strip() == 'ENDWHILE':
                loop_depth -= 1
                if loop_depth == 0:
                    i += 1
                    break
            loop_block.append(lines[i])
            i += 1
        
        if loop_depth > 0:
            raise ValueError(f"WHILE loop not properly closed with ENDWHILE, starting from line {i + 1}")
        
        output = []
        iteration = 0
        while self.evaluate_expression(condition):
            self.push_scope()
            self.loop_stack.append(('WHILE', None, iteration))
            result = self.interpret('\n'.join(loop_block))
            if result:
                output.append(result)
            self.loop_stack.pop()
            self.pop_scope()
            iteration += 1
        
        return '\n'.join(output), i - 1

    def function_definition(self, lines, i):
        match = re.match(r'FUNCTION\s+(\w+)\s*\((.*?)\)', lines[i])
        if not match:
            raise ValueError(f"Invalid function definition on line {i + 1}: {lines[i]}")
        
        func_name, params = match.groups()
        params = [p.strip() for p in params.split(',') if p.strip()]
        i += 1
        func_body = []
        
        while i < len(lines):
            if lines[i].strip() == 'ENDFUNCTION':
                i += 1
                break
            func_body.append(lines[i])
            i += 1
        
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
        
        self.push_scope()
        for param, arg in zip(func['params'], args):
            self.current_scope.set(param, arg)
        
        self.loop_stack.append(('FUNCTION', func_name))
        result = self.interpret('\n'.join(func['body']))
        self.loop_stack.pop()
        self.pop_scope()
        
        return result

    def array_declaration(self, line):
        match = re.match(r'ARRAY\s+(\w+)\s*\[(\d+)\]', line)
        if not match:
            raise ValueError(f"Invalid array declaration: {line}")
        
        array_name, size = match.groups()
        self.current_scope.set(array_name, [0] * int(size))

    def evaluate_expression(self, expression):
        try:
            if expression.startswith('"') and expression.endswith('"'):
                return expression[1:-1]
            
            array_access = re.match(r'(\w+)\[(.+)\]', expression)
            if array_access:
                array_name, index = array_access.groups()
                index = int(self.evaluate_expression(index))
                array = self.get_variable(array_name)
                if not isinstance(array, list):
                    raise ValueError(f"'{array_name}' is not an array")
                if index < 0 or index >= len(array):
                    raise ValueError(f"Index {index} is out of bounds for array '{array_name}'")
                return array[index]
            
            for var in re.findall(r'\b[a-zA-Z_]\w*\b', expression):
                if var in self.get_all_variables():
                    expression = re.sub(r'\b' + var + r'\b', str(self.get_variable(var)), expression)
            
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
            loop_info = self.get_loop_info()
            raise ValueError(f"Invalid expression: {expression}. Error: {str(e)}. {loop_info}")

    def get_next_step(self):
        if self.current_step < len(self.execution_steps):
            step = self.execution_steps[self.current_step]
            self.current_step += 1
            return step
        return None

    def reset_execution(self):
        self.current_step = 0
        self.global_scope = Scope()
        self.scope_stack = [self.global_scope]
        self.functions = {}
        self.output = []
        self.loop_stack = []
        self.current_line = 0

    def get_all_variables(self):
        variables = {}
        for scope in reversed(self.scope_stack):
            variables.update(scope.variables)
        return variables

    def get_variable(self, name):
        for scope in reversed(self.scope_stack):
            if name in scope.variables:
                return scope.variables[name]
        raise ValueError(f"Variable '{name}' is not defined")

    def get_loop_info(self):
        if self.loop_stack:
            loop_type, var, iteration = self.loop_stack[-1]
            return f"In {loop_type} loop, variable '{var}', iteration {iteration}"
        return "Not currently in a loop"

    def format_error(self, error_message, line_number):
        loop_info = self.get_loop_info()
        variables = ", ".join([f"{k}={v}" for k, v in self.get_all_variables().items()])
        return f"Error on line {line_number + 1}: {error_message}. {loop_info}. Variables: {variables}"
