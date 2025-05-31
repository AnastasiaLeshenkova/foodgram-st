from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MeUserViewSet

router = DefaultRouter()
router.register(r'users', MeUserViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),
]