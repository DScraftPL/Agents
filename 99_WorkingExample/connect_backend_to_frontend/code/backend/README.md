# Backend for AI Communication Web Application

## Project Description
This backend is part of a web application that allows users to submit queries or commands to an AI model and receive responses. It processes user inputs and communicates with the AI model to retrieve responses.

## Architecture Summary
The application's architecture follows a client-server model. The backend works as a server application that handles incoming requests from the frontend and generates appropriate responses by interfacing with an AI model.

## Tech Stack
- **Python** — Used for server-side logic.
- **Flask** — Lightweight framework to serve the backend.
- **Flask-CORS** — To enable Cross-Origin Resource Sharing (CORS).

## How to Run
1. Navigate to the `backend` directory.
2. Install the dependencies: `pip install -r requirements.txt`
3. Run the application: `python app.py`
4. The server will start at `http://127.0.0.1:5000`, ready to receive requests from the frontend.