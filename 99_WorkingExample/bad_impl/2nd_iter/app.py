from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import openai

from graph import graph

app = Flask(__name__)
CORS(app, origins='http://localhost:3000')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/send_message', methods=['POST'])
def send_message():
    user_input = request.json.get('message')
    if not user_input:
        return jsonify({'error': 'No message provided'}), 400
    response_text = ai_interaction(user_input)
    return jsonify({'response': response_text})

def ai_interaction(message):
    ai_response = graph.invoke({"messages": message}, config = {"configurable": {"thread_id": "user1"}})

    return ai_response["messages"][-1].content

if __name__ == '__main__':
    app.run(debug=True, port=5000)