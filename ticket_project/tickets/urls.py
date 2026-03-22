
from django.urls import path
from . import views

urlpatterns = [
    # Authentication URLs
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Main pages
    path('', views.dashboard_view, name='dashboard'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    
    # Ticket URLs
    path('tickets/', views.ticket_list_view, name='ticket_list'),
    path('tickets/create/', views.ticket_create_view, name='ticket_create'),
    path('tickets/<int:ticket_id>/', views.ticket_detail_view, name='ticket_detail'),
    path('tickets/<int:ticket_id>/edit/', views.ticket_edit_view, name='ticket_edit'),
    path('tickets/<int:ticket_id>/delete/', views.ticket_delete_view, name='ticket_delete'),
    
    # Comment URL
    path('tickets/<int:ticket_id>/comment/', views.add_comment_view, name='add_comment'),
    
    # Admin only URL
    path('tickets/<int:ticket_id>/status/', views.update_status_view, name='update_status'),
]