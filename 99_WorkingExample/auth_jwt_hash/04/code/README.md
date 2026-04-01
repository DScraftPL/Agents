# Culinary Chat Application

## Project Description
This project is a web application that allows users to chat with a culinary agent, create accounts, and store recipes. It includes functionality for user management and recipe management while providing placeholders for future integration with the culinary agent.

## Architecture Summary
The application follows a client-server architecture:
- **Client:** User Interface is built for the users to interact with the culinary agent and manage accounts and recipes.
- **Server:** Handles user authentication, data storage and management, providing a RESTful API to the client.

## Tech Stack
- **Backend:** Python (Flask)
- **Frontend:** HTML, CSS, JavaScript
- **Database:** SQLite

## How to Run
1. Install required dependencies:
   ```bash
   pip install flask
   ````
2. Navigate to the backend directory and start the server:
   ```bash
   cd backend
   flask run
   ```
3. Open `frontend/index.html` in a web browser to use the application.