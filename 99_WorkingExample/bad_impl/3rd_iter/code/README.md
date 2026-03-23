# Project Description
This project is a chat interface that allows users to interact with an AI agent. Users can send messages through a web-based chat interface and receive AI-generated responses.

# Architecture Summary
The system uses a client-server architecture where the frontend is built with HTML, CSS, and JavaScript, providing a chat interface. The backend is a Flask-based server that processes user messages and generates AI responses using the OpenAI API. Messages and some data are stored in an SQLite database.

# Tech Stack
- **HTML/CSS/JavaScript** — for building the user interface.
- **Flask** — Python-based framework used to create the backend server.
- **SQLite** — a lightweight database to store generated messages and related data.
- **OpenAI API** — for generating AI responses.

# How to Run
1. Clone this repository.
2. Navigate to the `backend/` directory and install the required packages using the command:
   ```bash
   pip install -r requirements.txt
   ```
3. Start the backend server by running:
   ```bash
   python app.py
   ```
   Ensure you replace `YOUR_OPENAI_API_KEY` in `app.py` with your actual OpenAI API key.
4. Open the `index.html` file under `frontend/` directory in a web browser.
5. Use the chat interface to send messages to the AI and receive responses.