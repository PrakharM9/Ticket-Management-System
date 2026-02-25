"""
Views
EASY EXPLANATION: Each function here handles what happens on a specific page
Think of them as: "When user goes to this URL, do this"
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Ticket, Comment
from .forms import RegisterForm, LoginForm, TicketForm, CommentForm, StatusUpdateForm
from .decorators import staff_required, ticket_owner_required

# ==================== AUTHENTICATION VIEWS ====================

def register_view(request):
    """Handle user registration"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Registration successful! Please login.')
            return redirect('login')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = RegisterForm()
    
    return render(request, 'tickets/register.html', {'form': form})


def login_view(request):
    """Handle user login"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                return redirect('dashboard')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()
    
    return render(request, 'tickets/login.html', {'form': form})


def logout_view(request):
    """Handle user logout"""
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('login')


# ==================== MAIN VIEWS ====================

@login_required
def dashboard_view(request):
    """
    Show summary dashboard
    Shows different data for regular users vs staff
    """
    if request.user.is_staff:
        # Staff see all tickets
        all_tickets = Ticket.objects.all()
        recent_tickets = Ticket.objects.order_by('-created_at')[:5]
    else:
        # Regular users see tickets created FOR them (not by them)
        all_tickets = Ticket.objects.filter(created_for=request.user)  # ← CHANGED to created_for
        recent_tickets = all_tickets.order_by('-created_at')[:5]
    
    # Calculate counts
    total_tickets = all_tickets.count()
    open_count = all_tickets.filter(status='open').count()
    in_progress_count = all_tickets.filter(status='in_progress').count()
    resolved_count = all_tickets.filter(status='resolved').count()
    high_priority_count = all_tickets.filter(priority='high').count()
    
    context = {
        'total_tickets': total_tickets,
        'open_count': open_count,
        'in_progress_count': in_progress_count,
        'resolved_count': resolved_count,
        'high_priority_count': high_priority_count,
        'recent_tickets': recent_tickets,
        'is_staff': request.user.is_staff,
    }
    
    return render(request, 'tickets/dashboard.html', context)
@login_required
def ticket_list_view(request):
    """
    Show list of tickets with filtering and search
    """
    # Base queryset based on user type
    if request.user.is_staff:
        tickets = Ticket.objects.all()
    else:
        # Regular users see tickets created FOR them (not by them)
        tickets = Ticket.objects.filter(created_for=request.user)  # ← CHANGED to created_for
    
    # Get filter parameters from GET request
    status_filter = request.GET.get('status')
    search_query = request.GET.get('search')
    
    # Apply status filter if provided
    if status_filter:
        tickets = tickets.filter(status=status_filter)
    
    # Apply search filter if provided
    if search_query:
        tickets = tickets.filter(title__icontains=search_query)
    
    # Order by latest first
    tickets = tickets.order_by('-created_at')
    
    context = {
        'tickets': tickets,
        'current_status': status_filter,
        'search_query': search_query,
        'is_staff': request.user.is_staff,
    }
    
    return render(request, 'tickets/ticket_list.html', context)
@login_required
def ticket_detail_view(request, ticket_id):
    """
    Show single ticket with details and comments
    """
    ticket = get_object_or_404(Ticket, id=ticket_id)
    
    # Check permission (staff can see all, regular users only their own)
    # CHANGED: Check created_for instead of created_by
    if not request.user.is_staff and ticket.created_for != request.user:
        messages.error(request, "You don't have permission to view this ticket.")
        return redirect('ticket_list')
    
    # Get comments
    comments = Comment.objects.filter(ticket=ticket).order_by('-created_at')
    comment_form = CommentForm()
    
    # Create status update form for staff
    status_form = None
    if request.user.is_staff:
        status_form = StatusUpdateForm(instance=ticket)
    
    context = {
        'ticket': ticket,
        'comments': comments,
        'comment_form': comment_form,
        'status_form': status_form,
        'is_staff': request.user.is_staff,
    }
    
    return render(request, 'tickets/ticket_detail.html', context)


@login_required
def ticket_create_view(request):
    if request.method == 'POST':
        # Pass user to form
        form = TicketForm(request.POST, user=request.user)
        if form.is_valid():
            ticket = form.save(commit=False)
            
            # CASE 1: Regular user
            if not request.user.is_staff:
                ticket.created_by = request.user
                ticket.created_for = request.user
                ticket.is_admin_created = False
            
            # CASE 2: Admin creating for someone
            else:
                ticket.created_by = request.user
                ticket.created_for = form.cleaned_data['created_for']
                ticket.is_admin_created = True
            
            ticket.status = 'open'
            ticket.save()
            return redirect('ticket_detail', ticket_id=ticket.id)
    else:
        form = TicketForm(user=request.user)
    
    return render(request, 'tickets/ticket_form.html', {'form': form})


@login_required
def ticket_edit_view(request, ticket_id):
    """Edit existing ticket"""
    ticket = get_object_or_404(Ticket, id=ticket_id)
    if not request.user.is_staff and ticket.created_for != request.user:
        messages.error(request, "You don't have permission to edit this ticket.")
        return redirect('ticket_list')
    
    if request.method == 'POST':
        form = TicketForm(request.POST, instance=ticket)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ticket updated successfully!')
            if ticket.id:
                return redirect('ticket_detail', ticket_id=ticket.id)
            else:
                return redirect('ticket_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = TicketForm(instance=ticket)
    
    return render(request, 'tickets/ticket_form.html', {
        'form': form, 
        'action': 'Edit',
        'ticket': ticket
    })


@login_required
def ticket_delete_view(request, ticket_id):
    """Delete ticket (with confirmation)"""
    ticket = get_object_or_404(Ticket, id=ticket_id)
    if not request.user.is_staff and ticket.created_for != request.user:
        messages.error(request, "You don't have permission to delete this ticket.")
        return redirect('ticket_list')
    
    if request.method == 'POST':
        ticket.delete()
        messages.success(request, 'Ticket deleted successfully!')
        return redirect('ticket_list')
    
    return render(request, 'tickets/ticket_confirm_delete.html', {'ticket': ticket})

@login_required
def add_comment_view(request, ticket_id):
    """Add comment to ticket"""
    if request.method != 'POST':
        return redirect('ticket_detail', ticket_id=ticket_id)
    
    ticket = get_object_or_404(Ticket, id=ticket_id)
    if not request.user.is_staff and ticket.created_for != request.user:
        messages.error(request, "You don't have permission to comment on this ticket.")
        return redirect('ticket_list')
    
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.ticket = ticket
        comment.author = request.user
        comment.save()
        messages.success(request, 'Comment added successfully!')
    else:
        messages.error(request, 'Failed to add comment. Please try again.')
    
    return redirect('ticket_detail', ticket_id=ticket_id)

@login_required
def update_status_view(request, ticket_id):
    """Update ticket status (admin only)"""
    if not request.user.is_staff:
        messages.error(request, "You don't have permission to update ticket status.")
        return redirect('ticket_detail', ticket_id=ticket_id)
    
    if request.method != 'POST':
        return redirect('ticket_detail', ticket_id=ticket_id)
    
    ticket = get_object_or_404(Ticket, id=ticket_id)
    form = StatusUpdateForm(request.POST, instance=ticket)
    
    if form.is_valid():
        form.save()
        status_display = ticket.get_status_display_safe()
        messages.success(request, f'Ticket status updated to {status_display}')
    else:
        messages.error(request, 'Failed to update status.')
    
    return redirect('ticket_detail', ticket_id=ticket_id)