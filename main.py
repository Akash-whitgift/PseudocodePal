FOR i FROM 1 TO 3 DO
PRINT "Outer loop: "
PRINT i
FOR j FROM 1 TO 2 DO
PRINT "Inner loop: "
PRINT j
ENDFOR
ENDFORfrom flask import Flask, render_template, request, jsonify
from pseudocode_interpreter import PseudocodeInterpreter
import json
import os

app = Flask(__name__)
interpreter = PseudocodeInterpreter()

if not os.path.exists('snippets'):
    os.makedirs('snippets')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/interpret', methods=['POST'])
def interpret():
    pseudocode = request.json.get('pseudocode', '')
    try:
        result = interpreter.interpret(pseudocode)
        return jsonify({'result': result, 'error': None})
    except Exception as e:
        return jsonify({'result': None, 'error': str(e)})

@app.route('/start_execution', methods=['POST'])
def start_execution():
    pseudocode = request.json.get('pseudocode', '')
    interpreter.interpret(pseudocode)
    interpreter.reset_execution()
    return jsonify({'message': 'Execution started'})

@app.route('/next_step', methods=['GET'])
def next_step():
    step = interpreter.get_next_step()
    if step:
        return jsonify(step)
    else:
        return jsonify({'message': 'Execution completed'})

@app.route('/example')
def example():
    example_code = """
# This is a comment
x = 10
y = 5

IF x > y THEN
    PRINT "x is greater than y"
ELSE
    PRINT "y is greater than or equal to x"
ENDIF

PRINT "The value of x is"
PRINT x

count = 0
WHILE count < 5
    PRINT "Current count:"
    PRINT count
    count = count + 1
ENDWHILE

PRINT "Counting from 1 to 3:"
FOR i FROM 1 TO 3 DO
    PRINT i
ENDFOR

result = (x + y) * 2
PRINT "The result of (x + y) * 2 is:"
PRINT result

# Function definition
FUNCTION add(a, b)
    PRINT "Adding two numbers:"
    PRINT a + b
ENDFUNCTION

# Function call
CALL add(5, 7)

# Array declaration and usage
ARRAY numbers[5]
numbers[0] = 10
numbers[1] = 20
numbers[2] = 30
numbers[3] = 40
numbers[4] = 50

PRINT "Array elements:"
FOR i FROM 0 TO 4 DO
    PRINT numbers[i]
ENDFOR

# Function to calculate sum of array elements
FUNCTION array_sum(arr, size)
    sum = 0
    FOR i FROM 0 TO size - 1 DO
        sum = sum + arr[i]
    ENDFOR
    PRINT "Sum of array elements:"
    PRINT sum
ENDFUNCTION

CALL array_sum(numbers, 5)
"""
    return jsonify({'example': example_code})

@app.route('/save_snippet', methods=['POST'])
def save_snippet():
    data = request.json
    snippet_name = data.get('name')
    snippet_code = data.get('code')
    
    if not snippet_name or not snippet_code:
        return jsonify({'error': 'Name and code are required'}), 400
    
    filename = f"snippets/{snippet_name}.json"
    with open(filename, 'w') as f:
        json.dump({'name': snippet_name, 'code': snippet_code}, f)
    
    return jsonify({'message': 'Snippet saved successfully'})

@app.route('/load_snippet/<snippet_name>', methods=['GET'])
def load_snippet(snippet_name):
    filename = f"snippets/{snippet_name}.json"
    try:
        with open(filename, 'r') as f:
            snippet = json.load(f)
        return jsonify(snippet)
    except FileNotFoundError:
        return jsonify({'error': 'Snippet not found'}), 404

@app.route('/list_snippets', methods=['GET'])
def list_snippets():
    snippets = [f.split('.')[0] for f in os.listdir('snippets') if f.endswith('.json')]
    return jsonify({'snippets': snippets})

@app.route('/test_consistency', methods=['POST'])
def test_consistency():
    pseudocode = request.json.get('pseudocode', '')
    
    # Full interpretation
    full_result = interpreter.interpret(pseudocode)
    full_output = interpreter.output
    full_variables = interpreter.get_all_variables()
    
    # Step-by-step execution
    interpreter.reset_execution()
    interpreter.interpret(pseudocode)
    step_result = []
    step_output = []
    step_variables = {}
    
    while True:
        step = interpreter.get_next_step()
        if step is None:
            break
        if step['output'] is not None:
            step_result.append(step['output'])
        step_output.append(step['output'])
        step_variables = step['variables']
    
    # Compare results
    consistency = {
        'output_match': full_output == step_output,
        'variable_match': full_variables == step_variables,
        'full_output': full_output,
        'step_output': step_output,
        'full_variables': full_variables,
        'step_variables': step_variables
    }
    
    return jsonify({
        'full_result': full_result,
        'step_result': '\n'.join(step_result),
        'consistency': consistency
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
