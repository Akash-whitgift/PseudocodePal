from flask import Flask, render_template, request, jsonify
from pseudocode_interpreter import PseudocodeInterpreter
import json
import os
import traceback
import logging
import sys
import difflib

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', stream=sys.stdout)
logger = logging.getLogger(__name__)

app = Flask(__name__)
interpreter = PseudocodeInterpreter()

if not os.path.exists('snippets'):
    os.makedirs('snippets')

@app.route('/')
def index():
    logger.debug("Serving index page")
    return render_template('index.html')

@app.route('/interpret', methods=['POST'])
def interpret():
    pseudocode = request.json.get('pseudocode', '')
    try:
        logger.debug(f"Interpreting pseudocode: {pseudocode[:50]}...")
        result = interpreter.interpret(pseudocode)
        return jsonify({'result': result, 'error': None})
    except Exception as e:
        logger.error(f"Error interpreting pseudocode: {str(e)}")
        return jsonify({'result': None, 'error': str(e)})

@app.route('/start_execution', methods=['POST'])
def start_execution():
    pseudocode = request.json.get('pseudocode', '')
    logger.debug(f"Starting execution of pseudocode: {pseudocode[:50]}...")
    interpreter.interpret(pseudocode)
    interpreter.reset_execution()
    return jsonify({'message': 'Execution started'})

@app.route('/next_step', methods=['GET'])
def next_step():
    logger.debug("Getting next step")
    step = interpreter.get_next_step()
    if step:
        return jsonify(step)
    else:
        return jsonify({'message': 'Execution completed'})

@app.route('/example')
def example():
    logger.debug("Serving example code")
    try:
        example_code = """
# This is a comment
DECLARE x : INTEGER
DECLARE y : INTEGER
x ← 10
y ← 5

IF x > y THEN
    OUTPUT "x is greater than y"
ELSE
    OUTPUT "y is greater than or equal to x"
ENDIF

OUTPUT "The value of x is"
OUTPUT x

DECLARE count : INTEGER
count ← 0
WHILE count < 5 DO
    OUTPUT "Current count:"
    OUTPUT count
    count ← count + 1
ENDWHILE

OUTPUT "Counting from 1 to 3:"
FOR i ← 1 TO 3
    OUTPUT i
NEXT i

DECLARE result : INTEGER
result ← (x + y) * 2
OUTPUT "The result of (x + y) * 2 is:"
OUTPUT result

# Procedure definition
PROCEDURE add(a, b)
    OUTPUT "Adding two numbers:"
    OUTPUT a + b
ENDPROCEDURE

# Procedure call
add(5, 7)

# Array declaration and initialization
ARRAY numbers[1:5] OF INTEGER
numbers[1] ← 10
numbers[2] ← 20
numbers[3] ← 30
numbers[4] ← 40
numbers[5] ← 50

OUTPUT "Array elements:"
FOR i ← 1 TO 5
    OUTPUT numbers[i]
NEXT i

# Get array length
OUTPUT "Array length:"
OUTPUT 5  # Hardcoded as IGCSE doesn't have a built-in length function

# Append to array (not supported in IGCSE, but we can simulate by reassigning)
DECLARE temp : INTEGER
temp ← numbers[5]
numbers[5] ← 60
OUTPUT "Array after append:"
FOR i ← 1 TO 5
    OUTPUT numbers[i]
NEXT i

# Remove from array (not supported in IGCSE, but we can simulate by shifting elements)
FOR i ← 2 TO 4
    numbers[i] ← numbers[i + 1]
NEXT i
numbers[5] ← temp
OUTPUT "Array after removing index 2:"
FOR i ← 1 TO 5
    OUTPUT numbers[i]
NEXT i

# Procedure to calculate sum of array elements
PROCEDURE array_sum(arr)
    DECLARE sum : INTEGER
    sum ← 0
    FOR i ← 1 TO 5
        sum ← sum + arr[i]
    NEXT i
    OUTPUT "Sum of array elements:"
    OUTPUT sum
ENDPROCEDURE

array_sum(numbers)

# Demonstrate INPUT statement
INPUT name
OUTPUT "Hello, " + name

# Demonstrate BOOLEAN type and logical operators
DECLARE is_true : BOOLEAN
DECLARE is_false : BOOLEAN
is_true ← TRUE
is_false ← FALSE
IF is_true AND NOT is_false THEN
    OUTPUT "Boolean logic works!"
ENDIF

# Demonstrate REAL type and relational operators
DECLARE pi : REAL
pi ← 3.14159
IF pi > 3 AND pi < 4 THEN
    OUTPUT "pi is between 3 and 4"
ENDIF

# Demonstrate MOD and ^ operators
DECLARE mod_result : INTEGER
DECLARE power_result : INTEGER
mod_result ← 17 MOD 5
power_result ← 2 ^ 3
OUTPUT "17 MOD 5 ="
OUTPUT mod_result
OUTPUT "2 ^ 3 ="
OUTPUT power_result
"""
        # Ensure the example code is properly escaped
        example_code = json.dumps(example_code)
        return jsonify({'example': json.loads(example_code)})
    except Exception as e:
        logger.error(f"Error in /example route: {str(e)}")
        return jsonify({'error': 'Failed to load example code'}), 500

