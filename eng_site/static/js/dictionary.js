function addToMyWords(button, wordId) {
    const url = `/flashcards/add/${wordId}/`;

    fetch(url, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success' || data.status === 'info') {
            const badgeText = data.status === 'success' ? 'Додано' : 'Вже вчу';
            button.outerHTML = `
                <span class="badge bg-success bg-opacity-10 text-success border border-success px-3 py-2 rounded-pill fade-in">
                    <i class="bi bi-check-circle me-1"></i> ${badgeText}
                </span>
            `;
        } else {
            alert("Помилка: " + data.message);
        }
    })
    .catch(error => console.error('Помилка fetch:', error));
}