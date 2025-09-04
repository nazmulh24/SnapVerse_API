from djoser.serializers import (
    UserSerializer as BaseUserSerializer,
    UserCreateSerializer as BaseUserCreateSerializer,
)
from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class UserCreateSerializer(BaseUserCreateSerializer):
    """Serializer for user registration"""

    class Meta(BaseUserCreateSerializer.Meta):
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "password",
        )


class UserSerializer(BaseUserSerializer):
    """Complete user serializer for authenticated users"""

    full_name = serializers.SerializerMethodField(method_name="get_full_name")
    followers_count = serializers.SerializerMethodField(
        method_name="get_followers_count"
    )
    following_count = serializers.SerializerMethodField(
        method_name="get_following_count"
    )
    posts_count = serializers.SerializerMethodField(method_name="get_posts_count")

    class Meta(BaseUserSerializer.Meta):
        ref_name = "CustomUser"
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "full_name",
            "profile_picture",
            "cover_photo",
            "bio",
            "location",
            "phone_number",
            "date_of_birth",
            "gender",
            "relationship_status",
            "is_private",
            "date_joined",
            "last_login",
            "followers_count",
            "following_count",
            "posts_count",
        )
        read_only_fields = ("id", "date_joined", "last_login")

    def get_full_name(self, obj):
        return obj.get_full_name()

    def get_followers_count(self, obj):
        return obj.followers.filter(is_approved=True).count()

    def get_following_count(self, obj):
        return obj.following.filter(is_approved=True).count()

    def get_posts_count(self, obj):
        return obj.posts.count()


class UserListSerializer(serializers.ModelSerializer):
    """Minimal serializer for user lists"""

    full_name = serializers.SerializerMethodField(method_name="get_full_name")
    is_following = serializers.SerializerMethodField(method_name="get_is_following")

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "full_name",
            "profile_picture",
            "bio",
            "is_private",
            "is_following",
        )

    def get_full_name(self, obj):
        return obj.get_full_name()

    def get_is_following(self, obj):
        request_user = (
            self.context.get("request").user if self.context.get("request") else None
        )
        if request_user and request_user.is_authenticated:
            try:
                follow = request_user.following.get(following=obj)
                return follow.is_approved
            except:
                return False
        return False


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for viewing other users' public profiles"""

    full_name = serializers.SerializerMethodField()
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()
    posts_count = serializers.SerializerMethodField()
    is_following = serializers.SerializerMethodField()
    follow_status = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "full_name",
            "email",
            "profile_picture",
            "cover_photo",
            "bio",
            "location",
            "phone_number",
            "date_of_birth",
            "gender",
            "relationship_status",
            "is_private",
            "date_joined",
            "last_login",
            "followers_count",
            "following_count",
            "posts_count",
            "is_following",
            "follow_status",
        )

    def get_full_name(self, obj):
        return obj.get_full_name()

    def get_followers_count(self, obj):
        return obj.followers.filter(is_approved=True).count()

    def get_following_count(self, obj):
        return obj.following.filter(is_approved=True).count()
    
    def get_posts_count(self, obj):
        return obj.posts.count()

    def get_is_following(self, obj):
        request_user = (
            self.context.get("request").user if self.context.get("request") else None
        )
        if request_user and request_user.is_authenticated:
            return self._is_following(obj, request_user)
        return False

    def get_follow_status(self, obj):
        """Returns: 'following', 'pending', 'not_following'"""
        request_user = (
            self.context.get("request").user if self.context.get("request") else None
        )
        if request_user and request_user.is_authenticated:
            try:
                follow = request_user.following.get(following=obj)
                return "following" if follow.is_approved else "pending"
            except:
                return "not-following"
        return "not-following"

    def _is_following(self, obj, request_user):
        """Helper method to check if request_user is following obj"""
        try:
            follow = request_user.following.get(following=obj)
            return follow.is_approved
        except:
            return False
