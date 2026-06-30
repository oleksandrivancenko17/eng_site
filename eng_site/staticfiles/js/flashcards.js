document.addEventListener("DOMContentLoaded", function() {
    const cardsDataElement = document.getElementById('cards-data');
    if (!cardsDataElement) return;

    const cards = JSON.parse(cardsDataElement.textContent);
    let currentIndex = 0;

    const cardsLeftEl = document.getElementById('cards-left');
    let totalCardsLeft = parseInt(cardsLeftEl.innerText);
    const trainingArea = document.getElementById('training-area');
    const dictUrl = trainingArea.getAttribute('data-dict-url');

    const btnShowAnswer = document.getElementById('show-answer-btn');
    const cardBack = document.getElementById('card-back');
    const srsControls = document.getElementById('srs-controls');

    function loadCurrentCard() {
        if (currentIndex >= cards.length) {
            if (totalCardsLeft > 0) {
                location.reload();
            } else {
                showSuccessScreen();
            }
            return;
        }

        const card = cards[currentIndex];
        document.getElementById('word-category').innerText = card.category;
        document.getElementById('english-word').innerText = card.english_word;
        document.getElementById('ukrainian-translation').innerText = card.translation;
        document.getElementById('example-sentence').innerText = card.example ? `"${card.example}"` : "";
        cardsLeftEl.innerText = totalCardsLeft;

        cardBack.style.display = 'none';
        cardBack.classList.remove('fade-in');
        srsControls.style.display = 'none';
        srsControls.classList.remove('fade-in');
        btnShowAnswer.style.display = 'block';
    }

    window.nextCard = function(quality) {
        const currentCard = cards[currentIndex];
        const url = `/flashcards/review/${currentCard.id}/`;

        fetch(url, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({'quality': quality})
        });

        currentIndex++;
        if (quality !== 'again') {
            totalCardsLeft--;
        }
        loadCurrentCard();
    };

    window.showAnswer = function() {
        btnShowAnswer.style.display = 'none';
        cardBack.style.display = 'block';
        cardBack.classList.add('fade-in');
        srsControls.style.display = 'block';
        srsControls.classList.add('fade-in');
    };

    window.speakWord = function() {
        const word = cards[currentIndex].english_word;
        const msg = new SpeechSynthesisUtterance(word);
        msg.lang = 'en-US';
        window.speechSynthesis.speak(msg);
    };

    function showSuccessScreen() {
        trainingArea.innerHTML = `
        <div class="col-md-8 col-lg-6 text-center py-5">
            <div class="display-1 text-success mb-4"><i class="bi bi-check-circle-fill"></i></div>
            <h2 class="fw-bold">Чудова робота!</h2>
            <p class="text-muted fs-5">Ти повторив усі слова на сьогодні.</p>
            <a href="${dictUrl}" class="btn btn-primary btn-lg mt-3 px-5">До словника</a>
        </div>`;
    }

    if (cards.length > 0) {
        loadCurrentCard();
    }
});