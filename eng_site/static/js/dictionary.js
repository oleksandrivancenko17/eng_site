/**
 * @fileoverview Dictionary SPA Controller
 * Handles loading words, dynamic filtering, pagination, and adding words to SRS.
 */

document.addEventListener('DOMContentLoaded', function () {
    const tableBody = document.getElementById('dictionary-table-body');
    const filterForm = document.getElementById('dictionary-filter-form');
    const pagContainer = document.getElementById('dictionary-pagination');
    const categorySelect = document.getElementById('category-filter');

    if (!tableBody) return;

    // Load initial data
    loadCategories();
    fetchWords('/dictionary/api/v1/words/');

    // Handle Filters
    filterForm.addEventListener('submit', function (e) {
        e.preventDefault();
        const formData = new FormData(filterForm);
        const params = new URLSearchParams();

        for (const [key, value] of formData.entries()) {
            if (value) params.append(key, value);
        }
        fetchWords(`/dictionary/api/v1/words/?${params.toString()}`);
    });

    /**
     * Fetches categories from the Library/Dictionary API and populates the select dropdown.
     */
    async function loadCategories() {
        try {
            const response = await fetchWithAuth('/library/api/v1/categories/');
            if (response.ok) {
                const data = await response.json();
                const categories = data.results || data;

                categories.forEach(cat => {
                    categorySelect.insertAdjacentHTML('beforeend', `<option value="${cat.id}">${cat.name}</option>`);
                });
            }
        } catch (error) {
            console.error("Failed to load categories:", error);
        }
    }

    /**
     * Fetches words list from the API and renders the table.
     * @param {string} url - API endpoint with query params
     */
    async function fetchWords(url) {
        tableBody.innerHTML = `<tr><td colspan="5" class="text-center py-5"><div class="spinner-border text-primary" role="status"></div></td></tr>`;
        pagContainer.innerHTML = '';

        try {
            const response = await fetchWithAuth(url);
            if (response.ok) {
                const data = await response.json();
                const words = data.results || data;

                renderWords(words);
                renderPagination(data.previous, data.next);
            } else {
                tableBody.innerHTML = `<tr><td colspan="5" class="text-center py-5 text-danger">Помилка завантаження словника.</td></tr>`;
            }
        } catch (error) {
            console.error("API Error [fetchWords]:", error);
            tableBody.innerHTML = `<tr><td colspan="5" class="text-center py-5 text-danger">Помилка мережі. Перевірте з'єднання.</td></tr>`;
        }
    }

    /**
     * Renders array of word objects into the table body.
     * @param {Array} words
     */
    function renderWords(words) {
        tableBody.innerHTML = '';

        if (words.length === 0) {
            tableBody.innerHTML = `<tr><td colspan="5" class="text-center py-5 text-muted">За вашим запитом слів не знайдено.</td></tr>`;
            return;
        }

        words.forEach(word => {
            // Оновлено: використовуємо category_name з бекенду
            const catName = word.category_name || '-';
            const levelClass = word.level.includes('A') ? 'bg-success' : (word.level.includes('B') ? 'bg-primary' : 'bg-danger');

            // Оновлено: використовуємо is_learning з бекенду
            const isLearning = word.is_learning;

            const actionHtml = isLearning
                ? `<span class="badge bg-success bg-opacity-10 text-success border border-success px-3 py-2 rounded-pill"><i class="bi bi-check-circle me-1"></i> Вже вчу</span>`
                : `<button class="btn btn-sm btn-primary rounded-pill px-3 shadow-sm add-word-btn" data-word-id="${word.id}"><i class="bi bi-plus-circle me-1"></i> Вивчати</button>`;

            const tr = `
                <tr>
                    <td class="ps-4 py-3 fw-bold text-dark fs-5">${word.english_word}</td>
                    <td class="py-3">
                        <span class="d-block text-muted mb-1">${word.translation}</span>
                        ${catName !== '-' ? `<span class="badge bg-light text-secondary border category-tag"><i class="bi bi-tag me-1"></i> ${catName}</span>` : ''}
                    </td>
                    <td class="py-3 text-muted small fst-italic">${word.example ? `"${word.example}"` : '-'}</td>
                    <td class="py-3 text-center"><span class="badge ${levelClass} text-white">${word.level}</span></td>
                    <td class="pe-4 py-3 text-end">${actionHtml}</td>
                </tr>
            `;
            tableBody.insertAdjacentHTML('beforeend', tr);
        });

        attachAddWordListeners();
    }

    function renderPagination(prevUrl, nextUrl) {
        pagContainer.innerHTML = '';
        if (prevUrl) pagContainer.insertAdjacentHTML('beforeend', `<li class="page-item"><button class="page-link" onclick="window.fetchWordsGlobal('${prevUrl}')">Попередня</button></li>`);
        if (nextUrl) pagContainer.insertAdjacentHTML('beforeend', `<li class="page-item"><button class="page-link" onclick="window.fetchWordsGlobal('${nextUrl}')">Наступна</button></li>`);
    }

    // Expose fetch function globally for inline pagination buttons
    window.fetchWordsGlobal = fetchWords;

    /**
     * Attaches click event listeners to dynamically generated "Add to Flashcards" buttons.
     */
    function attachAddWordListeners() {
        document.querySelectorAll('.add-word-btn').forEach(btn => {
            btn.addEventListener('click', async function () {
                const wordId = this.getAttribute('data-word-id');
                const buttonElement = this;
                const originalHtml = buttonElement.innerHTML;

                buttonElement.innerHTML = '<span class="spinner-border spinner-border-sm"></span>';
                buttonElement.disabled = true;

                try {
                    const response = await fetchWithAuth('/flashcards/api/v1/cards/add-existing-word/', {
                        method: 'POST',
                        body: JSON.stringify({ word_id: parseInt(wordId) })
                    });

                    const data = await response.json();

                    if (response.ok && (data.status === 'success' || data.status === 'info')) {
                        const badgeText = data.status === 'success' ? 'Додано' : 'Вже вчу';
                        buttonElement.outerHTML = `
                            <span class="badge bg-success bg-opacity-10 text-success border border-success px-3 py-2 rounded-pill fade-in">
                                <i class="bi bi-check-circle me-1"></i> ${badgeText}
                            </span>
                        `;
                    } else {
                        buttonElement.innerHTML = '<i class="bi bi-x-circle"></i> Помилка';
                        buttonElement.classList.replace('btn-primary', 'btn-danger');
                        setTimeout(() => {
                            buttonElement.innerHTML = originalHtml;
                            buttonElement.classList.replace('btn-danger', 'btn-primary');
                            buttonElement.disabled = false;
                        }, 2000);
                    }
                } catch (error) {
                    console.error("Помилка додавання слова:", error);
                    buttonElement.innerHTML = 'Помилка';
                    buttonElement.disabled = false;
                }
            });
        });
    }
});