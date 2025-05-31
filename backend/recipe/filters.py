import django_filters
from .models import MeRecipe, MeCategory

class RecipeFilter(django_filters.FilterSet):
    """Фильтр для рецептов"""
    tags = django_filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=MeCategory.objects.all()
    )
    author = django_filters.NumberFilter(field_name='author__id')
    
    class Meta:
        model = MeRecipe
        fields = ['tags', 'author']