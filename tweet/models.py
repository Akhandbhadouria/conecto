from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta


class Tweet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    #Each tweet belongs to one user
    #ForeignKey creates a many-to-one relationship
    #One user → many tweets
    #One tweet → one user
    #on_delete=models.CASCADE
    #If a user is deleted → all their tweets are automatically deleted

    text = models.TextField(max_length=240)
    photo = models.ImageField(upload_to='photo/', blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(User, related_name='tweet_likes', blank=True)

    def __str__(self):
        return f'{self.user.username}-{self.text[:10]}'

    def total_likes(self):
        return self.likes.count()

    def user_has_liked(self, user):
        return self.likes.filter(id=user.id).exists()


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profession = models.CharField(max_length=100, blank=True)
    email = models.CharField(max_length=200)
    is_verified = models.BooleanField(default=False)
    bio = models.TextField(blank=True)
    profile_photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)

    followers = models.ManyToManyField(
        User, related_name='following', blank=True
    )

    # === Image Moderation Fields ===
    warning_count = models.IntegerField(default=0)
    suspended_until = models.DateTimeField(null=True, blank=True)

    SUSPENSION_HOURS = 24       # Duration of suspension
    MAX_WARNINGS = 3            # Warnings before suspension

    def __str__(self):
        return self.user.username

    @property
    def following_count(self):
        return self.user.following.count()

    @property
    def followers_count(self):
        return self.followers.count()

    @property
    def is_suspended(self):
        """Check if the user is currently suspended from posting."""
        if self.suspended_until and self.suspended_until > timezone.now():
            return True
        return False

    @property
    def suspension_remaining(self):
        """Return human-readable time remaining on suspension."""
        if not self.is_suspended:
            return None
        delta = self.suspended_until - timezone.now()
        hours, remainder = divmod(int(delta.total_seconds()), 3600)
        minutes, _ = divmod(remainder, 60)
        return f"{hours}h {minutes}m"

    def record_violation(self):
        """Record a content violation and suspend if threshold reached."""
        self.warning_count += 1
        if self.warning_count >= self.MAX_WARNINGS:
            self.suspended_until = timezone.now() + timedelta(hours=self.SUSPENSION_HOURS)
        self.save()

    def total_likes_received(self):
        """Count total likes across all user's tweets."""
        return Tweet.objects.filter(user=self.user).aggregate(
            total_likes=Count('likes')
        )['total_likes'] or 0


class Comment(models.Model):
    """Comment on a Tweet — like Instagram comments."""
    tweet = models.ForeignKey(Tweet, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'Comment by {self.user.username} on tweet {self.tweet.id}'


class ModerationLog(models.Model):
    """Audit log for every AI moderation prediction."""
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    comment_text = models.TextField()
    prediction = models.CharField(max_length=50)  # 'safe' or 'abusive'
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.prediction} — {self.user.username if self.user else 'Unknown'} @ {self.timestamp}"
    


