import django_filters as filters

from dictionary.models import Word


class WordFilter(filters.FilterSet):
    status = filters.CharFilter(method='filter_by_status')

    class Meta:
        model = Word
        fields = ('category', 'level')

    def filter_by_status(self, queryset, name, value):
        user = self.request.user

        if not user.is_authenticated:
            return queryset

        if value == 'learning':
            return queryset.filter(user_learning__user=user)
        elif value == 'not_learning':
            return queryset.exclude(user_learning__user=user)

        return queryset
