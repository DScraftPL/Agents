from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import sqlite3
import json

app = Flask(__name__)
CORS(app, origins='http://localhost:3000')

DATABASE = 'messages.db'

def create_connection():
    conn = sqlite3.connect(DATABASE)
    return conn

def create_table():
    conn = create_connection()
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_input TEXT NOT NULL,
                    ai_response TEXT NOT NULL,
                    json_data TEXT
                )''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/send_message', methods=['POST'])
def send_message():
    user_input = request.json.get('message')
    if not user_input:
        return jsonify({'error': 'No message provided'}), 400

    response_text = "AI response placeholder"  # Placeholder AI response
    
    # Scan for JSON data in AI's message
    json_data = None
    try:
        response_data = json.loads(response_text)
        json_data = json.dumps(response_data)
    except json.JSONDecodeError:
        pass

    # Store message and JSON data in DB
    store_message_in_db(user_input, response_text, json_data)

    return jsonify({'response': response_text})


def store_message_in_db(user_input, ai_response, json_data=None):
    conn = create_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO messages (user_input, ai_response, json_data) VALUES (?, ?, ?)", 
        (user_input, ai_response, json_data)
    )
    conn.commit()
    conn.close()

if __name__ == '__main__':
    create_table()
    app.run(debug=True, host='0.0.0.0', port=5000)
