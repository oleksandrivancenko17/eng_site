document.addEventListener("DOMContentLoaded", function () {

    const topicsContainer = document.getElementById('topics-container');
    const filterSelect = document.getElementById('level-filter');

    if (topicsContainer) {
        let allTopics = [];

        fetchTopics();

        async function fetchTopics() {
            try {
                const response = await fetchWithAuth('/grammar/api/v1/topics/');
                if (response.ok) {
                    const data = await response.json();
                    allTopics = data.results || data;
                    renderTopics(allTopics);
                } else {
                    showError("Не вдалося завантажити теми.");
                }
            } catch (error) {
                console.error("Помилка завантаження тем:", error);
                showError("Помилка мережі.");
            }
        }

        function renderTopics(topics) {
            topicsContainer.innerHTML = '';

            if (topics.length === 0) {
                topicsContainer.innerHTML = `<div class="col-12 text-center mt-5"><h4 class="text-muted">Теми ще не додані.</h4></div>`;
                return;
            }

            const bgClasses = ['bg-tenses', 'bg-articles', 'bg-modals'];
            const iconClasses = ['bi-hourglass-split', 'bi-fonts', 'bi-chat-quote'];

            topics.forEach((topic, index) => {
                const bgClass = bgClasses[index % bgClasses.length];
                const iconClass = iconClasses[index % iconClasses.length];
                const badgeColor = (topic.level === 'A1' || topic.level === 'A2') ? 'bg-success' : ((topic.level === 'B1' || topic.level === 'B2') ? 'bg-primary' : 'bg-danger');

                const hasScore = topic.score !== null && topic.score !== undefined;
                const percentage = hasScore ? Math.round((topic.score / topic.total_questions) * 100) : 0;
                const borderClass = hasScore ? (percentage >= 80 ? 'border-success border-opacity-50' : 'border-warning border-opacity-50') : '';

                let progressHtml = `<div class="mt-auto"></div>`;
                let btnHtml = `<a href="/grammar/test/${topic.id}/" class="btn btn-sm px-3 btn-primary">Почати тест</a>`;

                if (hasScore) {
                    progressHtml = `
                        <div class="mb-3 mt-auto">
                            <div class="d-flex justify-content-between small mb-1">
                                ${percentage >= 80 
                                    ? `<span class="text-success fw-bold"><i class="bi bi-check-circle-fill me-1"></i>Пройдено</span>` 
                                    : `<span class="text-warning text-dark fw-bold"><i class="bi bi-exclamation-circle-fill me-1"></i>Потребує повторення</span>`}
                                <span class="fw-bold">${topic.score}/${topic.total_questions}</span>
                            </div>
                            <div class="progress" style="height: 6px;">
                                <div class="progress-bar ${percentage >= 80 ? 'bg-success' : 'bg-warning'}" role="progressbar" style="width: ${percentage}%;"></div>
                            </div>
                        </div>`;

                    btnHtml = `<a href="/grammar/test/${topic.id}/" class="btn btn-sm px-3 ${percentage >= 80 ? 'btn-outline-secondary' : 'btn-warning'}">${percentage >= 80 ? 'Пройти знову' : 'Покращити результат'}</a>`;
                }

                const cardHtml = `
                    <div class="col-md-6 col-lg-4 topic-item" data-level="${topic.level}">
                        <div class="card topic-card shadow-sm h-100 border ${borderClass}">
                            <div class="card-body d-flex flex-column">
                                <div class="d-flex justify-content-between align-items-start mb-3">
                                    <div class="icon-wrapper ${bgClass}"><i class="bi ${iconClass}"></i></div>
                                    <span class="badge ${badgeColor}">${topic.level}</span>
                                </div>
                                <h5 class="card-title fw-bold">${topic.title}</h5>
                                <p class="card-text text-muted small mb-4">${topic.theory ? topic.theory.substring(0, 80) + '...' : ''}</p>
                                ${progressHtml}
                                <div class="d-flex justify-content-between align-items-center ${!hasScore ? 'mt-auto' : 'mt-3'}">
                                    <span class="text-muted small"><i class="bi bi-list-ol me-1"></i> ${topic.total_questions || 0} питань</span>
                                    ${btnHtml}
                                </div>
                            </div>
                        </div>
                    </div>`;
                topicsContainer.insertAdjacentHTML('beforeend', cardHtml);
            });
        }

        function showError(msg) {
            topicsContainer.innerHTML = `<div class="col-12 text-center py-5 text-danger">${msg}</div>`;
        }

        if (filterSelect) {
            filterSelect.addEventListener('change', function () {
                const selectedLevel = this.value;
                const cards = document.querySelectorAll('.topic-item');

                cards.forEach(card => {
                    const cardLevel = card.getAttribute('data-level');
                    if (selectedLevel === 'all' || cardLevel.startsWith(selectedLevel)) {
                        card.style.display = 'block';
                    } else {
                        card.style.display = 'none';
                    }
                });
            });
        }
    }

    const quizCard = document.getElementById('quiz-card');
    if (quizCard) {
        let quizData = [];
        let totalQuestions = 0;
        let currentQuestionIndex = 0;
        let score = 0;

        const pathMatch = window.location.pathname.match(/\/grammar\/test\/(\d+)/);
        const topicId = pathMatch ? pathMatch[1] : null;

        if (topicId) {
            fetchQuizData(topicId);
        } else {
            document.getElementById('question-text').innerText = "Тест не знайдено.";
            quizCard.style.display = 'block';
        }

        async function fetchQuizData(id) {
            try {
                const response = await fetchWithAuth(`/grammar/api/v1/topics/${id}/`);

                if (response.ok) {
                    const data = await response.json();
                    const topic = data;
                    quizData = data.questions || [];

                    document.getElementById('topic-title').innerText = topic.title;
                    document.getElementById('topic-level').innerText = topic.level;
                    document.getElementById('topic-level').classList.remove('placeholder-glow');

                    totalQuestions = quizData.length;
                    document.getElementById('total-score').innerText = totalQuestions;

                    quizCard.style.display = 'block';
                    loadQuestion();
                } else {
                    document.getElementById('question-text').innerText = "Не вдалося завантажити тест.";
                    quizCard.style.display = 'block';
                }
            } catch (error) {
                console.error("API Error:", error);
            }
        }

        function loadQuestion() {
            if (!quizData || quizData.length === 0) return;

            const q = quizData[currentQuestionIndex];
            document.getElementById('question-text').innerHTML = q.text.replace('___', '<span class="text-primary fw-bold">________</span>');

            const optionsContainer = document.getElementById('options-container');
            optionsContainer.innerHTML = '';

            q.answers.forEach((answer) => {
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
            document.getElementById('progress-bar').style.width = `${((currentQuestionIndex) / totalQuestions) * 100}%`;

            if (currentQuestionIndex === totalQuestions - 1) {
                const nextBtn = document.getElementById('next-btn');
                nextBtn.innerHTML = 'Завершити <i class="bi bi-check2-circle ms-2"></i>';
                nextBtn.classList.replace('btn-primary', 'btn-success');
            }
        }

        document.getElementById('next-btn')?.addEventListener('click', function() {
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

            fetchWithAuth(`/grammar/api/v1/topics/${topicId}/save_progress/`, {
                method: 'POST',
                body: JSON.stringify({ score: score })
            }).catch(e => console.error("Не вдалося зберегти прогрес:", e));
        }
    }
});