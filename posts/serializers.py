from rest_framework import serializers

from django.contrib.auth import get_user_model
from posts.models import Post, Reaction, Comment

User = get_user_model()


class PostCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating posts"""

    image = serializers.ImageField(required=False)

    class Meta:
        model = Post
        fields = [
            "caption",
            "image",
            # "video",
            "location",
            "privacy",
        ]

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)


class PostDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed post view"""

    user = serializers.CharField(source="user.get_full_name", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)
    user_profile_picture = serializers.ImageField(
        source="user.profile_picture", read_only=True
    )
    reactions_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            "id",
            "user",
            "username",
            "user_profile_picture",
            "caption",
            "image",
            # "video",
            "location",
            "privacy",
            "is_edited",
            "created_at",
            "updated_at",
            "reactions_count",
            "comments_count",
        ]

    def get_reactions_count(self, obj):
        """Get total reactions count for this post"""
        return obj.reactions.count()

    def get_comments_count(self, obj):
        """Get total comments count for this post"""
        return obj.comments.count()


class PostUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating posts"""

    image = serializers.ImageField(required=False)

    class Meta:
        model = Post
        fields = ["caption", "location", "privacy", "image", "is_edited"]

    def update(self, instance, validated_data):
        validated_data["is_edited"] = True
        return super().update(instance, validated_data)


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for displaying comments"""

    user = serializers.CharField(source="user.get_full_name", read_only=True)
    user_profile_picture = serializers.ImageField(
        source="user.profile_picture", read_only=True
    )
    replies_count = serializers.SerializerMethodField()
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = [
            "id",
            "user",
            "user_profile_picture",
            "text",
            "is_edited",
            "created_at",
            "updated_at",
            "replies_count",
            "replies",
        ]

    def get_replies_count(self, obj):
        """Get count of replies to this comment"""
        return obj.replies.count()

    def get_replies(self, obj):
        """Get first few replies (limit to avoid deep nesting)"""
        replies = obj.replies.all()[:5]  # --> Limit to 5 replies for performance
        return CommentReplySerializer(replies, many=True, context=self.context).data


class CommentWithPostSerializer(serializers.ModelSerializer):
    """Serializer for displaying comments with post information"""

    user = serializers.CharField(source="user.username", read_only=True)
    user_profile_picture = serializers.ImageField(
        source="user.profile_picture", read_only=True
    )
    replies_count = serializers.SerializerMethodField()
    post = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = [
            "id",
            "user",
            "user_profile_picture",
            "text",
            "is_edited",
            "created_at",
            "updated_at",
            "replies_count",
            "post",
        ]

    def get_replies_count(self, obj):
        """Get count of replies to this comment"""
        return obj.replies.count()

    def get_post(self, obj):
        """Get basic post information"""
        return {
            "id": obj.post.id,
            "user": obj.post.user.username,
            "caption": (
                obj.post.caption[:100] + "..."
                if len(obj.post.caption) > 100
                else obj.post.caption
            ),
            "image": obj.post.image.url if obj.post.image else None,
            # "video": obj.post.video.url if obj.post.video else None,
            "created_at": obj.post.created_at,
            "privacy": obj.post.privacy,
        }


class CommentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating comments"""

    class Meta:
        model = Comment
        fields = ["text", "parent_comment"]

    def validate_parent_comment(self, value):
        """Validate parent comment belongs to the same post"""
        if value and hasattr(self.context["view"], "get_object"):
            post = self.context["view"].get_object()
            if value.post != post:
                raise serializers.ValidationError(
                    "Parent comment must belong to the same post"
                )
        return value


class CommentTextSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating comments and replies - only text field needed"""

    class Meta:
        model = Comment
        fields = ["text"]


class CommentReplySerializer(serializers.ModelSerializer):
    """Serializer for comment replies (nested comments)"""

    user = serializers.CharField(source="user.get_full_name", read_only=True)
    user_profile_picture = serializers.ImageField(
        source="user.profile_picture", read_only=True
    )

    class Meta:
        model = Comment
        fields = [
            "id",
            "user",
            "user_profile_picture",
            "text",
            "is_edited",
            "created_at",
            "updated_at",
        ]


class ReactionSerializer(serializers.ModelSerializer):
    """Serializer for post reactions"""

    user = serializers.CharField(source="user.get_full_name", read_only=True)
    user_profile_picture = serializers.ImageField(
        source="user.profile_picture", read_only=True
    )

    class Meta:
        model = Reaction
        fields = [
            "id",
            "user",
            "user_profile_picture",
            "reaction",
            "created_at",
        ]


class ReactionCreateSerializer(serializers.Serializer):
    """Serializer for creating/updating reactions with choice field"""

    reaction = serializers.ChoiceField(
        choices=Reaction.REACTION_CHOICES, help_text="Choose a reaction type"
    )

    def validate_reaction(self, value):
        """Validate reaction choice"""
        valid_choices = [choice[0] for choice in Reaction.REACTION_CHOICES]
        if value not in valid_choices:
            raise serializers.ValidationError(
                f"Invalid reaction. Choose from: {valid_choices}"
            )
        return value
