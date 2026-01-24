from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.get_json() or {}

    a = float(data.get('a', 0))
    b = float(data.get('b', 0))
    op = data.get('op')

    if op == 'add':
        return jsonify(result=a+b)
    if op == 'subtract':
        return jsonify(result=a-b)
    if op == 'multiply':
        return jsonify(result=a*b)
    if op == 'divide':
        if b == 0:
            return jsonify(error="Division by zero"), 400
        return jsonify(result=a/b)

    return jsonify(error="Invalid operation"), 400


@app.route('/api/health', methods=['GET'])
def health():
    return jsonify(status="ok")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)