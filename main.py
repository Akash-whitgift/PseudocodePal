from flask import Flask, render_template, request, jsonify
from pseudocode_interpreter import PseudocodeInterpreter

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/interpret', methods=['POST'])
def interpret():
    pseudocode = request.json.get('pseudocode', '')
    interpreter = PseudocodeInterpreter()
    try:
        result = interpreter.interpret(pseudocode)
        return jsonify({'result': result, 'error': None})
    except Exception as e:
        return jsonify({'result': None, 'error': str(e)})

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
"""
    return jsonify({'example': example_code})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
