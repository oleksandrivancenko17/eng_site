/**
 * @fileoverview Core utility functions for API requests and JWT token management.
 */

function setTokens(access, refresh) {
    localStorage.setItem('access_token', access);
    localStorage.setItem('refresh_token', refresh);
}

function clearTokens() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
}

async function fetchWithAuth(url, options = {}) {
    const token = localStorage.getItem('access_token');

    if (!options.headers) {
        options.headers = {};
    }

    options.headers['Content-Type'] = 'application/json';

    if (token) {
        options.headers['Authorization'] = `Bearer ${token}`;
    }

    return fetch(url, options);
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

/**
 * SPA Global Authentication Check
 */
async function initializeAuthState() {
    const authContainer = document.getElementById('navbar-auth-container');
    if (!authContainer) return;

    const token = localStorage.getItem('access_token');

    if (token) {
        try {
            const response = await fetchWithAuth('/users/api/v1/users/me/');

            if (response.ok) {
                const user = await response.json();

                authContainer.innerHTML = `
                    <span class="text-light me-3 fw-medium">
                        <i class="bi bi-person-circle me-1"></i> Привіт, ${user.username}!
                    </span>
                    <button id="spa-logout-btn" class="btn btn-outline-light btn-sm fw-bold">Вийти</button>
                `;

                document.getElementById('spa-logout-btn').addEventListener('click', function () {
                    clearTokens();
                    window.location.href = '/users/login/';
                });

                return;
            }
        } catch (error) {
            console.error("JWT Validation failed:", error);
        }
    }

    authContainer.innerHTML = `
        <a href="/users/login/" class="btn btn-outline-light btn-sm me-2 fw-bold">Увійти</a>
        <a href="/users/register/" class="btn btn-primary btn-sm fw-bold">Реєстрація</a>
    `;

    const publicPages = ['/users/login/', '/users/register/', '/'];
    if (!publicPages.includes(window.location.pathname)) {
        window.location.href = '/users/login/';
    }
}

document.addEventListener('DOMContentLoaded', initializeAuthState);