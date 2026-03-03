# Backend for Recipe Management Web Application

## Project Description
This backend is part of a web application that allows storage and retrieval of recipe data conforming to a specific schema. It processes recipe data submissions and stores them in a SQLite database. The application also interacts with an AI model to receive recipe suggestions and automatically stores valid recipes.

## Architecture Summary
The application's architecture follows a client-server model. The backend works as a server application that handles incoming requests from the frontend, validates the recipe data, and stores it in a dedicated database. Recipes can be added manually or automatically by interpreting AI responses.

## Tech Stack
- **Python** — Used for server-side logic.
- **Flask** — Lightweight framework to serve the backend.
- **Flask-CORS** — To enable Cross-Origin Resource Sharing (CORS).
- **SQLite** — Database for storing recipes.

## How to Run
1. Navigate to the `backend` directory.
2. Install the dependencies: `pip install -r requirements.txt`
3. Run the application: `python app.py`
4. The server will start at `http://127.0.0.1:5000`, ready to receive recipes manually or through AI responses and store them in the database. The database will be initialized on the first run if it does not already exist.
