from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import sqlite3

from graph import graph

app = Flask(__name__)
CORS(app, origins='http://localhost:3000')

DATABASE = 'recipes.db'

def create_connection():
    conn = sqlite3.connect(DATABASE)
    return conn

def create_table():
    conn = create_connection()
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS recipes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    dish_name TEXT NOT NULL,
                    ingredients TEXT NOT NULL,
                    recipe TEXT NOT NULL
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
    response_text = ai_interaction(user_input)
    return jsonify({'response': response_text})

def ai_interaction(message):
    ai_response = graph.invoke({"messages": message}, config = {"configurable": {"thread_id": "user1"}})

    return ai_response["messages"][-1].content


def store_recipe_in_db(dish_name, recipe_text):
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO recipes (dish_name, ingredients, recipe) VALUES (?, ?, ?)", (dish_name, '', recipe_text))
    conn.commit()
    conn.close()

if __name__ == '__main__':
    create_table()
    app.run(debug=True, host='0.0.0.0', port=5000)