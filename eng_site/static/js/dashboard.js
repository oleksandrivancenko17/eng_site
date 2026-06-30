/**
 * @fileoverview Dashboard SPA Controller.
 * Fetches user statistics using JWT authentication and populates the dashboard UI.
 */

document.addEventListener('DOMContentLoaded', async function () {
    const statCardsReview = document.getElementById('stat-cards-review');
    const statTotalWords = document.getElementById('stat-total-words');
    const statStreak = document.getElementById('stat-streak');

    if (!statCardsReview) return;

    try {
        const response = await fetchWithAuth('/api/v1/dashboard/stats/');

        if (response.ok) {
            const data = await response.json();

            statCardsReview.innerText = data.cards_to_review || 0;
            statTotalWords.innerText = data.total_words || 0;
            statStreak.innerText = data.streak_days || 0;
        } else if (response.status === 401) {
            // Правильний редирект
            window.location.href = '/users/login/';
        } else {
            setFallbackValues('-');
        }
    } catch (error) {
        console.error("API Error [Dashboard Stats]:", error);
        setFallbackValues('!');
    }

    function setFallbackValues(val) {
        statCardsReview.innerText = val;
        statTotalWords.innerText = val;
        statStreak.innerText = val;
    }
});