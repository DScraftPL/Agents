
from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import bcrypt
import jwt
import datetime

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = 'your_secret_key'

from graph import graph

# Initialize the database
def init_db():
    conn = sqlite3.connect('user_recipes.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 username TEXT UNIQUE NOT NULL,
                 password TEXT NOT NULL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS recipes (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 user_id INTEGER NOT NULL,
                 title TEXT NOT NULL,
                 content TEXT NOT NULL,
                 FOREIGN KEY(user_id) REFERENCES users(id))''')
    conn.commit()
    conn.close()

from functools import wraps
from flask import request, jsonify
import jwt

def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Token is missing!'}), 401
        try:
            decoded_token = jwt.decode(
                token.split()[1],
                app.config['SECRET_KEY'],
                algorithms=['HS256']
            )
            return f(decoded_token, *args, **kwargs)
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Token is invalid!'}), 401
    return decorator

# Route to register a new user
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    try:
        conn = sqlite3.connect('user_recipes.db')
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                  (username, hashed_password))
        conn.commit()
        return jsonify({'message': 'User registered successfully'}), 201
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Username already exists'}), 400
    finally:
        conn.close()

# Route to authenticate a user and return a JWT token
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    conn = sqlite3.connect('user_recipes.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = c.fetchone()
    conn.close()
    if user and bcrypt.checkpw(password.encode('utf-8'), user[2]):
        token = jwt.encode({'user_id': user[0], 'exp': datetime.datetime.utcnow(
        ) + datetime.timedelta(hours=1)}, app.config['SECRET_KEY'])
        return jsonify({'message': 'Login successful', 'token': token})
    else:
        return jsonify({'error': 'Invalid credentials'}), 401

# Route to add a new recipe
@app.route('/recipes', methods=['POST'])
@token_required
def add_recipe(decoded_token):
    data = request.get_json()
    user_id = decoded_token['user_id']
    title = data.get('title')
    content = data.get('content')
    conn = sqlite3.connect('user_recipes.db')
    c = conn.cursor()
    c.execute("INSERT INTO recipes (user_id, title, content) VALUES (?, ?, ?)",
              (user_id, title, content))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Recipe added successfully'}), 201

# Route to retrieve recipes for a user
@app.route('/recipes', methods=['GET'])
@token_required
def get_recipes(decoded_token):
    user_id = decoded_token['user_id']
    conn = sqlite3.connect('user_recipes.db')
    c = conn.cursor()
    c.execute("SELECT id, title, content FROM recipes WHERE user_id = ?", (user_id,))
    recipes = c.fetchall()
    conn.close()
    return jsonify({'recipes': recipes})

@app.route('/chat', methods=['POST'])
@token_required
# Placeholder for the chat with the culinary agent
def culinary_agent_chat(decoded_token):
    user_query = request.json.get('message')
    ai_response = graph.invoke({"messages": user_query},
                               config={"configurable": {"thread_id": "user1"}})

    recipe_data = ai_response.get('recipe_data')

    # Save recipe data to database if it exists
    if recipe_data:
        conn = sqlite3.connect('user_recipes.db')   
        c = conn.cursor()
        user_id = decoded_token['user_id']
        for title, details in recipe_data.items():
            content = f"Ingredients: {', '.join(details['ingredients'])}\nRecipe: {' '.join(details['recipe'])}"
            c.execute("INSERT INTO recipes (user_id, title, content) VALUES (?, ?, ?)",
                      (user_id, title, content))
        conn.commit()
        conn.close()

    response = ai_response["messages"][-1]

    print(response.content)

    return jsonify({'message': response.content})


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
