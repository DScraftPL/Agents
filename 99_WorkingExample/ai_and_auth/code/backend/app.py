from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import bcrypt
import jwt
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)
SECRET_KEY = 'your_secret_key'

# Initialize database
conn = sqlite3.connect('recipes.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS recipes (id INTEGER PRIMARY KEY, user_id INTEGER, title TEXT, content TEXT)''')
conn.commit()

def generate_jwt_token(user_id):
    return jwt.encode({'user_id': user_id, 'exp': datetime.utcnow() + timedelta(hours=1)}, SECRET_KEY, algorithm='HS256')

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    try:
        c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed))
        conn.commit()
    except sqlite3.IntegrityError:
        return jsonify({'message': 'Username already exists'}), 400
    return jsonify({'message': 'User registered successfully'})

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    c.execute('SELECT id, password FROM users WHERE username = ?', (username,))
    result = c.fetchone()
    if result and bcrypt.checkpw(password.encode('utf-8'), result[1] ):
        token = generate_jwt_token(result[0])
        return jsonify({'token': token})
    return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/recipes', methods=['POST', 'GET'])
def manage_recipes():
    token = request.headers.get('Authorization').split()[1]
    try:
        user_id = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])['user_id']
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return jsonify({'message': 'Invalid token'}), 401

    if request.method == 'POST':
        data = request.get_json()
        title = data.get('title')
        content = data.get('content')
        c.execute('INSERT INTO recipes (user_id, title, content) VALUES (?, ?, ?)', (user_id, title, content))
        conn.commit()
        return jsonify({'message': 'Recipe saved successfully'})
    elif request.method == 'GET':
        c.execute('SELECT id, title, content FROM recipes WHERE user_id = ?', (user_id,))
        recipes = [{'id': row[0], 'title': row[1], 'content': row[2]} for row in c.fetchall()]
        return jsonify(recipes)

# Placeholder endpoint for agent interaction
@app.route('/agent', methods=['POST'])
def agent_interact():
    data = request.get_json()
    agent_code = data.get('agent_code')
    # Placeholder logic; implement agent interaction here

    from graph import graph

    ai_response = graph.invoke({"messages": agent_code},
                 config = {"configurable": {"thread_id": "user1"}})

    response = ai_response["messages"][-1]


    return jsonify({'message': response.content})

    return jsonify({'message': 'Agent code received', 'agent_code': agent_code})

if __name__ == '__main__':
    app.run(debug=True)