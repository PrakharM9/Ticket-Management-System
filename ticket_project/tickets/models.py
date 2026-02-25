"""
Database Models
EASY EXPLANATION: Each class here becomes a table in the database
Think of them like Excel sheets with columns
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Ticket(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),  # (value_in_db, display_name)
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]
    
    # PRIORITY CHOICES
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    
    # Basic ticket information
    title = models.CharField(max_length=200)
    description = models.TextField()
    
    # Status and Priority (with defaults)
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='open'
    )
    priority = models.CharField(
        max_length=10, 
        choices=PRIORITY_CHOICES, 
        default='medium'
    )
    
    # Relationships
    created_by = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='tickets_created'  # Changed to avoid confusion
    )
    created_for = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='tickets_owned',  # This user's tickets
        null=True,  # Allow null for existing tickets
        blank=True
    )
    
    # NEW: Track if admin created it
    is_admin_created = models.BooleanField(default=False)
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        """How this ticket appears in admin panel"""
        # FIX: Use direct dictionary access instead of get_status_display if it's not working
        status_dict = dict(self.STATUS_CHOICES)
        status_value = status_dict.get(self.status, self.status)
        return f"{self.title} - {status_value}"
    
    def get_status_display_safe(self):
        """Safe way to get status display value"""
        status_dict = dict(self.STATUS_CHOICES)
        return status_dict.get(self.status, self.status)
    
    def get_priority_display_safe(self):
        """Safe way to get priority display value"""
        priority_dict = dict(self.PRIORITY_CHOICES)
        return priority_dict.get(self.priority, self.priority)
    
    def time_since_created(self):
        """Helper method to show how long ago ticket was created"""
        now = timezone.now()
        diff = now - self.created_at
        if diff.days > 0:
            return f"{diff.days} days ago"
        elif diff.seconds // 3600 > 0:
            return f"{diff.seconds // 3600} hours ago"
        elif diff.seconds // 60 > 0:
            return f"{diff.seconds // 60} minutes ago"
        else:
            return "Just now"


class Comment(models.Model):
    """
    Comment Model - Comments on tickets
    Each comment belongs to one ticket and one user
    """
    
    # Relationships
    ticket = models.ForeignKey(
        Ticket, 
        on_delete=models.CASCADE, 
        related_name='comments'  # This MUST match what you use in views
    )
    author = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='comments_made'  # Optional, but good practice
    )
    
    # Comment content
    message = models.TextField()
    
    # Timestamp
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Comment by {self.author.username} on {self.ticket.title}"
    
    class Meta:
        ordering = ['-created_at']  # Show newest comments first