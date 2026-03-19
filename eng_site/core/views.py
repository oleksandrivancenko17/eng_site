from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from flashcards.models import UserWord


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        now = timezone.now()

        context['cards_to_review_count'] = UserWord.objects.filter(
            user=self.request.user,
            next_review_date__lte=now
        ).count()

        context['total_words_count'] = UserWord.objects.filter(
            user=self.request.user
        ).count()

        context['streak_days'] = 0

        return context