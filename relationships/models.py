from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError


class Follow(models.Model):
    """
    Model representing a follow relationship between users.
    For private accounts, is_approved=False until approved.
    """

    follower = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="following",
    )
    following = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="followers",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    # --> False for pending requests to private accounts
    is_approved = models.BooleanField(default=True)

    class Meta:
        unique_together = ("follower", "following")
        ordering = ["-created_at"]

    def __str__(self):
        status = "follows" if self.is_approved else "requested to follow"
        return f"{self.follower.username} {status} {self.following.username}"

    def clean(self):
        """Prevent users from following themselves"""
        if self.follower == self.following:
            raise ValidationError("Users cannot follow themselves.")

    def save(self, *args, **kwargs):
        """Auto-set is_approved based on account privacy"""
        if not self.pk:  # -->Only on creation
            if self.following.is_private:
                self.is_approved = False  # --> Needs approval for private accounts
            else:
                self.is_approved = True  # --> Auto-approved for public accounts
        super().save(*args, **kwargs)

    def approve(self):
        """Approve the follow request"""
        self.is_approved = True
        self.save()

    def reject(self):
        """Reject the follow request (delete it)"""
        self.delete()

    @classmethod
    def create_follow(cls, follower, following):
        """Helper method to create a follow relationship"""
        follow, created = cls.objects.get_or_create(
            follower=follower, following=following
        )
        return follow, created
