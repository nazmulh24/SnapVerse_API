from django.urls import path, include
from rest_framework_nested import routers

from users.views import UserViewSet
from posts.views import PostViewSet, CommentViewSet
from relationships.views import FollowViewSet


router = routers.DefaultRouter()  # ----> Api Root a error day na...link day...

# User endpoints
router.register("users", UserViewSet, basename="users")

# Post endpoints
router.register("posts", PostViewSet, basename="posts")
router.register("comments", CommentViewSet, basename="comments")

# Follow endpoints
router.register("follows", FollowViewSet, basename="follows")

# Nested router for post comments
posts_router = routers.NestedDefaultRouter(router, "posts", lookup="post")
posts_router.register("comments", CommentViewSet, basename="post-comments")


urlpatterns = [
    path("", include(router.urls)),
    path("", include(posts_router.urls)),
    # Authentication
    path("auth/", include("djoser.urls")),
    path("auth/", include("djoser.urls.jwt")),
]
