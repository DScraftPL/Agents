# Description
The system is a web application where users can create accounts, log in, and chat with a culinary agent. The backend is protected through JWT authentication to ensure that only authorized users can interact with the chat endpoint and manage their stored recipes.

# UI/UX
The user interface includes a login form and a chat interface. Upon logging in, users are redirected from the login form to a chat screen where they can communicate with the culinary agent. The application is designed to be simple and intuitive, making use of plain HTML, CSS, and vanilla JavaScript for interaction.

# Modules
- **Authentication Module**: Handles user registration and login functionality with JWT token issuance.
- **Chat Module**: Provides an interface for users to send messages to the agent.
- **Recipe Management Module**: Allows authenticated users to store and retrieve recipes.
- **JWT Verification**: Ensures JWT tokens are valid for access to specific routes.

# Architecture
Client-Server: This pattern suitably separates concerns between the client-side interface handling user interactions and the server-side business logic and data persistence, enforcing security with JWT-based authentication.