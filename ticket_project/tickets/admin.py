"""
Admin Panel Configuration
EASY EXPLANATION: This makes our models look nice in the admin panel
"""

from django.contrib import admin
from .models import Ticket, Comment

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    """How tickets appear in admin panel"""
    list_display = ['id', 'title', 'status', 'priority', 'created_by', 'created_at']
    list_filter = ['status', 'priority', 'created_at']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['status', 'priority']
    list_per_page = 25
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description')
        }),
        ('Status & Priority', {
            'fields': ('status', 'priority')
        }),
        ('User Information', {
            'fields': ('created_by',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)  # Collapsed by default
        }),
    )


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """How comments appear in admin panel"""
    list_display = ['id', 'ticket', 'author', 'created_at']
    list_filter = ['created_at']
    search_fields = ['message']
    readonly_fields = ['created_at']