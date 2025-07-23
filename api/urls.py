from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers


router = routers.DefaultRouter()  # ----> Api Root a error day na...link day...


urlpatterns = [
    path("", include(router.urls)),
    # path
]
