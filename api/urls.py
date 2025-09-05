from django.urls import path, include
from rest_framework_nested import routers

from users.views import UserViewSet
from posts.views import PostViewSet, CommentViewSet, initiate_payment
from relationships.views import FollowViewSet


router = routers.DefaultRouter()

router.register("users", UserViewSet, basename="users")
router.register("posts", PostViewSet, basename="posts")
router.register("comments", CommentViewSet, basename="comments")
router.register("follows", FollowViewSet, basename="follows")

posts_router = routers.NestedDefaultRouter(router, "posts", lookup="post")
posts_router.register("comments", CommentViewSet, basename="post-comments")


urlpatterns = [
    path("", include(router.urls)),
    path("", include(posts_router.urls)),
    #
    path("auth/", include("djoser.urls")),
    path("auth/", include("djoser.urls.jwt")),
    #
    path("payment/initiate", initiate_payment, name="initiate-payment"),
]
