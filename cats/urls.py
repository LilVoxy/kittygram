from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import AchievementViewSet, CatViewSet, UserViewSet

router = DefaultRouter()
router.register('cats', CatViewSet)
router.register('users', UserViewSet)
router.register('achievements', AchievementViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
