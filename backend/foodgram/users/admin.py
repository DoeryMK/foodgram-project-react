from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


class CustomUserAdmin(UserAdmin):
    list_display = ('id', 'username', 'email', 'first_name',
                    'last_name', 'is_staff')
    list_filter = ('email', 'username')
    search_fields = ('email', 'username')
    ordering = ('username',)
    empty_value_display = '-пусто-'
    list_per_page = 30


admin.site.register(User, CustomUserAdmin)
