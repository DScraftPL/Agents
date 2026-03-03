from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/ai', methods=['POST'])
def ai_interface():
    user_query = request.json.get('query')
    # Here you would integrate your AI model, for this example we mock a response
    ai_response = f"AI: This is a simulated response to '{user_query}'"
    return jsonify({'response': ai_response})

if __name__ == '__main__':
    app.run(debug=True)
