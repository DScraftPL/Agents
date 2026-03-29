# Penguin Tracker

## Project Description
The Penguin Tracker system is designed to enable real-time location tracking of individual penguins, record historical movement data, provide visualizations of penguin movements, and allow users to track specific penguins for study purposes. It features a user-friendly interface that presents data through maps and dashboards.

## Architecture Summary
The system follows a client-server architecture that supports efficient data processing and visualization. The server handles data storage and tracking updates, while the client displays both real-time and historical data.

## Tech Stack
- Backend: Flask
- Frontend: HTML, CSS, JavaScript (with Leaflet.js for map rendering)
- Database: SQLite

## Simple Authentication
The system uses Basic Authentication for securing the API endpoints.

## How to Run
### Backend
1. Navigate to the `backend/` directory.
2. Install the required dependencies: `pip install flask flask_cors`
3. Run the Flask app: `python app.py`

### Frontend
1. Open `frontend/index.html` in a web browser.

Ensure the backend server is running to allow the frontend to retrieve data.