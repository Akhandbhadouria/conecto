from django.contrib import admin
from .models import Tweet, UserProfile


@admin.register(Tweet)
class TweetAdmin(admin.ModelAdmin):
    list_display = ('user', 'text', 'updated_at', 'total_likes')
    list_filter = ('updated_at',)
    search_fields = ('user__username', 'text')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'profession', 'warning_count', 'suspended_until', 'is_suspended')
    list_filter = ('warning_count', 'suspended_until')
    search_fields = ('user__username', 'email')
    readonly_fields = ('is_suspended', 'suspension_remaining')

    def is_suspended(self, obj):
        return obj.is_suspended
    is_suspended.boolean = True
    is_suspended.short_description = 'Currently Suspended'

    def suspension_remaining(self, obj):
        return obj.suspension_remaining or '—'
    suspension_remaining.short_description = 'Suspension Remaining'
