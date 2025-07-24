from rest_framework import serializers

from django.contrib.auth import get_user_model
from relationships.models import Follow

User = get_user_model()


class UserMinimalSerializer(serializers.ModelSerializer):
    """Minimal user serializer for follow relationships"""

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "profile_picture",
            "is_private",
        ]
        read_only_fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "profile_picture",
            "is_private",
        ]


class FollowSerializer(serializers.ModelSerializer):
    """Complete follow relationship serializer"""

    follower = UserMinimalSerializer(read_only=True)
    following = UserMinimalSerializer(read_only=True)

    class Meta:
        model = Follow
        fields = [
            "id",
            "follower",
            "following",
            "is_approved",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class FollowActionRequestSerializer(serializers.Serializer):
    """Serializer for follow action requests (input validation)"""

    user_id = serializers.IntegerField(
        min_value=1, help_text="ID of the user to follow"
    )


class FollowStatsSerializer(serializers.Serializer):
    """Serializer for follow statistics"""

    followers_count = serializers.IntegerField()
    following_count = serializers.IntegerField()
    pending_requests_count = serializers.IntegerField()


class PendingRequestActionSerializer(serializers.Serializer):
    """Serializer for handling pending requests with approve/reject choice"""

    CHOICE_OPTIONS = [("Approve", "Approve"), ("Reject", "Reject")]

    id = serializers.IntegerField(min_value=1, help_text="ID of the follow request")
    action = serializers.ChoiceField(
        choices=CHOICE_OPTIONS, help_text="Choose Approve or Reject"
    )
