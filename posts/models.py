from django.db import models
from django.conf import settings


class Post(models.Model):
    """
    Model representing a post in the application.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="posts",
    )
    caption = models.TextField(max_length=2200, blank=True, null=True)
    image = models.ImageField(upload_to="posts/images/", blank=True, null=True)
    video = models.FileField(upload_to="posts/videos/", blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    PRIVACY_CHOICES = [
        ("public", "Public"),
        ("private", "Private"),
        ("followers", "Followers Only"),
    ]
    privacy = models.CharField(
        max_length=10,
        choices=PRIVACY_CHOICES,
        default="public",
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        if self.caption:
            return self.caption[:50] + "..." if len(self.caption) > 50 else self.caption
        return f"Post by {self.user.username}"


class Reaction(models.Model):
    """
    Model representing a reaction to a post.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reactions",
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="reactions",
    )

    REACTION_CHOICES = [
        ("like", "Like"),
        ("dislike", "Dislike"),
        ("love", "Love"),
        ("haha", "Haha"),
        ("wow", "Wow"),
        ("sad", "Sad"),
        ("angry", "Angry"),
    ]
    reaction = models.CharField(
        max_length=10,
        choices=REACTION_CHOICES,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "post")

    def __str__(self):
        return f"{self.user.username} {self.reaction} {self.post.caption[:20] if self.post.caption else 'post'}..."


class Comment(models.Model):
    """
    Model representing a comment on a post.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    text = models.TextField(max_length=1000)
    is_edited = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # --> For nested comments (replies)
    parent_comment = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="replies",
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["post"]),
            models.Index(fields=["parent_comment"]),
        ]

    def __str__(self):
        return f"{self.user.username}: {self.text[:30]}..."

    def save(self, *args, **kwargs):
        # --> Mark as edited if text is being updated (not on creation)
        if self.pk and self.text:
            original = Comment.objects.get(pk=self.pk)
            if original.text != self.text:
                self.is_edited = True
        super().save(*args, **kwargs)

