# AI Recipe Manager

## Project Description
This application provides a secure platform for users to store and manage AI-generated recipes. Users can register, log in, and have access to a personal dashboard where they can manage their recipes. The app includes functionality to interact with an AI agent.

## Architecture Summary
The application uses a client-server architecture. The backend is built with Flask and stores data in a SQLite database, while the frontend is a simple HTML/CSS/JavaScript interface.

## Tech Stack
- HTML/CSS for web page structure and styling
- JavaScript for client-side interactivity
- Flask for the backend server
- SQLite for local data storage
- JWT for token-based authentication
- bcrypt for password hashing

## Running the Application
1. **Setup the Backend**
    - Install Flask, bcrypt, jwt, and flask-cors using pip:
      ```sh
      pip install flask bcrypt pyjwt flask-cors
      ```
    - Run the Flask application:
      ```sh
      python backend/app.py
      ```

2. **Access the Frontend**
    - Simply open `frontend/index.html` in a web browser.

## Features
- User registration and authentication
- Manage personal recipes (Create, View)
- Submit agent code for AI interaction (currently a placeholder implementation)