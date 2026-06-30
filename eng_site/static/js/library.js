/**
 * @fileoverview Library SPA Controller
 * Handles async data fetching, rendering article lists, article details, and translation.
 */

document.addEventListener('DOMContentLoaded', function () {

    // ==========================================
    // MODULE: READING LIST (Feed)
    // ==========================================
    const articlesContainer = document.getElementById('articles-container');
    const filterForm = document.getElementById('filter-form');
    const categorySelect = document.getElementById('category-filter');

    if (articlesContainer) {
        loadLibraryCategories();
        fetchArticles('/library/api/v1/articles/');

        filterForm.addEventListener('submit', function (e) {
            e.preventDefault();
            const formData = new FormData(filterForm);
            const params = new URLSearchParams();

            for (const [key, value] of formData.entries()) {
                if (value) params.append(key, value);
            }
            fetchArticles(`/library/api/v1/articles/?${params.toString()}`);
        });

        document.getElementById('reset-filters').addEventListener('click', () => {
            filterForm.reset();
            fetchArticles('/library/api/v1/articles/');
        });
    }

    async function loadLibraryCategories() {
        if (!categorySelect) return;
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
            console.error("Failed to load library categories:", error);
        }
    }

    async function fetchArticles(url) {
        try {
            const response = await fetchWithAuth(url);
            const data = await response.json();

            const results = data.results || data;
            const count = data.count || results.length;

            document.getElementById('articles-count').innerText = count;
            renderArticles(results);
            renderPagination(data.previous, data.next);
        } catch (error) {
            console.error("API Error [fetchArticles]:", error);
            articlesContainer.innerHTML = '<p class="text-danger px-3">Не вдалося завантажити статті.</p>';
        }
    }

    function renderArticles(articles) {
        articlesContainer.innerHTML = '';
        if (articles.length === 0) {
            articlesContainer.innerHTML = '<div class="col-12 text-center py-5"><h4 class="text-muted">За вашим запитом нічого не знайдено 😔</h4></div>';
            return;
        }

        articles.forEach(article => {
            const levelClass = article.level.includes('A') ? 'bg-success' : (article.level.includes('B') ? 'bg-primary' : 'bg-danger');
            const categoryName = article.category_name || article.category?.name || 'Різне';

            const card = `
                <div class="col-md-6">
                    <div class="card text-card h-100 shadow-sm border-0">
                        <img src="https://placehold.co/600x400/e9ecef/495057?text=Reading" class="card-img-top" alt="Cover">
                        <div class="card-body d-flex flex-column">
                            <div class="d-flex justify-content-between align-items-center mb-2">
                                <span class="badge ${levelClass}">${article.level}</span>
                            </div>
                            <h5 class="card-title fw-bold">${article.title}</h5>
                            <p class="card-text text-muted small mb-3">${article.description.substring(0, 100)}...</p>
                            <div class="mt-auto d-flex justify-content-between align-items-center">
                                <span class="badge bg-light text-dark border"><i class="bi bi-tag me-1"></i> ${categoryName}</span>
                            </div>
                        </div>
                        <div class="card-footer bg-white border-top-0 pb-3 pt-0">
                            <a href="/library/article/${article.id}/" class="btn btn-outline-primary w-100">Читати статтю</a>
                        </div>
                    </div>
                </div>
            `;
            articlesContainer.insertAdjacentHTML('beforeend', card);
        });
    }

    function renderPagination(prevUrl, nextUrl) {
        const pagContainer = document.getElementById('pagination-container');
        if (!pagContainer) return;
        pagContainer.innerHTML = '';

        if (prevUrl) {
            pagContainer.insertAdjacentHTML('beforeend', `<li class="page-item"><button class="page-link" onclick="window.fetchArticlesGlobal('${prevUrl}')">Назад</button></li>`);
        }
        if (nextUrl) {
            pagContainer.insertAdjacentHTML('beforeend', `<li class="page-item"><button class="page-link" onclick="window.fetchArticlesGlobal('${nextUrl}')">Вперед</button></li>`);
        }
    }

    window.fetchArticlesGlobal = fetchArticles;


    // ==========================================
    // MODULE: ARTICLE DETAILS (Reader & Translator)
    // ==========================================
    const articleTextContainer = document.getElementById('article-text');

    if (articleTextContainer) {

        const articleIdMatch = window.location.pathname.match(/\/library\/article\/(\d+)\//);
        const articleId = articleIdMatch ? articleIdMatch[1] : null;

        if (articleId) {
            fetchArticleDetail(articleId);
        } else {
            showArticleError("Статтю не знайдено");
        }

        async function fetchArticleDetail(id) {
            try {
                const response = await fetchWithAuth(`/library/api/v1/articles/${id}/`);
                if (response.ok) {
                    const article = await response.json();

                    document.getElementById('article-title').innerText = article.title;

                    const descEl = document.getElementById('article-description');
                    descEl.innerText = article.description;
                    descEl.classList.remove('placeholder-glow');

                    const levelEl = document.getElementById('article-level');
                    levelEl.innerText = article.level;
                    levelEl.className = `badge ${article.level.includes('A') ? 'bg-success' : (article.level.includes('B') ? 'bg-primary' : 'bg-danger')}`;

                    articleTextContainer.innerHTML = `<div class="fs-5 lh-lg reading-text text-dark" style="text-align: justify;">${article.content}</div>`;

                    const catId = article.category?.id || article.category || 1;
                    articleTextContainer.setAttribute('data-category-id', catId);

                } else {
                    showArticleError("Не вдалося завантажити статтю. Можливо, її видалено.");
                }
            } catch (error) {
                console.error("API Error [fetchArticleDetail]:", error);
                showArticleError("Помилка мережі. Перевірте з'єднання.");
            }
        }

        function showArticleError(msg) {
            document.getElementById('article-title').innerText = 'Помилка';
            document.getElementById('article-description').classList.remove('placeholder-glow');
            document.getElementById('article-description').innerText = '';
            document.getElementById('article-level').innerText = 'Error';
            articleTextContainer.innerHTML = `<div class="alert alert-danger">${msg}</div>`;
        }

        const translateUrl = document.getElementById('translation-panel')?.getAttribute('data-translate-url') || '/library/api/v1/translate/';
        let currentSelectedWord = "";
        let currentTranslation = "";
        let currentExampleSentence = "";

        // Створюємо єдину функцію для обробки виділення (підтримує фрази та мобільні пристрої)
        function handleTextSelection() {
            setTimeout(() => {
                let selection = window.getSelection();
                let selectedText = selection.toString().trim();

                // Обмежуємо довжину до 150 символів, щоб не перекладати весь абзац випадково
                if (selectedText.length > 0 && selectedText.length < 150 && /[a-zA-Z]/.test(selectedText)) {

                    currentSelectedWord = selectedText;

                    let paragraphText = selection.anchorNode.textContent || "";
                    let textIndex = paragraphText.indexOf(currentSelectedWord);

                    // Беремо 50 символів ліворуч та праворуч від фрази для контексту
                    if (textIndex !== -1) {
                        let start = Math.max(0, textIndex - 50);
                        let end = Math.min(paragraphText.length, textIndex + currentSelectedWord.length + 50);
                        currentExampleSentence = "..." + paragraphText.substring(start, end).trim() + "...";
                    } else {
                        currentExampleSentence = currentSelectedWord;
                    }

                    if (currentExampleSentence.length > 255) {
                        currentExampleSentence = currentExampleSentence.substring(0, 252) + "...";
                    }

                    document.getElementById('selected-word').textContent = currentSelectedWord;
                    document.getElementById('empty-state').style.display = 'none';
                    document.getElementById('word-action-state').style.display = 'block';
                    document.getElementById('translated-word').innerHTML = '<span class="spinner-border spinner-border-sm text-primary"></span>';

                    // Скидаємо стан кнопки перед новим запитом
                    const srsBtn = document.getElementById('add-to-srs-btn');
                    if (srsBtn) {
                        srsBtn.innerHTML = '<i class="bi bi-plus-circle me-2"></i>Додати у картки';
                        srsBtn.className = 'btn btn-primary w-100 fw-bold';
                        srsBtn.disabled = false;
                    }

                    fetchWithAuth(translateUrl, {
                        method: 'POST',
                        body: JSON.stringify({word: currentSelectedWord})
                    })
                    .then(res => res.json())
                    .then(data => {
                        currentTranslation = data.translation;
                        document.getElementById('translated-word').textContent = data.translation || 'Не знайдено';

                        if (srsBtn) {
                            if (data.is_in_flashcards) {
                                srsBtn.innerHTML = '<i class="bi bi-info-circle me-2"></i>Вже в картках';
                                srsBtn.className = 'btn btn-secondary w-100 fw-bold';
                                srsBtn.disabled = true;
                            } else {
                                srsBtn.innerHTML = '<i class="bi bi-plus-circle me-2"></i>Додати у картки';
                                srsBtn.className = 'btn btn-primary w-100 fw-bold';
                                srsBtn.disabled = false;
                            }
                        }
                    });
                }
            }, 150);
        }

        // Вішаємо слухачів на ПК (mouseup) та на смартфони (touchend)
        articleTextContainer.addEventListener('mouseup', handleTextSelection);
        articleTextContainer.addEventListener('touchend', handleTextSelection);


        const addToSrsBtn = document.getElementById('add-to-srs-btn');
        if (addToSrsBtn) {
            addToSrsBtn.addEventListener('click', function() {
                if (!currentSelectedWord) return;

                const btn = this;
                const originalHtml = btn.innerHTML;

                btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>...';
                btn.disabled = true;

                const categoryId = articleTextContainer.getAttribute('data-category-id');

                fetchWithAuth('/flashcards/api/v1/cards/add-custom-word/', {
                    method: 'POST',
                    body: JSON.stringify({
                        english_word: currentSelectedWord,
                        translation: currentTranslation,
                        level: document.getElementById('article-level').innerText || "A1",
                        example: currentExampleSentence,
                        category_id: parseInt(categoryId)
                    })
                })
                .then(async res => {
                    if (res.ok) {
                        const data = await res.json();

                        if (data.status === 'success') {
                            btn.innerHTML = '<i class="bi bi-check2 me-2"></i>Додано!';
                            btn.className = 'btn btn-success w-100 fw-bold';
                        } else {
                            btn.innerHTML = '<i class="bi bi-info-circle me-2"></i>Вже в картках';
                            btn.className = 'btn btn-secondary w-100 fw-bold';
                        }
                    } else {
                        btn.innerHTML = '<i class="bi bi-x-circle me-2"></i>Помилка';
                        btn.className = 'btn btn-danger w-100 fw-bold';

                        setTimeout(() => {
                            btn.innerHTML = originalHtml;
                            btn.className = 'btn btn-primary w-100 fw-bold';
                            btn.disabled = false;
                        }, 2500);
                    }
                })
                .catch(err => {
                    btn.innerHTML = 'Помилка мережі!';
                    setTimeout(() => {
                        btn.innerHTML = originalHtml;
                        btn.className = 'btn btn-primary w-100 fw-bold';
                        btn.disabled = false;
                    }, 2000);
                });
            });
        }
    }
});