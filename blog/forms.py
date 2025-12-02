from django import forms
from .models import Post,Category,Tag,Comment
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate
import re
from ckeditor_uploader.widgets import CKEditorUploadingWidget

class PostForm(forms.ModelForm):
    new_category = forms.CharField(required=False, label="Add New Category")
    new_tags = forms.CharField(
        required=False,
        label="Add New Tags (comma-separated)",
        help_text="Example: python, django, ai"
    )
    content = forms.CharField(widget=CKEditorUploadingWidget())
    class Meta:
        model = Post
        fields = ['title', 'content', 'category', 'tags', 'status']
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')  # Get logged-in user
        super().__init__(*args, **kwargs)

        # Show only user's categories and tags
        self.fields['category'].queryset = Category.objects.filter(user=user)
        self.fields['tags'].queryset = Tag.objects.filter(user=user)

class RegisterForm(forms.Form):
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'First Name'}),
        error_messages={'required': 'First name is required.'}
    )

    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Last Name'}),
        error_messages={'required': 'Last name is required.'}
    )

    username = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Username'}),
        error_messages={'required': 'Username is required.'}
    )

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'Email'}),
        error_messages={'required': 'Email is required.'}
    )

    profile_pic = forms.FileField(required=False)

    password = forms.CharField(
        min_length=8,
        widget=forms.PasswordInput(attrs={'placeholder': 'Password'}),
        help_text="At least 8 chars, must include letters & numbers.",
        error_messages={'required': 'Password is required.'}
    )

    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password'}),
        required=True,
        error_messages={'required': 'Please confirm your password.'}
    )

    # First Name validation - Only alphabets allowed
    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if not re.match(r'^[A-Za-z]+$', first_name):
            raise ValidationError("First name can only contain letters.")
        return first_name

    # Last Name validation - Only alphabets allowed
    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if not re.match(r'^[A-Za-z]+$', last_name):
            raise ValidationError("Last name can only contain letters.")
        return last_name

    # Username validation - Only letters, numbers, underscore. No special chars.
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username__iexact=username).exists():
            raise ValidationError("This username is already taken.")
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            raise ValidationError("Username can only contain letters, numbers, and underscores.")
        return username

    # Email validation - Check uniqueness
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("This email is already registered.")
        return email

    # Password Strength validation
    def clean_password(self):
        password = self.cleaned_data.get('password')
        if not re.search(r'[A-Za-z]', password) or not re.search(r'\d', password):
            raise ValidationError("Password must contain both letters and numbers.")
        return password

    # Cross-field validation (password match)
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match.")

        return cleaned_data

class LoginForm(forms.Form):
    username_or_email = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Username or Email'}),
        error_messages={'required': 'Please enter your username or email.'}
    )
    
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={'placeholder': 'Password'}),
        error_messages={'required': 'Please enter your password.'}
    )

    def clean(self):
        cleaned_data = super().clean()
        username_or_email = cleaned_data.get('username_or_email')
        password = cleaned_data.get('password')

        if username_or_email and password:
            # Try logging in with username first
            user = authenticate(request=self.request, username=username_or_email, password=password)

            # If failed, try with email
            if user is None:
                try:
                    user_obj = User.objects.get(email__iexact=username_or_email)
                    user = authenticate(request=self.request, username=user_obj.username, password=password)
                except User.DoesNotExist:
                    user = None

            # Handle errors
            if user is None:
                self.add_error('username_or_email', "Invalid username/email or password.")
            elif not user.is_active:
                self.add_error('username_or_email', "This account is inactive. Contact support.")
            
            cleaned_data['user'] = user  # Pass user to view

        return cleaned_data
    

class ProfileUpdateForm(forms.Form):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    username = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)
    profile_pic = forms.FileField(required=False)

    # Only letters allowed in names
    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if not re.match(r'^[A-Za-z]+$', first_name):
            raise ValidationError("First name can only contain letters.")
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if not re.match(r'^[A-Za-z]+$', last_name):
            raise ValidationError("Last name can only contain letters.")
        return last_name

    # Unique username (skip current user)
    def clean_username(self):
        username = self.cleaned_data.get('username')
        user_qs = User.objects.filter(username__iexact=username).exclude(id=self.initial['user_id'])
        if user_qs.exists():
            raise ValidationError("This username already exists.")
        return username

    # Unique email (skip current user)
    def clean_email(self):
        email = self.cleaned_data.get('email')
        email_qs = User.objects.filter(email__iexact=email).exclude(id=self.initial['user_id'])
        if email_qs.exists():
            raise ValidationError("This email is already registered.")
        return email
    

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Write your comment...'}),
        }