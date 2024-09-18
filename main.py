from flask import Flask, render_template, request, jsonify
from pseudocode_interpreter import PseudocodeInterpreter

app = Flask(__name__)
interpreter = PseudocodeInterpreter()

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
    PRINT x is greater than y
ELSE
    PRINT y is greater than or equal to x
ENDIF

PRINT The value of x is
PRINT x

count = 0
WHILE count < 5
    PRINT Current count:
    PRINT count
    count = count + 1
ENDWHILE

PRINT Counting from 1 to 3:
FOR i FROM 1 TO 3 DO PRINT i

result = (x + y) * 2
PRINT The result of (x + y) * 2 is:
PRINT result

# Function definition
FUNCTION add(a, b)
    PRINT Adding two numbers:
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

PRINT Array elements:
FOR i FROM 0 TO 4 DO PRINT numbers[i]

# Function to calculate sum of array elements
FUNCTION array_sum(arr, size)
    sum = 0
    FOR i FROM 0 TO size - 1 DO
        sum = sum + arr[i]
    ENDFOR
    PRINT Sum of array elements:
    PRINT sum
ENDFUNCTION

CALL array_sum(numbers, 5)
"""
    return jsonify({'example': example_code})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
