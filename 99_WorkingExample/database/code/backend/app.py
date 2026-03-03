from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os
import json

app = Flask(__name__)
CORS(app)

DB_NAME = 'recipe_database.db'

# Function to initialize the database
def init_db():
    if not os.path.exists(DB_NAME):
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute('''
            CREATE TABLE recipes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                ingredients TEXT NOT NULL,
                steps TEXT NOT NULL
            )
            ''')
            conn.commit()
            print('Initialized database with recipes table.')
    else:
        print('Database already initialized.')

@app.route('/add_recipe', methods=['POST'])
def add_recipe():
    recipe_data = request.json
    try:
        for dish_name, content in recipe_data.items():
            ingredients = content.get('ingredients')
            recipe_steps = content.get('recipe')

            if not isinstance(ingredients, list) or not isinstance(recipe_steps, list):
                return jsonify({'error': 'Invalid format for ingredients or recipe steps.'}), 400

            with sqlite3.connect(DB_NAME) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'INSERT INTO recipes (name, ingredients, steps) VALUES (?, ?, ?)',
                    (dish_name, json.dumps(ingredients), json.dumps(recipe_steps))
                )
                conn.commit()
        return jsonify({'status': 'Recipe added successfully.'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/recipes', methods=['GET'])
def get_recipes():
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT name, ingredients, steps FROM recipes')
            recipes = cursor.fetchall()
            return jsonify([{ "name": row[0], "ingredients": json.loads(row[1]), "steps": json.loads(row[2]) } for row in recipes])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/ai', methods=['POST'])
def ai_interface():
    user_query = request.json.get('query')
    # Here you would integrate your AI model, for this example we mock a response with a possible recipe JSON
    ai_response = {
        "response": "AI: This is a simulated response",
        "recipe_data": {'Pasta': {"ingredients": ["Pasta: 200g", "Tomato: 100g"], "recipe": ["Boil pasta", "Add sauce"]}}
    }

    # Check if AI response has recipe_data to be stored
    if 'recipe_data' in ai_response:
        recipe_data = ai_response['recipe_data']
        store_recipe_data(recipe_data)

    return jsonify(ai_response)

# Function to store recipes from AI response
def store_recipe_data(recipe_data):
    try:
        for dish_name, content in recipe_data.items():
            ingredients = content.get('ingredients')
            recipe_steps = content.get('recipe')

            if not isinstance(ingredients, list) or not isinstance(recipe_steps, list):
                print('Invalid format for ingredients or recipe steps.')
                continue

            with sqlite3.connect(DB_NAME) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'INSERT OR IGNORE INTO recipes (name, ingredients, steps) VALUES (?, ?, ?)',
                    (dish_name, json.dumps(ingredients), json.dumps(recipe_steps))
                )
                conn.commit()
                print('Stored AI-generated recipe:', dish_name)
    except Exception as e:
        print('Error storing AI-generated recipe:', str(e))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
