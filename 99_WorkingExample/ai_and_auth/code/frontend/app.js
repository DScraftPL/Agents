$(document).ready(function() {
    $('#login-form').on('submit', function(event) {
        event.preventDefault();
        const username = $('#login-username').val();
        const password = $('#login-password').val();
        $.ajax({
            url: 'http://localhost:5000/login',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ username, password }),
            success: function(response) {
                localStorage.setItem('token', response.token);
                $('#auth').hide();
                $('#dashboard').show();
                loadRecipes();
            },
            error: function() {
                alert('Login failed!');
            }
        });
    });

    $('#register-form').on('submit', function(event) {
        event.preventDefault();
        const username = $('#register-username').val();
        const password = $('#register-password').val();
        $.ajax({
            url: 'http://localhost:5000/register',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ username, password }),
            success: function() {
                alert('Registration successful! Please log in.');
            },
            error: function() {
                alert('Registration failed!');
            }
        });
    });

    $('#logout').on('click', function() {
        localStorage.removeItem('token');
        $('#auth').show();
        $('#dashboard').hide();
    });

    function loadRecipes() {
        const token = localStorage.getItem('token');
        if (!token) return;
        $.ajax({
            url: '/recipes',
            method: 'GET',
            headers: { 'x-access-token': token },
            success: function(response) {
                // Handle displaying recipes
            },
            error: function() {
                alert('Could not load recipes!');
            }
        });
    }

    // Check if user is already logged in
    if (localStorage.getItem('token')) {
        $('#auth').hide();
        $('#dashboard').show();
        loadRecipes();
    }
});