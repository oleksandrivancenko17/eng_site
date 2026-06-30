document.addEventListener("DOMContentLoaded", function () {
    const loginForm = document.getElementById("login-form");
    const registerForm = document.getElementById("register-form");

    // =====================================
    // ЛОГІКА ДЛЯ ЛОГІНУ (JWT)
    // =====================================
    if (loginForm) {
        loginForm.addEventListener("submit", async function (e) {
            e.preventDefault();
            const btn = document.getElementById('login-btn');
            const errorsDiv = document.getElementById('login-errors');

            btn.disabled = true;
            btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Входимо...';
            errorsDiv.classList.add('d-none');

            const data = {
                username: loginForm.username.value,
                password: loginForm.password.value
            };

            try {
                // ОНОВЛЕНИЙ МАРШРУТ ДО API ЛОГІНУ
                const response = await fetch('/users/api/v1/auth/login/', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });

                const result = await response.json();

                if (response.ok) {
                    // Зберігаємо JWT токени
                    setTokens(result.access, result.refresh);
                    window.location.href = '/';
                } else {
                    errorsDiv.textContent = result.detail || 'Неправильний логін або пароль';
                    errorsDiv.classList.remove('d-none');
                    btn.disabled = false;
                    btn.innerHTML = 'Увійти';
                }
            } catch (error) {
                errorsDiv.textContent = 'Помилка мережі.';
                errorsDiv.classList.remove('d-none');
                btn.disabled = false;
                btn.innerHTML = 'Увійти';
            }
        });
    }

    // =====================================
    // ЛОГІКА ДЛЯ РЕЄСТРАЦІЇ
    // =====================================
    if (registerForm) {
        registerForm.addEventListener("submit", async function (e) {
            e.preventDefault();
            const btn = document.getElementById('register-btn');
            const globalErrors = document.getElementById('register-errors');

            document.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));
            globalErrors.classList.add('d-none');

            btn.disabled = true;
            btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Створюємо...';

            const data = {
                username: registerForm.username.value,
                email: registerForm.email.value,
                password: registerForm.password.value,
            };

            if (data.password !== registerForm.password_confirm.value) {
                document.getElementById('password_confirm').classList.add('is-invalid');
                document.getElementById('error-password_confirm').textContent = "Паролі не збігаються!";
                btn.disabled = false;
                btn.innerHTML = 'Створити акаунт';
                return;
            }

            try {
                // ОНОВЛЕНИЙ МАРШРУТ ДО API РЕЄСТРАЦІЇ
                const response = await fetch('/users/api/v1/users/register/', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });

                const result = await response.json();

                if (response.ok) {
                    window.location.href = '/users/login/';
                } else {
                    for (const [field, errors] of Object.entries(result)) {
                        const inputEl = document.getElementById(field);
                        if (inputEl) {
                            inputEl.classList.add('is-invalid');
                            document.getElementById(`error-${field}`).textContent = errors[0];
                        } else {
                            globalErrors.textContent += errors[0] + ' ';
                            globalErrors.classList.remove('d-none');
                        }
                    }
                    btn.disabled = false;
                    btn.innerHTML = 'Створити акаунт';
                }
            } catch (error) {
                globalErrors.textContent = 'Помилка мережі.';
                globalErrors.classList.remove('d-none');
                btn.disabled = false;
                btn.innerHTML = 'Створити акаунт';
            }
        });
    }
});