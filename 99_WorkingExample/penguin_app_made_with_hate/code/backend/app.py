from flask import Flask, jsonify, request, Response
from flask_cors import CORS
from functools import wraps
import json

app = Flask(__name__)
CORS(app)

# Simple in-memory user database
users = {
    'admin': 'password123'
}

penguins_data = {
    'Penguin1': {
        'location': [-25.344, 131.036]
    },
    'Penguin2': {
        'location': [37.7749, -122.4194]
    }
}

def check_auth(username, password):
    """Check if a username/password combination is valid."""
    return users.get(username) == password


def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
    'Could not verify your login!\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

@app.route('/api/penguins', methods=['GET'])
@requires_auth
def get_penguins():
    return jsonify(penguins_data)

if __name__ == '__main__':
    app.run(debug=True)