@app.route('/save_snippet', methods=['POST'])
def save_snippet():
    data = request.json
    snippet_name = data.get('name')
    snippet_code = data.get('code')
    
    if not snippet_name or not snippet_code:
        logger.warning("Attempt to save snippet with missing name or code")
        return jsonify({'error': 'Name and code are required'}), 400
    
    filename = f"snippets/{snippet_name}.json"
    with open(filename, 'w') as f:
        json.dump({'name': snippet_name, 'code': snippet_code}, f)
    
    logger.info(f"Snippet '{snippet_name}' saved successfully")
    return jsonify({'message': 'Snippet saved successfully'})

@app.route('/load_snippet/<snippet_name>', methods=['GET'])
def load_snippet(snippet_name):
    filename = f"snippets/{snippet_name}.json"
    try:
        with open(filename, 'r') as f:
            snippet = json.load(f)
        logger.info(f"Snippet '{snippet_name}' loaded successfully")
        return jsonify(snippet)
    except FileNotFoundError:
        logger.warning(f"Attempt to load non-existent snippet '{snippet_name}'")
        return jsonify({'error': 'Snippet not found'}), 404

@app.route('/list_snippets', methods=['GET'])
def list_snippets():
    snippets = [f.split('.')[0] for f in os.listdir('snippets') if f.endswith('.json')]
    logger.debug(f"Listed snippets: {snippets}")
    return jsonify({'snippets': snippets})

@app.route('/test_consistency', methods=['POST'])
def test_consistency():
    pseudocode = request.json.get('pseudocode', '')
    logger.debug(f"Testing consistency for pseudocode: {pseudocode[:50]}...")
    
    try:
        # Full interpretation
        interpreter.reset_execution()
        full_result = interpreter.interpret(pseudocode)
        full_output = interpreter.output
        full_variables = interpreter.get_all_variables()
        full_error = interpreter.error
        
        # Step-by-step execution
        interpreter.reset_execution()
        interpreter.interpret(pseudocode)
        step_result = []
        step_output = []
        step_variables = []
        step_error = None
        
        while True:
            step = interpreter.get_next_step()
            if step is None:
                break
            if step['output'] is not None:
                step_result.append(step['output'])
            step_output.append(step['output'])
            step_variables.append(step['variables'])
            if step['error'] is not None:
                step_error = step['error']
                break
        
        # Compare results
        output_diff = list(difflib.unified_diff(full_output, step_output, lineterm=''))
        
        variable_diffs = []
        for i, step_vars in enumerate(step_variables):
            if i == 0:
                full_vars = full_variables
            else:
                full_vars = step_variables[i-1]
            
            var_diff = {}
            for var, value in step_vars.items():
                if var not in full_vars or full_vars[var] != value:
                    var_diff[var] = {'step': value, 'full': full_vars.get(var, 'Not present')}
            
            if var_diff:
                variable_diffs.append({'step': i+1, 'differences': var_diff})
        
        consistency = {
            'output_match': full_output == step_output,
            'variable_match': len(variable_diffs) == 0,
            'error_match': full_error == step_error,
            'output_diff': output_diff,
            'variable_diffs': variable_diffs,
            'full_error': full_error,
            'step_error': step_error
        }
        
        logger.info("Consistency test completed")
        return jsonify({
            'full_result': full_result,
            'step_result': '\n'.join(step_result) if step_result else '',
            'consistency': consistency
        })
    except Exception as e:
        error_traceback = traceback.format_exc()
        logger.error(f"Error during consistency test: {str(e)}")
        return jsonify({
            'error': str(e),
            'traceback': error_traceback
        }), 500

if __name__ == '__main__':
    logger.info("Starting Flask application")
    app.run(host='0.0.0.0', port=5000, debug=True)