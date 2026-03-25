# AI Recipe Manager

## Project Description
AI Recipe Manager is a secure web application designed to allow users to store and manage AI-generated recipes. The application includes user authentication, recipe management, and agent code input features.

## Architecture Summary
The application utilizes a client-server architecture with a clear separation between the frontend and backend components.

## Tech Stack
- **HTML/CSS**: Structure and styling of the frontend application.
- **JavaScript**: For client-side interactivity.
- **Flask**: Backend server framework.
- **SQLite**: Database for local storage of user and recipe data.
- **JWT**: Token-based authentication for securing user sessions.
- **bcrypt**: For secure password hashing.

## Getting Started

### Prerequisites
- Python 3
- Flask
- Flask-JWT-Extended
- SQLAlchemy
- bcrypt

### Installation
1. Clone the repository.
   ```bash
   git clone <repository-url>
   ```
2. Navigate to the backend directory, set up a virtual environment, and install dependencies.
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
3. Run the Flask application.
   ```bash
   python app.py
   ```
4. Open `frontend/index.html` in a web browser to interact with the application.

## Usage
- Register a new account or login using existing credentials.
- Use the dashboard to input agent responses and store AI-generated recipes.
- View and manage saved recipes from the user dashboard.

## Notes
Ensure the server is running to allow the frontend to communicate effectively with the backend endpoints.