from django.http import HttpResponseRedirect
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q

from drf_yasg.utils import swagger_auto_schema

from api.paginations import PostPagination, CommentPagination
from posts.models import Post, Comment, Reaction
from api.permissions import (
    IsOwnerOrReadOnly,
    IsOwnerOrStaff,
    IsCommentOwnerOrStaff,
    IsCommentOwnerOrReadOnly,
    IsCommentOwnerPostOwnerOrAdmin,
    IsPostOwnerOrStaffOrReadOnly,
)
from .serializers import (
    PostCreateSerializer,
    PostDetailSerializer,
    PostUpdateSerializer,
    CommentSerializer,
    CommentWithPostSerializer,
    CommentCreateSerializer,
    CommentTextSerializer,
    CommentReplySerializer,
    ReactionSerializer,
    ReactionCreateSerializer,
)

from sslcommerz_lib import SSLCOMMERZ
from django.conf import settings as main_settings
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model

User = get_user_model()


class PostViewSet(viewsets.ModelViewSet):
    """Post management endpoints for social media content."""

    queryset = Post.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = PostPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["privacy", "user"]
    search_fields = ["caption", "location", "user__username"]
    ordering_fields = ["created_at", "updated_at"]
    ordering = ["-created_at"]
    http_method_names = ["get", "post", "put", "delete"]

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ["update", "partial_update", "destroy"]:
            # Allow owners and staff to edit/delete posts
            permission_classes = [IsAuthenticated, IsOwnerOrStaff]
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == "create":
            return PostCreateSerializer
        elif self.action in ["update", "partial_update"]:
            return PostUpdateSerializer
        elif self.action == "retrieve":
            return PostDetailSerializer
        elif self.action == "react":
            return ReactionCreateSerializer
        elif self.action == "comments":
            return CommentCreateSerializer
        return PostDetailSerializer

    def get_queryset(self):
        """Filter posts based on privacy settings and user permissions"""
        user = self.request.user

        if self.action == "list":
            # Show posts based on privacy settings
            return (
                Post.objects.filter(
                    Q(privacy="public")  # Public posts
                    | Q(user=user)  # User's own posts
                    | Q(
                        privacy="followers", user__followers__follower=user
                    )  # Posts from followed users
                )
                .select_related("user")
                .prefetch_related("reactions", "comments")
                .distinct()  # --> Remove duplicates
            )

        return Post.objects.select_related("user").prefetch_related(
            "reactions", "comments"
        )

    @swagger_auto_schema(
        operation_summary="List Posts",
        operation_description="Get posts with privacy-based filtering and pagination",
        tags=["Posts"],
    )
    def list(self, request, *args, **kwargs):
        """Get personalized social media feed with privacy-based filtering"""
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Update Post", tags=["Posts"])
    def update(self, request, *args, **kwargs):
        """Update a post"""
        return super().update(request, *args, **kwargs)

    def perform_create(self, serializer):
        """Set the user when creating a post"""
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        """Update the post (permission already checked)"""
        serializer.save()

    def perform_destroy(self, instance):
        """Delete the post (permission already checked)"""
        instance.delete()

    @swagger_auto_schema(
        methods=["post"],
        operation_summary="Add Reaction",
        tags=["Posts"],
    )
    @swagger_auto_schema(
        methods=["delete"],
        operation_summary="Remove Reaction",
        tags=["Posts"],
    )
    @action(detail=True, methods=["post", "delete"])
    def react(self, request, pk=None):
        """Handle post reactions - add, update, or remove"""
        post = self.get_object()
        user = request.user

        if request.method == "POST":
            serializer = ReactionCreateSerializer(data=request.data)

            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            reaction_type = serializer.validated_data["reaction"]

            # Check if user already has this reaction (to remove it)
            try:
                existing_reaction = Reaction.objects.get(user=user, post=post)
                if existing_reaction.reaction == reaction_type:
                    # User clicked same reaction - remove it
                    existing_reaction.delete()
                    return Response(
                        {
                            "message": f"Removed {reaction_type} reaction",
                            "action": "removed",
                            "reaction_type": reaction_type,
                        }
                    )
                else:
                    # User changed reaction
                    existing_reaction.reaction = reaction_type
                    existing_reaction.save()
                    return Response(
                        {
                            "message": f"Changed reaction to {reaction_type}",
                            "action": "updated",
                            "reaction_type": reaction_type,
                        }
                    )
            except Reaction.DoesNotExist:
                # Create new reaction
                reaction = Reaction.objects.create(
                    user=user, post=post, reaction=reaction_type
                )
                return Response(
                    {
                        "message": f"Added {reaction_type} reaction",
                        "action": "added",
                        "reaction_type": reaction_type,
                    },
                    status=status.HTTP_201_CREATED,
                )

        elif request.method == "DELETE":
            try:
                reaction = Reaction.objects.get(user=user, post=post)
                reaction_type = reaction.reaction
                reaction.delete()
                return Response(
                    {
                        "message": f"Removed {reaction_type} reaction",
                        "action": "removed",
                    }
                )
            except Reaction.DoesNotExist:
                return Response(
                    {"error": "No reaction found to remove"},
                    status=status.HTTP_404_NOT_FOUND,
                )

    @swagger_auto_schema(
        operation_summary="Get Post Reactions",
        tags=["Posts"],
    )
    @action(detail=True, methods=["get"])
    def reactions(self, request, pk=None):
        """Get all reactions for a post"""
        post = self.get_object()
        reactions = post.reactions.all().order_by("-created_at")

        # Filter by reaction type if provided
        reaction_type = request.query_params.get("type")
        if reaction_type:
            reactions = reactions.filter(reaction=reaction_type)

        serializer = ReactionSerializer(reactions, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        methods=["get"], operation_summary="Get Comments", tags=["Posts"]
    )
    @swagger_auto_schema(
        methods=["post"], operation_summary="Add Comment", tags=["Posts"]
    )
    @action(detail=True, methods=["get", "post"])
    def comments(self, request, pk=None):
        """Get comments for a post or add a new comment"""
        post = self.get_object()

        if request.method == "GET":
            # Get top-level comments only (no replies)
            comments = (
                post.comments.filter(parent_comment=None)
                .select_related("user")
                .prefetch_related("replies")
                .order_by("-created_at")
            )

            # Apply pagination using CommentPagination
            paginator = CommentPagination()
            page = paginator.paginate_queryset(comments, request)
            if page is not None:
                serializer = CommentSerializer(
                    page, many=True, context={"request": request}
                )
                return paginator.get_paginated_response(serializer.data)

            # Fallback if pagination fails
            serializer = CommentSerializer(
                comments, many=True, context={"request": request}
            )
            return Response(serializer.data)

        elif request.method == "POST":
            serializer = CommentCreateSerializer(
                data=request.data, context={"request": request, "view": self}
            )
            if serializer.is_valid():
                comment = serializer.save(user=request.user, post=post)
                response_serializer = CommentSerializer(
                    comment, context={"request": request}
                )
                return Response(
                    response_serializer.data, status=status.HTTP_201_CREATED
                )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary="My Posts",
        tags=["Posts"],
    )
    @action(detail=False, methods=["get"])
    def my_posts(self, request):
        """Get current user's posts with pagination"""
        posts = (
            Post.objects.filter(user=request.user)
            .select_related("user")
            .prefetch_related("reactions", "comments")
            .order_by("-created_at")
        )
        page = self.paginate_queryset(posts)
        serializer = PostDetailSerializer(page, many=True, context={"request": request})
        return self.get_paginated_response(serializer.data)

    @swagger_auto_schema(
        operation_summary="User Feed",
        tags=["Posts"],
    )
    @action(detail=False, methods=["get"])
    def feed(self, request):
        """Get personalized feed for the user with pagination"""
        posts = (
            Post.objects.filter(
                Q(privacy="public")
                | Q(user__followers__follower=request.user)
                | Q(user=request.user)
            )
            .select_related("user")
            .prefetch_related("reactions", "comments")
            .distinct()
            .order_by("-created_at")
        )
        page = self.paginate_queryset(posts)
        serializer = PostDetailSerializer(page, many=True, context={"request": request})
        return self.get_paginated_response(serializer.data)


