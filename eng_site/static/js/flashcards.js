/**
 * @fileoverview Flashcards Training Module (SRS)
 * Manages the client-side state for the spaced repetition system, including
 * fetching batches of cards, rendering UI states, and syncing reviews with the API.
 */

document.addEventListener("DOMContentLoaded", function () {
    const loadingArea = document.getElementById('loading-area');
    const trainingArea = document.getElementById('training-area');
    const successArea = document.getElementById('success-area');

    // Ensure we are on the training page
    if (!trainingArea) return;

    // UI Elements
    const cardsLeftEl = document.getElementById('cards-left');
    const btnShowAnswer = document.getElementById('show-answer-btn');
    const cardBack = document.getElementById('card-back');
    const srsControls = document.getElementById('srs-controls');
    const btnSpeak = document.getElementById('btn-speak');

    // State Management
    let cards = [];
    let currentIndex = 0;
    let totalCardsLeft = 0;
    let isFetchingNextBatch = false;

    // Initialize application state
    fetchTrainingSession();

    /**
     * Fetches the next batch of due flashcards from the API.
     */
    async function fetchTrainingSession() {
        try {
            const response = await fetchWithAuth('/flashcards/api/v1/cards/training-session/');
            const data = await response.json();

            if (response.ok) {
                cards = data.cards_to_review || [];
                totalCardsLeft = data.cards_left || 0;
                currentIndex = 0;

                loadingArea.classList.add('d-none');

                if (cards.length > 0) {
                    trainingArea.classList.remove('d-none');
                    renderCurrentCard();
                } else {
                    showSuccessScreen();
                }
            } else {
                showError("Не вдалося завантажити сесію. Спробуйте пізніше.");
            }
        } catch (error) {
            console.error("API Error [fetchTrainingSession]:", error);
            showError("Помилка мережі. Перевірте з'єднання.");
        }
    }

    /**
     * Renders the current flashcard data into the DOM.
     * Triggers batch refetch if the current batch is exhausted.
     */
    function renderCurrentCard() {
        if (currentIndex >= cards.length) {
            if (totalCardsLeft > 0 && !isFetchingNextBatch) {
                isFetchingNextBatch = true;
                trainingArea.classList.add('d-none');
                loadingArea.classList.remove('d-none');

                // Fetch next chunk and reset flag
                fetchTrainingSession().finally(() => {
                    isFetchingNextBatch = false;
                });
            } else {
                showSuccessScreen();
            }
            return;
        }

        const card = cards[currentIndex];

        // Populate DOM nodes
        document.getElementById('word-category').innerText = card.category || 'Слово';
        document.getElementById('english-word').innerText = card.english_word;
        document.getElementById('ukrainian-translation').innerText = card.translation;
        document.getElementById('example-sentence').innerText = card.example ? `"${card.example}"` : "";
        cardsLeftEl.innerText = totalCardsLeft;

        // Reset UI state for the new card
        cardBack.style.display = 'none';
        cardBack.classList.remove('fade-in');
        srsControls.style.display = 'none';
        srsControls.classList.remove('fade-in');
        btnShowAnswer.style.display = 'block';
    }

    // Event Listeners
    btnShowAnswer.addEventListener('click', function () {
        btnShowAnswer.style.display = 'none';
        cardBack.style.display = 'block';
        cardBack.classList.add('fade-in');
        srsControls.style.display = 'block';
        srsControls.classList.add('fade-in');
    });

    btnSpeak.addEventListener('click', function () {
        const word = cards[currentIndex]?.english_word;
        if (word) {
            const utterance = new SpeechSynthesisUtterance(word);
            utterance.lang = 'en-US';
            window.speechSynthesis.speak(utterance);
        }
    });

    // SRS Review submission logic
    document.querySelectorAll('.srs-btn').forEach(btn => {
        btn.addEventListener('click', async function () {
            const quality = this.getAttribute('data-quality');
            const currentCard = cards[currentIndex];

            // Optimistic UI update: disable buttons to prevent rapid multi-clicks
            const allSrsBtns = document.querySelectorAll('.srs-btn');
            allSrsBtns.forEach(b => b.disabled = true);

            try {
                // Fire-and-forget API request (doesn't block UI progression)
                fetchWithAuth(`/flashcards/api/v1/cards/${currentCard.id}/review/`, {
                    method: 'POST',
                    body: JSON.stringify({ quality: quality })
                });
            } catch (error) {
                console.error("Failed to sync review:", error);
            }

            // Restore button states for the next card
            allSrsBtns.forEach(b => b.disabled = false);

            // Progress state
            currentIndex++;
            if (quality !== 'again') {
                totalCardsLeft--;
            }
            renderCurrentCard();
        });
    });

    /**
     * UI State transitions
     */
    function showSuccessScreen() {
        trainingArea.classList.add('d-none');
        loadingArea.classList.add('d-none');
        successArea.classList.remove('d-none');
    }

    function showError(msg) {
        loadingArea.innerHTML = `<p class="text-danger fs-5">${msg}</p>`;
    }
});