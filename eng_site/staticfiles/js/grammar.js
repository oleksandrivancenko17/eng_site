document.addEventListener("DOMContentLoaded", function() {
    const filterSelect = document.getElementById('level-filter');
    const topicCards = document.querySelectorAll('.topic-item');

    if (filterSelect && topicCards.length > 0) {
        filterSelect.addEventListener('change', function() {
            const selectedLevel = this.value;
            topicCards.forEach(card => {
                const cardLevel = card.getAttribute('data-level');
                if (selectedLevel === 'all' || cardLevel.startsWith(selectedLevel)) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            });
        });
    }

    const quizDataElement = document.getElementById('quiz-data');
    if (!quizDataElement) return;

    let quizData = [];
    let totalQuestions = 0;
    let currentQuestionIndex = 0;
    let score = 0;

    const quizCard = document.getElementById('quiz-card');
    const saveUrl = quizCard.getAttribute('data-save-url');

    try {
        quizData = JSON.parse(JSON.parse(quizDataElement.textContent));
        totalQuestions = quizData.length;
        document.getElementById('total-score').innerText = totalQuestions;
    } catch (e) {
        console.error("Помилка JSON:", e);
    }

    function loadQuestion() {
        if (!quizData || quizData.length === 0) return;

        const q = quizData[currentQuestionIndex];
        document.getElementById('question-text').innerHTML = q.text.replace('___', '<span class="text-primary fw-bold">________</span>');

        const optionsContainer = document.getElementById('options-container');
        optionsContainer.innerHTML = '';

        q.answers.forEach((answer, index) => {
            const btn = document.createElement('button');
            btn.type = 'button';
            btn.className = 'option-btn';
            btn.innerHTML = answer.text;

            btn.onclick = function() {
                const allButtons = optionsContainer.querySelectorAll('.option-btn');
                allButtons.forEach(b => {
                    b.disabled = true;
                    b.style.pointerEvents = 'none';
                });

                if (answer.is_correct) {
                    score++;
                    btn.classList.add('correct');
                } else {
                    btn.classList.add('incorrect');
                    allButtons.forEach((b, i) => {
                        if (q.answers[i].is_correct) {
                            b.classList.add('correct');
                        }
                    });
                }

                const expBox = document.getElementById('explanation-box');
                document.getElementById('explanation-text').innerHTML = q.explanation || "Пояснення відсутнє.";
                expBox.style.display = 'block';
                expBox.style.borderLeftColor = answer.is_correct ? '#198754' : '#dc3545';

                document.getElementById('next-btn').style.display = 'inline-block';
            };

            optionsContainer.appendChild(btn);
        });

        document.getElementById('explanation-box').style.display = 'none';
        document.getElementById('next-btn').style.display = 'none';

        document.getElementById('progress-text').innerText = `Питання ${currentQuestionIndex + 1} з ${totalQuestions}`;
        document.getElementById('progress-bar').style.width = `${(currentQuestionIndex / totalQuestions) * 100}%`;

        if (currentQuestionIndex === totalQuestions - 1) {
            const nextBtn = document.getElementById('next-btn');
            nextBtn.innerHTML = 'Завершити <i class="bi bi-check2-circle ms-2"></i>';
            nextBtn.classList.replace('btn-primary', 'btn-success');
        }
    }

    document.getElementById('next-btn').addEventListener('click', function() {
        currentQuestionIndex++;
        if (currentQuestionIndex < totalQuestions) {
            loadQuestion();
        } else {
            finishQuiz();
        }
    });

    function finishQuiz() {
        document.getElementById('progress-bar').style.width = '100%';
        quizCard.style.display = 'none';

        document.getElementById('final-score').innerText = score;
        document.getElementById('result-card').style.display = 'block';

        fetch(saveUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ 'score': score })
        });
    }

    loadQuestion();
});