class CommentViewSet(viewsets.ModelViewSet):
    """Comment management endpoints for post interactions."""

    queryset = (
        Comment.objects.all()
        .select_related("user", "post", "post__user")
        .order_by("-created_at")
    )
    permission_classes = [IsAuthenticated]
    pagination_class = CommentPagination
    http_method_names = ["get", "put", "delete"]

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action == "destroy":
            # Allow comment owner, post owner, or staff to delete comments
            permission_classes = [IsAuthenticated, IsCommentOwnerPostOwnerOrAdmin]
        elif self.action in ["update", "partial_update"]:
            # Allow comment owner or staff to edit comments
            permission_classes = [IsAuthenticated, IsCommentOwnerOrStaff]
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action in ["update", "partial_update"]:
            return CommentTextSerializer
        elif self.action == "list":
            return CommentWithPostSerializer
        return CommentSerializer

    @swagger_auto_schema(operation_summary="Update Comment", tags=["Comments"])
    def update(self, request, *args, **kwargs):
        """Update a comment"""
        return super().update(request, *args, **kwargs)

    def perform_update(self, serializer):
        """Update the comment (permission already checked)"""
        serializer.save()

    def perform_destroy(self, instance):
        """Delete the comment (permission already checked)"""
        instance.delete()

    @swagger_auto_schema(
        methods=["get"],
        operation_summary="Get Replies",
        tags=["Comments"],
    )
    @swagger_auto_schema(
        methods=["post"],
        operation_summary="Add Reply",
        tags=["Comments"],
    )
    @action(detail=True, methods=["get", "post"])
    def replies(self, request, pk=None):
        """Get replies for a comment or add a new reply"""
        parent_comment = self.get_object()

        if request.method == "GET":
            replies = parent_comment.replies.all().order_by("created_at")
            serializer = CommentReplySerializer(
                replies, many=True, context={"request": request}
            )
            return Response(serializer.data)

        elif request.method == "POST":
            serializer = CommentTextSerializer(
                data=request.data, context={"request": request}
            )
            if serializer.is_valid():
                reply = serializer.save(
                    user=request.user,
                    post=parent_comment.post,
                    parent_comment=parent_comment,
                )
                response_serializer = CommentReplySerializer(
                    reply, context={"request": request}
                )
                return Response(
                    response_serializer.data, status=status.HTTP_201_CREATED
                )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def initiate_payment(request):
    """Initiate payment for SnapVerse Pro subscription - 99 BDT for 30 days"""
    user = request.user

    # Fixed amount for pro subscription
    amount = 99
    subscription_type = "pro_monthly"

    from datetime import datetime

    # Create unique transaction ID for pro subscription
    tran_id = f"pro_{user.id}_{int(datetime.now().timestamp())}"

    settings = {
        "store_id": "nazmu689918a6d45d1",
        "store_pass": "nazmu689918a6d45d1@ssl",
        "issandbox": True,
    }

    sslcz = SSLCOMMERZ(settings)
    post_body = {}
    post_body["total_amount"] = amount
    post_body["currency"] = "BDT"
    post_body["tran_id"] = tran_id
    post_body["success_url"] = f"{main_settings.BACKEND_URL}/api/v1/payment/success/"
    post_body["fail_url"] = f"{main_settings.BACKEND_URL}/api/v1/payment/fail/"
    post_body["cancel_url"] = f"{main_settings.BACKEND_URL}/api/v1/payment/cancel/"

    # Fix EMI settings to prevent 500 error
    post_body["emi_option"] = 0

    # Safely handle user fields that might be None
    post_body["cus_name"] = (
        f"{user.first_name} {user.last_name}".strip()
        if user.first_name or user.last_name
        else user.username
    )
    post_body["cus_email"] = user.email
    post_body["cus_phone"] = getattr(user, "phone_number", None) or "01700000000"
    post_body["cus_add1"] = getattr(user, "location", None) or "Dhaka, Bangladesh"
    post_body["cus_city"] = "Dhaka"
    post_body["cus_country"] = "Bangladesh"
    post_body["shipping_method"] = "NO"
    post_body["multi_card_name"] = ""
    post_body["num_of_item"] = 1
    post_body["product_name"] = "SnapVerse Pro Subscription - 30 Days"
    post_body["product_category"] = "Subscription"
    post_body["product_profile"] = "general"

    try:
        response = sslcz.createSession(post_body)
        print(f"Payment response: {response}")

        if response.get("status") == "SUCCESS":
            return Response(
                {
                    "payment_url": response["GatewayPageURL"],
                    "transaction_id": tran_id,
                    "amount": amount,
                    "subscription_type": subscription_type,
                },
                status=200,
            )

        return Response(
            {"error": "Payment initiation failed", "details": response}, status=400
        )
    except Exception as e:
        print(f"Payment initiation error: {e}")
        return Response(
            {"error": "Payment service error", "message": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
def payment_success(request):
    print("Inside success")
    try:
        tran_id = request.data.get("tran_id")
        if not tran_id:
            print("No transaction ID found")
            return HttpResponseRedirect(
                f"{main_settings.FRONTEND_URL}/monetization/?error=no_tran_id"
            )

        # Extract user ID from transaction ID (format: pro_{user_id}_{timestamp})
        parts = tran_id.split("_")
        if len(parts) >= 2:
            user_id = parts[1]
            user = User.objects.get(id=user_id)
            user.activate_pro_subscription(duration_days=30)
            print(f"User {user_id} upgraded to pro")
        else:
            print(f"Invalid transaction ID format: {tran_id}")

    except (User.DoesNotExist, ValueError, IndexError) as e:
        print(f"Error processing payment success: {e}")

    return HttpResponseRedirect(f"{main_settings.FRONTEND_URL}/payment/success/")


@api_view(["POST"])
def payment_cancel(request):
    return HttpResponseRedirect(f"{main_settings.FRONTEND_URL}/monetization/")


@api_view(["POST"])
def payment_fail(request):
    print("Inside fail")
    return HttpResponseRedirect(f"{main_settings.FRONTEND_URL}/monetization/")
