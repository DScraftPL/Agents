document.addEventListener('DOMContentLoaded', () => {
    const registerForm = document.getElementById('register-form');
    const loginForm = document.getElementById('login-form');
    const recipeForm = document.getElementById('recipe-form');
    const agentForm = document.getElementById('agent-form');
    const dashboard = document.getElementById('dashboard');
    const recipesList = document.getElementById('recipes-list');

    registerForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = document.getElementById('register-username').value;
        const password = document.getElementById('register-password').value;

        const response = await fetch('http://127.0.0.1:5000/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
        const result = await response.json();
        alert(result.message);
    });

    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = document.getElementById('login-username').value;
        const password = document.getElementById('login-password').value;

        const response = await fetch('http://127.0.0.1:5000/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
        const result = await response.json();
        if (response.ok) {
            localStorage.setItem('token', result.token);
            alert('Login successful!');
            registerForm.style.display = 'none';
            loginForm.style.display = 'none';
            dashboard.style.display = 'block';
            loadRecipes();
        } else {
            alert(result.message);
        }
    });

    recipeForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const title = document.getElementById('recipe-title').value;
        const content = document.getElementById('recipe-content').value;
        const token = localStorage.getItem('token');

        const response = await fetch('http://127.0.0.1:5000/recipes', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ title, content })
        });
        const result = await response.json();
        alert(result.message);
        loadRecipes();
    });

    agentForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const agentCode = document.getElementById('agent-code').value;
        const token = localStorage.getItem('token');

        const response = await fetch('http://127.0.0.1:5000/agent', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ agent_code: agentCode })
        });

        const result = await response.json();
        alert(result.message);
    });

    async function loadRecipes() {
        const token = localStorage.getItem('token');
        const response = await fetch('http://127.0.0.1:5000/recipes', {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        const recipes = await response.json();
        recipesList.innerHTML = '';
        recipes.forEach(recipe => {
            const recipeDiv = document.createElement('div');
            recipeDiv.textContent = `${recipe.title}: ${recipe.content}`;
            recipesList.appendChild(recipeDiv);
        });
    }
});