from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('校內身分資訊', {'fields': ('student_id', 'is_school_member')}),
    )
    list_display = UserAdmin.list_display + ('student_id', 'is_school_member')
    list_filter = UserAdmin.list_filter + ('is_school_member',)
