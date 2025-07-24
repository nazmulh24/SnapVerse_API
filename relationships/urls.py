from django.urls import path, include
from rest_framework_nested import routers
from .views import FollowViewSet

router = routers.DefaultRouter()
router.register("follows", FollowViewSet, basename="follows")

urlpatterns = [
    path("", include(router.urls)),
]
