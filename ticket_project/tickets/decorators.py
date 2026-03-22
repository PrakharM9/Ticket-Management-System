from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

def staff_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "Please login first")
            return redirect('login')
        
        if not request.user.is_staff:
            messages.error(request, "You don't have permission to access this page")
            return redirect('dashboard')
        
        return view_func(request, *args, **kwargs)
    return wrapper


def ticket_owner_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "Please login first")
            return redirect('login')
        
        # Get ticket ID from URL
        ticket_id = kwargs.get('ticket_id')
        from .models import Ticket
        
        try:
            ticket = Ticket.objects.get(id=ticket_id)
            if ticket.created_by != request.user and not request.user.is_staff:
                messages.error(request, "You don't have permission to modify this ticket")
                return redirect('ticket_list')
        except Ticket.DoesNotExist:
            messages.error(request, "Ticket not found")
            return redirect('ticket_list')
        
        return view_func(request, *args, **kwargs)
    return wrapper