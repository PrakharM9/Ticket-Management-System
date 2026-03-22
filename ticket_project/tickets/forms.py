
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Ticket, Comment

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter your email'
    }))
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to all fields
        for field_name in self.fields:
            self.fields[field_name].widget.attrs['class'] = 'form-control'
            self.fields[field_name].widget.attrs['placeholder'] = f'Enter {field_name}'


class LoginForm(forms.Form):
    """
    Login Form
    Simple form for username and password
    """
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter your username'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter your password'
    }))


class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['title', 'description', 'priority', 'created_for']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter ticket title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Describe the issue in detail',
                'rows': 5
            }),
            'priority': forms.Select(attrs={
                'class': 'form-control'
            }),
            'created_for': forms.Select(attrs={
                'class': 'form-control'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        # Pop 'user' from kwargs (it's passed from view)
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # If user is admin, show the created_for field with all users
        if self.user and self.user.is_staff:
            self.fields['created_for'].queryset = User.objects.all()
            self.fields['created_for'].label = "Select User (Who is this ticket for?)"
            self.fields['created_for'].empty_label = "--------- Select a user ---------"
            self.fields['created_for'].required = True
            self.fields['created_for'].help_text = "Choose the user who needs help"
        else:
            # For regular users, hide/remove the created_for field
            if 'created_for' in self.fields:
                del self.fields['created_for']
    
    def clean_title(self):
        """Custom validation: Check if title is long enough"""
        title = self.cleaned_data.get('title')
        if title and len(title) < 5:
            raise forms.ValidationError("Title must be at least 5 characters long")
        return title
    
    def clean(self):
        """Additional validation based on user type"""
        cleaned_data = super().clean()
        
        # If user is admin, ensure created_for is selected
        if self.user and self.user.is_staff:
            created_for = cleaned_data.get('created_for')
            if not created_for:
                raise forms.ValidationError("Please select a user this ticket is for")
        
        return cleaned_data


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Write your comment here...',
                'rows': 3
            })
        }


class StatusUpdateForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={
                'class': 'form-control'
            })
        }