from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin


from .models import (CustomUser,
                     UserProfile,
                     Head, 
                     Officer,
                     Scholar,
                     )



class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False


# admin.site.register(CustomUser)
@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    readonly_fields = ('date_joined',)
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        (('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    list_display = ('username', 'id', 'email', 'is_staff', 'role')
    search_fields = ('email', 'username')
    ordering = ('username', )


@admin.register(Head)
class HeadAdmin(BaseUserAdmin):
    readonly_fields = ('date_joined',)
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        (('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    list_display = ('username', 'email', 'is_staff', 'is_active')
    search_fields = ('email', 'username')
    ordering = ('username', )
    inlines = (UserProfileInline, )


@admin.register(Officer)
class OfficerAdmin(BaseUserAdmin):
    readonly_fields = ('date_joined',)
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        (('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    list_display = ('username', 'email', 'is_staff', 'is_active')
    search_fields = ('email', 'username')
    ordering = ('username', )
    inlines = (UserProfileInline, )


@admin.register(Scholar)
class ScholarAdmin(BaseUserAdmin):
    readonly_fields = ('date_joined',)
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        (('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    list_display = ('username', 'email', 'is_staff', 'is_active')
    search_fields = ('email', 'username')
    ordering = ('username', )
    inlines = (UserProfileInline, )