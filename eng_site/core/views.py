from django.views.generic import TemplateView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from flashcards.models import UserWord


class DashboardUI(TemplateView):
    """
    SPA Shell for the Dashboard.
    Authentication is handled strictly on the client-side via JWT.
    """
    template_name = 'dashboard.html'


class DashboardStatsAPIView(APIView):
    """
    BFF (Backend For Frontend) endpoint aggregating statistics
    from different apps for the user dashboard.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        now = timezone.now()

        cards_to_review = UserWord.objects.filter(
            user=request.user,
            next_review_date__lte=now
        ).count()

        total_words = UserWord.objects.filter(
            user=request.user
        ).count()

        return Response({
            'cards_to_review': cards_to_review,
            'total_words': total_words,
            'streak_days': request.user.current_streak
        })