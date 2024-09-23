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

    def set(self, name, value, type_):
        self.variables[name] = {'value': value, 'type': type_}

class PseudocodeInterpreter:
    def __init__(self):
        self.global_scope = Scope()
        self.scope_stack = [self.global_scope]
        self.procedures = {}
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
                    error_msg = self.format_error(str(e), i, line)
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
        
        if line.startswith('OUTPUT'):
            result = self.output_statement(line)
            self.execution_steps[-1]['output'] = result
            return result, i
        elif line.startswith('INPUT'):
            self.input_statement(line)
            return None, i
        elif '←' in line:
            self.assignment(line)
            return None, i
        elif line.startswith('IF'):
            return self.if_statement(lines, i)
        elif line.startswith('FOR'):
            return self.for_loop(lines, i)
        elif line.startswith('WHILE'):
            return self.while_loop(lines, i)
        elif line.startswith('PROCEDURE'):
            return self.procedure_definition(lines, i)
        elif line.startswith('DECLARE'):
            self.variable_declaration(line)
            return None, i
        elif line.startswith('ARRAY'):
            self.array_declaration(line)
            return None, i
        elif line in ['NEXT', 'ENDWHILE', 'ENDIF', 'ENDPROCEDURE']:
            if self.loop_stack and self.loop_stack[-1][0] == line[3:]:
                self.loop_stack.pop()
            self.pop_scope()
            return None, i
        else:
            # Check if it's a procedure call
            procedure_match = re.match(r'(\w+)\s*\((.*?)\)', line)
            if procedure_match:
                result = self.procedure_call(line)
                self.execution_steps[-1]['output'] = result
                return result, i
            raise ValueError(f"Unsupported command: {line}")

    def output_statement(self, line):
        match = re.match(r'OUTPUT\s+(.+)', line)
        if match:
            content = match.group(1)
            if content.startswith('"') and content.endswith('"'):
                return content[1:-1]  # Remove quotes for string literals
            else:
                return str(self.evaluate_expression(content))
        raise ValueError(f"Invalid OUTPUT statement: {line}")

    def input_statement(self, line):
        match = re.match(r'INPUT\s+(\w+)', line)
        if match:
            variable = match.group(1)
            value = input(f"Enter value for {variable}: ")
            self.current_scope.set(variable, value, 'STRING')
        else:
            raise ValueError(f"Invalid INPUT statement: {line}")

    def assignment(self, line):
        variable, expression = map(str.strip, line.split('←'))
        if '[' in variable:  # Array assignment
            array_name, index = re.match(r'(\w+)\[(.+)\]', variable).groups()
            index = int(self.evaluate_expression(index))
            array = self.get_variable(array_name)
            if not isinstance(array['value'], list):
                raise ValueError(f"'{array_name}' is not an array")
            if index < 0 or index >= len(array['value']):
                raise ValueError(f"Index {index} is out of bounds for array '{array_name}'")
            value = self.evaluate_expression(expression)
            array['value'][index] = value
        else:
            value = self.evaluate_expression(expression)
            var_type = self.infer_type(value)
            self.current_scope.set(variable, value, var_type)

    def if_statement(self, lines, i):
        condition_match = re.match(r'IF\s+(.+)\s+THEN', lines[i])
        if not condition_match:
            raise ValueError(f"Invalid IF statement on line {self.current_line}: {lines[i]}")
        
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
            raise ValueError(f"IF statement not properly closed with ENDIF, starting from line {self.current_line}")
        
        self.push_scope()
        
        if self.evaluate_expression(condition):
            result = self.interpret('\n'.join(true_block))
        else:
            result = self.interpret('\n'.join(false_block))
        
        self.pop_scope()
        return result, i - 1

    def for_loop(self, lines, i):
        match = re.match(r'FOR\s+(\w+)\s+←\s+(.+)\s+TO\s+(.+)', lines[i])
        if not match:
            raise ValueError(f"Invalid FOR loop on line {self.current_line}: {lines[i]}")
        
        var, start, end = match.groups()
        i += 1
        loop_block = []
        loop_depth = 1
        
        while i < len(lines):
            if lines[i].strip().startswith('FOR'):
                loop_depth += 1
            elif lines[i].strip().startswith('NEXT'):
                loop_depth -= 1
                if loop_depth == 0:
                    if not lines[i].strip().endswith(var):
                        raise ValueError(f"FOR loop not properly closed with NEXT {var}, on line {i + 1}")
                    i += 1
                    break
            loop_block.append(lines[i])
            i += 1
        
        if loop_depth > 0:
            raise ValueError(f"FOR loop not properly closed with NEXT {var}, starting from line {self.current_line}")
        
        start_value = int(self.evaluate_expression(start))
        end_value = int(self.evaluate_expression(end))
        output = []
        
        for j in range(start_value, end_value + 1):
            self.push_scope()
            self.current_scope.set(var, j, 'INTEGER')
            self.loop_stack.append(('FOR', var, j))
            result = self.interpret('\n'.join(loop_block))
            if result:
                output.append(result)
            self.loop_stack.pop()
            self.pop_scope()
        
        return '\n'.join(output), i - 1

    def while_loop(self, lines, i):
        condition_match = re.match(r'WHILE\s+(.+)\s+DO', lines[i])
        if not condition_match:
            raise ValueError(f"Invalid WHILE statement on line {self.current_line}: {lines[i]}")
        
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
            raise ValueError(f"WHILE loop not properly closed with ENDWHILE, starting from line {self.current_line}")
        
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

    def procedure_definition(self, lines, i):
        match = re.match(r'PROCEDURE\s+(\w+)\s*\((.*?)\)', lines[i])
        if not match:
            raise ValueError(f"Invalid procedure definition on line {self.current_line}: {lines[i]}")
        
        proc_name, params = match.groups()
        params = [p.strip() for p in params.split(',') if p.strip()]
        i += 1
        proc_body = []
        
        while i < len(lines):
            if lines[i].strip() == 'ENDPROCEDURE':
                i += 1
                break
            proc_body.append(lines[i])
            i += 1
        
        if i == len(lines):
            raise ValueError(f"Procedure '{proc_name}' not properly closed with ENDPROCEDURE")
        
        self.procedures[proc_name] = {
            'params': params,
            'body': proc_body
        }
        
        return None, i - 1

    def procedure_call(self, line):
        match = re.match(r'(\w+)\s*\((.*?)\)', line)
        if not match:
            raise ValueError(f"Invalid procedure call: {line}")
        
        proc_name, args = match.groups()
        args = [self.evaluate_expression(arg.strip()) for arg in args.split(',') if arg.strip()]
        
        if proc_name not in self.procedures:
            raise ValueError(f"Procedure '{proc_name}' is not defined")
        
        proc = self.procedures[proc_name]
        if len(args) != len(proc['params']):
            raise ValueError(f"Procedure '{proc_name}' expects {len(proc['params'])} arguments, but {len(args)} were given")
        
        self.push_scope()
        for param, arg in zip(proc['params'], args):
            self.current_scope.set(param, arg, self.infer_type(arg))
        
        self.loop_stack.append(('PROCEDURE', proc_name, 0))
        result = self.interpret('\n'.join(proc['body']))
        self.loop_stack.pop()
        self.pop_scope()
        
        return result

    def variable_declaration(self, line):
        match = re.match(r'DECLARE\s+(\w+)\s*:\s*(\w+)', line)
        if not match:
            raise ValueError(f"Invalid variable declaration: {line}")
        
        var_name, var_type = match.groups()
        if var_type not in ['INTEGER', 'REAL', 'CHAR', 'STRING', 'BOOLEAN']:
            raise ValueError(f"Invalid variable type: {var_type}")
        
        self.current_scope.set(var_name, None, var_type)

    def array_declaration(self, line):
        match = re.match(r'ARRAY\s+(\w+)\[(\d+):(\d+)\]\s+OF\s+(\w+)', line)
        if not match:
            raise ValueError(f"Invalid array declaration: {line}")
        
        array_name, lower, upper, array_type = match.groups()
        lower = int(lower)
        upper = int(upper)
        
        if array_type not in ['INTEGER', 'REAL', 'CHAR', 'STRING', 'BOOLEAN']:
            raise ValueError(f"Invalid array type: {array_type}")
        
        size = upper - lower + 1
        self.current_scope.set(array_name, [None] * size, f'ARRAY[{lower}:{upper}] OF {array_type}')

    def evaluate_expression(self, expression):
        try:
            if expression.startswith('"') and expression.endswith('"'):
                return expression[1:-1]
            
            array_access = re.match(r'(\w+)\[(.+)\]', expression)
            if array_access:
                array_name, index = array_access.groups()
                index = int(self.evaluate_expression(index))
                array = self.get_variable(array_name)
                if not isinstance(array['value'], list):
                    raise ValueError(f"'{array_name}' is not an array")
                if index < 0 or index >= len(array['value']):
                    raise ValueError(f"Index {index} is out of bounds for array '{array_name}'")
                return array['value'][index]
            
            for var in re.findall(r'\b[a-zA-Z_]\w*\b', expression):
                if var in self.get_all_variables():
                    var_value = self.get_variable(var)['value']
                    expression = re.sub(r'\b' + var + r'\b', str(var_value), expression)
            
            # Replace ≠ with != for Python evaluation
            expression = expression.replace('≠', '!=')
            # Replace ^ with ** for exponentiation
            expression = expression.replace('^', '**')
            
            return eval(expression, {"__builtins__": None}, {
                "+": lambda x, y: x + y,
                "-": lambda x, y: x - y,
                "*": lambda x, y: x * y,
                "/": lambda x, y: x / y,
                "MOD": lambda x, y: x % y,
                "<": lambda x, y: x < y,
                ">": lambda x, y: x > y,
                "<=": lambda x, y: x <= y,
                ">=": lambda x, y: x >= y,
                "=": lambda x, y: x == y,
                "!=": lambda x, y: x != y,
                "AND": lambda x, y: x and y,
                "OR": lambda x, y: x or y,
                "NOT": lambda x: not x,
            })
        except Exception as e:
            loop_info = self.get_loop_info()
            raise ValueError(f"Invalid expression: {expression}. Error: {str(e)}. {loop_info}")

    def infer_type(self, value):
        if isinstance(value, bool):
            return 'BOOLEAN'
        elif isinstance(value, int):
            return 'INTEGER'
        elif isinstance(value, float):
            return 'REAL'
        elif isinstance(value, str):
            if len(value) == 1:
                return 'CHAR'
            else:
                return 'STRING'
        else:
            return 'UNKNOWN'

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
        self.procedures = {}
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
            return f"In {loop_type} loop" + (f", variable '{var}'" if var else "") + f", iteration {iteration}"
        return "Not currently in a loop"

    def format_error(self, error_message, line_number, line_content):
        loop_info = self.get_loop_info()
        variables = ", ".join([f"{k}={v['value']} ({v['type']})" for k, v in self.get_all_variables().items()])
        return f"Error on line {line_number + 1}: {error_message}\nLine content: {line_content}\n{loop_info}\nVariables: {variables}"
