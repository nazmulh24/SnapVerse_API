from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from api.paginations import FollowPagination
from relationships.models import Follow
from relationships.serializers import (
    FollowSerializer,
    FollowActionRequestSerializer,
    FollowStatsSerializer,
    PendingRequestActionSerializer,
)

User = get_user_model()


class FollowViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Social connections and follow system management.

    Handles following/unfollowing users, managing follow requests,
    and retrieving social connection data with privacy controls.
    """

    queryset = Follow.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = FollowPagination

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ["approve_request", "reject_request"]:
            permission_classes = [
                IsAuthenticated
            ]  # --> Only request recipient can approve/reject
        elif self.action in ["follow_user", "unfollow_user"]:
            permission_classes = [
                IsAuthenticated
            ]  # --> Only authenticated users can follow
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action in ["follow_user", "unfollow_user"]:
            return FollowActionRequestSerializer
        elif self.action == "list":
            return FollowStatsSerializer
        elif self.action == "pending_requests" and self.request.method == "POST":
            return PendingRequestActionSerializer
        elif self.action in ["following", "followers", "pending_requests"]:
            return FollowSerializer
        return FollowSerializer

    def get_queryset(self):
        user = self.request.user

        if self.action == "following":
            return Follow.objects.filter(
                follower=user, is_approved=True
            ).select_related("follower", "following")

        elif self.action == "followers":
            return Follow.objects.filter(
                following=user, is_approved=True
            ).select_related("follower", "following")

        elif self.action == "pending_requests":
            return Follow.objects.filter(
                following=user, is_approved=False
            ).select_related("follower", "following")

        return Follow.objects.none()

    @swagger_auto_schema(
        operation_summary="Get Follow Statistics",
        operation_description="Retrieve current user's follow statistics",
        responses={200: FollowStatsSerializer},
        tags=["Relationships"],
    )
    def list(self, request):
        """Get follow statistics for the current user"""
        user = request.user

        followers_count = Follow.objects.filter(
            following=user, is_approved=True
        ).count()
        following_count = Follow.objects.filter(follower=user, is_approved=True).count()
        pending_requests_count = Follow.objects.filter(
            following=user, is_approved=False
        ).count()

        stats_data = {
            "followers_count": followers_count,
            "following_count": following_count,
            "pending_requests_count": pending_requests_count,
        }

        serializer = self.get_serializer(stats_data)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Follow User",
        operation_description="Follow a user or send follow request for private accounts",
        request_body=FollowActionRequestSerializer,
        responses={201: "Follow successful", 400: "Bad request", 404: "User not found"},
        tags=["Relationships"],
    )
    @action(detail=False, methods=["post"])
    def follow_user(self, request):
        """Follow a user - instantly for public users, request for private users"""
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user_id = serializer.validated_data["user_id"]

        try:
            user_to_follow = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )

        if user_to_follow == request.user:
            return Response(
                {"error": "You cannot follow yourself"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        follow, created = Follow.objects.get_or_create(
            follower=request.user, following=user_to_follow
        )

        # --> Prepare response data with clear user ID and pending status
        response_data = {
            "success": True,
            "user": {
                "id": user_to_follow.id,
                "username": user_to_follow.username,
                "full_name": user_to_follow.get_full_name(),
                "is_private": user_to_follow.is_private,
            },
            "follow_id": follow.id,
            "is_pending": not follow.is_approved,
            "is_approved": follow.is_approved,
            "status": "pending" if not follow.is_approved else "following",
        }

        if created:
            response_data["message"] = (
                "Follow request sent (pending approval)"
                if not follow.is_approved
                else "Successfully followed user"
            )
            return Response(response_data, status=status.HTTP_201_CREATED)
        else:
            response_data["message"] = (
                "Already following this user"
                if follow.is_approved
                else "Follow request already sent (still pending)"
            )
            return Response(response_data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="Unfollow User",
        operation_description="Remove follow relationship with a user",
        request_body=FollowActionRequestSerializer,
        responses={
            200: "Unfollow successful",
            400: "Bad request",
            404: "User not found",
        },
        tags=["Relationships"],
    )
    @action(detail=False, methods=["post"])
    def unfollow_user(self, request):
        """Unfollow a user"""
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user_id = serializer.validated_data["user_id"]

        try:
            user_to_unfollow = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )

        try:
            follow = Follow.objects.get(
                follower=request.user, following=user_to_unfollow
            )
            follow.delete()
            return Response(
                {
                    "success": True,
                    "message": "Successfully unfollowed user",
                    "user_id": user_to_unfollow.id,
                    "user": {
                        "id": user_to_unfollow.id,
                        "username": user_to_unfollow.username,
                        "first_name": user_to_unfollow.first_name,
                        "last_name": user_to_unfollow.last_name,
                    },
                },
                status=status.HTTP_200_OK,
            )
        except Follow.DoesNotExist:
            return Response(
                {"error": "You are not following this user"},
                status=status.HTTP_404_NOT_FOUND,
            )

    @swagger_auto_schema(
        operation_summary="Get Following List",
        operation_description="Retrieve list of users the current user is following",
        manual_parameters=[
            openapi.Parameter(
                "page",
                openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                description="Page number",
            ),
        ],
        responses={200: FollowSerializer(many=True)},
        tags=["Relationships"],
    )
    @action(detail=False, methods=["get"])
    def following(self, request):
        """Get list of users that the current user is following"""
        following = self.get_queryset()

        # --> Apply pagination
        page = self.paginate_queryset(following)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(following, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Get Followers List",
        operation_description="Retrieve list of users following the current user",
        manual_parameters=[
            openapi.Parameter(
                "page",
                openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                description="Page number",
            ),
        ],
        responses={200: FollowSerializer(many=True)},
        tags=["Relationships"],
    )
    @action(detail=False, methods=["get"])
    def followers(self, request):
        """Get list of users following the current user"""
        followers = self.get_queryset()

        # --> Apply pagination
        page = self.paginate_queryset(followers)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(followers, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        methods=["get"],
        operation_summary="Get Pending Requests",
        operation_description="Retrieve pending follow requests",
        manual_parameters=[
            openapi.Parameter(
                "page",
                openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                description="Page number",
            ),
        ],
        responses={200: FollowSerializer(many=True)},
        tags=["Relationships"],
    )
    @swagger_auto_schema(
        methods=["post"],
        operation_summary="Handle Follow Request",
        operation_description="Approve or reject a follow request",
        request_body=PendingRequestActionSerializer,
        responses={
            200: "Request handled",
            400: "Bad request",
            404: "Request not found",
        },
        tags=["Relationships"],
    )
    @action(detail=False, methods=["get", "post"])
    def pending_requests(self, request):
        """Get pending follow requests or handle approve/reject actions"""

        if request.method == "POST":
            # --> Handle POST request for approve/reject
            serializer = PendingRequestActionSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            request_id = serializer.validated_data["id"]
            action = serializer.validated_data["action"]

            # --> Get the follow request
            try:
                follow = Follow.objects.get(
                    pk=request_id, following=request.user, is_approved=False
                )
            except Follow.DoesNotExist:
                return Response(
                    {"error": "Follow request not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # --> Perform the action
            if action == "Approve":
                follow.approve()
                return Response(
                    {"message": "Follow request approved successfully"},
                    status=status.HTTP_200_OK,
                )
            else:
                follow.delete()
                return Response(
                    {"message": "Follow request rejected successfully"},
                    status=status.HTTP_200_OK,
                )

        else:
            # --> Handle GET request - original functionality
            pending = self.get_queryset()

            # --> Apply pagination
            page = self.paginate_queryset(pending)
            if page is not None:
                serializer = self.get_serializer(
                    page, many=True, context={"request": request}
                )
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(
                pending, many=True, context={"request": request}
            )
            return Response(serializer.data)
