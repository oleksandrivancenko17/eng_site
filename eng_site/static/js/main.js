document.addEventListener('DOMContentLoaded', function() {

    // ==========================================
    // ЛОГІКА ДЛЯ КАРТОК SRS
    // ==========================================
    const btnShowAnswer = document.getElementById('show-answer-btn');
    const cardBack = document.getElementById('card-back');
    const srsControls = document.getElementById('srs-controls');
    let cardsLeft = 15;

    // Робимо функцію глобальною, щоб вона працювала з onclick в HTML
    window.showAnswer = function() {
        if (btnShowAnswer) {
            btnShowAnswer.style.display = 'none';
            cardBack.style.display = 'block';
            cardBack.classList.add('fade-in');
            srsControls.style.display = 'block';
            srsControls.classList.add('fade-in');
        }
    };

    window.nextCard = function(quality) {
        console.log(`Відправляємо на сервер: оцінка = ${quality}`);
        cardsLeft--;

        const cardsLeftEl = document.getElementById('cards-left');
        if (cardsLeftEl) cardsLeftEl.innerText = cardsLeft;

        if (cardsLeft > 0) {
            loadNextWordUI();
        } else {
            document.querySelector('.row.justify-content-center').innerHTML = `
                <div class="col-md-8 col-lg-6 text-center py-5">
                    <div class="display-1 text-success mb-4"><i class="bi bi-check-circle-fill"></i></div>
                    <h2 class="fw-bold">Чудова робота!</h2>
                    <p class="text-muted fs-5">Ти повторив усі слова на сьогодні.</p>
                    <a href="#" class="btn btn-primary btn-lg mt-3 px-5">Перейти до читання</a>
                </div>
            `;
        }
    };

    function loadNextWordUI() {
        cardBack.style.display = 'none';
        cardBack.classList.remove('fade-in');
        srsControls.style.display = 'none';
        srsControls.classList.remove('fade-in');
        btnShowAnswer.style.display = 'block';

        document.getElementById('english-word').innerText = "Inquisitive";
        document.getElementById('ukrainian-translation').innerText = "Допитливий";
        document.getElementById('example-sentence').innerText = '"He is a very inquisitive child..."';
    }


    // ==========================================
    // ЛОГІКА ДЛЯ ТЕСТІВ З ГРАМАТИКИ
    // ==========================================
    window.checkAnswer = function(selectedButton) {
        const allButtons = document.querySelectorAll('.option-btn');
        const isCorrect = selectedButton.getAttribute('data-correct') === 'true';

        allButtons.forEach(btn => {
            btn.disabled = true;
            if (btn.getAttribute('data-correct') === 'true') {
                btn.classList.add('correct');
            }
        });

        if (!isCorrect) {
            selectedButton.classList.add('incorrect');
        }

        const expBox = document.getElementById('explanation-box');
        if (expBox) {
            expBox.style.display = 'block';
            expBox.style.borderLeftColor = isCorrect ? '#198754' : '#dc3545';
        }

        const nextBtn = document.getElementById('next-btn');
        if (nextBtn) nextBtn.style.display = 'inline-block';
    };

    window.nextQuestion = function() {
        alert("Тут бекенд має відрендерити наступне питання.");
    };


    // ==========================================
    // ЛОГІКА ДЛЯ ЧИТАННЯ (Переклад виділеного тексту)
    // ==========================================
    const articleText = document.getElementById('article-text');
    if (articleText) {
        const emptyState = document.getElementById('empty-state');
        const wordActionState = document.getElementById('word-action-state');
        const selectedWordEl = document.getElementById('selected-word');
        const translatedWordEl = document.getElementById('translated-word');
        const addToSrsBtn = document.getElementById('add-to-srs-btn');
        let currentSelectedWord = "";

        articleText.addEventListener('mouseup', function() {
            let selection = window.getSelection().toString().trim();

            if (selection.length > 0 && /^[a-zA-Z\s\-]+$/.test(selection)) {
                currentSelectedWord = selection.split(' ')[0].toLowerCase();

                selectedWordEl.textContent = currentSelectedWord;
                emptyState.style.display = 'none';
                wordActionState.style.display = 'block';

                translatedWordEl.innerHTML = '<span class="spinner-border spinner-border-sm text-primary" role="status"></span> Шукаємо...';

                setTimeout(() => {
                    translatedWordEl.textContent = "приблизний переклад";
                }, 500);
            } else {
                emptyState.style.display = 'block';
                wordActionState.style.display = 'none';
            }
        });

        if (addToSrsBtn) {
            addToSrsBtn.addEventListener('click', function() {
                if (currentSelectedWord) {
                    console.log("POST запит на бекенд для слова:", currentSelectedWord);
                    this.innerHTML = '<i class="bi bi-check2 me-2"></i>Додано!';
                    this.classList.replace('btn-primary', 'btn-success');

                    setTimeout(() => {
                        this.innerHTML = '<i class="bi bi-plus-circle me-2"></i>Додати у картки';
                        this.classList.replace('btn-success', 'btn-primary');
                    }, 2000);
                }
            });
        }
    }

    // ==========================================
    // ЛОГІКА ДЛЯ СЛОВНИКА
    // ==========================================
    window.addToMyWords = function(button, wordId) {
        console.log(`Відправляємо запит на додавання слова з ID: ${wordId}`);
        const parentTd = button.parentElement;
        parentTd.innerHTML = `
            <span class="badge bg-success bg-opacity-10 text-success border border-success px-3 py-2 rounded-pill fade-in">
                <i class="bi bi-check-circle me-1"></i> Додано
            </span>
        `;
    };

});