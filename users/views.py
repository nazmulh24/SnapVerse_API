from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from users.serializers import UserListSerializer, UserProfileSerializer
from api.paginations import UserPagination

from django.db.models import Q
from django.contrib.auth import get_user_model

User = get_user_model()


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for User public operations - GET only"""

    queryset = User.objects.filter(is_active=True)
    pagination_class = UserPagination
    lookup_field = "username"
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == "list":
            return UserListSerializer
        elif self.action == "retrieve":
            return UserProfileSerializer
        return UserProfileSerializer

    def get_queryset(self):
        """Filter queryset for list view with search"""
        queryset = super().get_queryset()

        if self.action == "list":
            search = self.request.query_params.get("search", None)
            if search:
                queryset = queryset.filter(
                    Q(username__icontains=search)
                    | Q(first_name__icontains=search)
                    | Q(last_name__icontains=search)
                    | Q(email__icontains=search)
                )
            return queryset.order_by("username")

        return queryset

    def list(self, request, *args, **kwargs):
        """GET /api/v1/users/ - List all users (public data)"""
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """GET /api/v1/users/<username>/ - Get a user's public profile"""
        return super().retrieve(request, *args, **kwargs)

    @action(detail=True, methods=["get"])
    def posts(self, request, username=None):
        """GET /api/v1/users/<username>/posts/ - Posts by a specific user"""
        user = self.get_object()

        # --> Import here to avoid circular imports
        from posts.models import Post
        from posts.serializers import PostListSerializer

        # --> Check if user can view posts
        if user.is_private and not self._is_following_user(user, request.user):
            return Response(
                {"error": "This account is private. Follow to see their posts."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # --> Get user's posts
        posts = Post.objects.filter(user=user).order_by("-created_at")

        # -->Apply pagination
        page = self.paginate_queryset(posts)
        if page is not None:
            serializer = PostListSerializer(
                page, many=True, context={"request": request}
            )
            return self.get_paginated_response(serializer.data)

        serializer = PostListSerializer(posts, many=True, context={"request": request})
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def followers(self, request, username=None):
        """GET /api/v1/users/<username>/followers/ - Get user's followers list"""
        user = self.get_object()

        # Get approved followers
        followers_relations = user.followers.filter(is_approved=True)
        followers = User.objects.filter(
            id__in=followers_relations.values_list("follower_id", flat=True)
        ).order_by("username")

        # Apply pagination
        page = self.paginate_queryset(followers)
        if page is not None:
            serializer = UserListSerializer(
                page, many=True, context={"request": request}
            )
            return self.get_paginated_response(serializer.data)

        serializer = UserListSerializer(
            followers, many=True, context={"request": request}
        )
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def following(self, request, username=None):
        """GET /api/v1/users/<username>/following/ - Get user's following list"""
        user = self.get_object()

        # Get approved following
        following_relations = user.following.filter(is_approved=True)
        following = User.objects.filter(
            id__in=following_relations.values_list("following_id", flat=True)
        ).order_by("username")

        # Apply pagination
        page = self.paginate_queryset(following)
        if page is not None:
            serializer = UserListSerializer(
                page, many=True, context={"request": request}
            )
            return self.get_paginated_response(serializer.data)

        serializer = UserListSerializer(
            following, many=True, context={"request": request}
        )
        return Response(serializer.data)

    def _is_following_user(self, target_user, request_user):
        """Helper method to check if request_user is following target_user"""
        if not request_user or not request_user.is_authenticated:
            return False

        try:
            from relationships.models import Follow

            follow = Follow.objects.get(follower=request_user, following=target_user)
            return follow.is_approved
        except Follow.DoesNotExist:
            return False
