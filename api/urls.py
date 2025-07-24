from django.urls import path, include
from rest_framework_nested import routers

from users.views import UserViewSet


router = routers.DefaultRouter()  # ----> Api Root a error day na...link day...

router.register("users", UserViewSet, basename="users")


urlpatterns = [
    path("", include(router.urls)),
    # path
    path("auth/", include("djoser.urls")),
    path("auth/", include("djoser.urls.jwt")),
]
