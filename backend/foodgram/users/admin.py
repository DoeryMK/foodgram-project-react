from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

from .models import User, Follow


class CustomUserAdmin(UserAdmin):
    list_display = (
        'id', 'username', 'email', 'first_name', 'last_name', 'is_staff'
    )
    list_filter = (
        'email', 'username'
    )
    search_fields = (
        'email', 'username'
    )
    ordering = (
        'username',
    )
    empty_value_display = '-пусто-'
    list_per_page = 30


class FollowAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'author'
    )
    list_filter = (
        'author',
    )


admin.site.register(User, CustomUserAdmin)
admin.site.register(Follow, FollowAdmin)
admin.site.unregister(Group)
