document.addEventListener('DOMContentLoaded', function () {
    const articleText = document.getElementById('article-text');
    if (!articleText) return;

    const emptyState = document.getElementById('empty-state');
    const wordActionState = document.getElementById('word-action-state');
    const selectedWordEl = document.getElementById('selected-word');
    const translatedWordEl = document.getElementById('translated-word');

    const addToSrsBtn = document.getElementById('add-to-srs-btn');
    const markReadBtn = document.getElementById('mark-read-btn');
    const translationPanel = document.getElementById('translation-panel');
    const translateUrl = translationPanel.getAttribute('data-translate-url');

    let currentSelectedWord = "";
    let currentTranslation = "";
    let currentExample = "";

    articleText.addEventListener('mouseup', function () {
        let selection = window.getSelection();
        let selectedText = selection.toString().trim();

        if (selectedText.length > 0 && /^[a-zA-Z\s\-]+$/.test(selectedText)) {
            currentSelectedWord = selectedText.split(' ')[0].toLowerCase();

            let nodeText = selection.anchorNode.textContent;
            let offset = selection.anchorOffset;

            let start = Math.max(
                nodeText.lastIndexOf('.', offset - 1),
                nodeText.lastIndexOf('!', offset - 1),
                nodeText.lastIndexOf('?', offset - 1)
            );
            start = start < 0 ? 0 : start + 1;

            let ends = [
                nodeText.indexOf('.', offset),
                nodeText.indexOf('!', offset),
                nodeText.indexOf('?', offset)
            ].filter(i => i !== -1);
            let end = ends.length > 0 ? Math.min(...ends) + 1 : nodeText.length;

            currentExample = nodeText.substring(start, end).trim();

            selectedWordEl.textContent = currentSelectedWord;
            emptyState.style.display = 'none';
            wordActionState.style.display = 'block';

            translatedWordEl.innerHTML = '<span class="spinner-border spinner-border-sm text-primary" role="status"></span> Шукаємо...';

            fetch(translateUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({word: currentSelectedWord})
            })
            .then(response => response.json())
            .then(data => {
                if (data.translation) {
                    currentTranslation = data.translation;
                    translatedWordEl.textContent = data.translation;
                } else {
                    translatedWordEl.textContent = "Помилка перекладу";
                }
            })
            .catch(() => {
                translatedWordEl.textContent = "Помилка зв'язку";
            });

        } else {
            emptyState.style.display = 'block';
            wordActionState.style.display = 'none';
        }
    });

    if (addToSrsBtn) {
        addToSrsBtn.addEventListener('click', function () {
            if (currentSelectedWord && currentTranslation) {
                const originalHtml = this.innerHTML;
                this.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status"></span>Зберігаємо...';
                this.disabled = true;

                const addUrl = this.getAttribute('data-url');

                fetch(addUrl, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    body: JSON.stringify({
                        word: currentSelectedWord,
                        translation: currentTranslation,
                        example_usage: currentExample,
                        level: this.dataset.level,
                        category_id: this.dataset.category
                    })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        this.innerHTML = '<i class="bi bi-check2 me-2"></i>Додано!';
                        this.classList.replace('btn-primary', 'btn-success');
                    } else {
                        this.innerHTML = '<i class="bi bi-exclamation-triangle me-2"></i>Помилка';
                        this.classList.replace('btn-primary', 'btn-danger');
                    }

                    setTimeout(() => {
                        this.innerHTML = originalHtml;
                        this.classList.remove('btn-success', 'btn-danger');
                        this.classList.add('btn-primary');
                        this.disabled = false;
                    }, 2000);
                })
                .catch(() => {
                    this.innerHTML = originalHtml;
                    this.disabled = false;
                });
            }
        });
    }

    if (markReadBtn) {
        markReadBtn.addEventListener('click', function () {
            const articleId = this.dataset.articleId;
            const originalContent = this.innerHTML;

            this.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status"></span>Зберігаємо...';
            this.disabled = true;

            fetch(`/library/article/${articleId}/mark-read/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'Content-Type': 'application/json'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    this.innerHTML = '<i class="bi bi-check2-all me-2"></i>Прочитано!';
                    this.classList.replace('btn-success', 'btn-outline-success');
                } else {
                    this.innerHTML = originalContent;
                    this.disabled = false;
                }
            })
            .catch(() => {
                this.innerHTML = originalContent;
                this.disabled = false;
            });
        });
    }
});