# Project AI Chat Interface

## Description
This project provides an interactive chat application that allows users to communicate with an AI agent. The application consists of a web-based chat interface and a Flask backend that processes messages and communicates with an AI model.

## Architecture Summary
- **Frontend**: Developed using HTML/CSS/JavaScript, the frontend includes a user-friendly chat interface.
- **Backend**: Implemented with Flask, it handles incoming messages, generates AI responses via the OpenAI API, and stores messages in an SQLite database.
- **Communication**: Uses Socket.IO for real-time communication between the client and server.

## Tech Stack
- **Frontend**: HTML, CSS, JavaScript
- **Backend**: Flask
- **Real-Time Communication**: Socket.IO
- **AI Integration**: OpenAI API
- **Database**: SQLite for storage of messages
- **Security**: HTTPS for secure data transmission

## Running the Application
1. **Set up Backend**:
   - Install dependencies:
     ```
     pip install flask flask-cors
     ```
   - Run the Flask server:
     ```
     python backend/app.py
     ```
2. **Frontend**:
   - Open `frontend/index.html` in a web browser to interact with the chat interface.

Ensure the Flask server is running before accessing the chat interface.
