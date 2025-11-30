from django.shortcuts import render,redirect,get_object_or_404
from .models import Post,Category,Tag
from .forms import PostForm,RegisterForm,LoginForm,ProfileUpdateForm
from django.contrib.auth import login,logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.db.models import Q

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = User.objects.create_user(
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password'],
            )

            # Save profile picture if uploaded
            profile = user.profile  # auto created from signal
            profile.profile_pic = form.cleaned_data.get('profile_pic')
            profile.save()

            login(request, user)
            messages.success(request,'Registration succesful. You are now logged in.')
            return redirect('blog_list')
    else:
        form = RegisterForm()

    return render(request, 'blog/register_form.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        form.request = request  # Needed for authenticate()
        if form.is_valid():
            user = form.cleaned_data.get('user')
            login(request, user)
            messages.success(request,'You are now logged in.')
            return redirect('blog_list')
    else:
        form = LoginForm()

    return render(request, 'blog/login_form.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)   # must pass request
    messages.success(request,'You are now logged out.')
    return redirect('login')

def index(request):
    blogs = Post.objects.all().order_by('-created_at')
    return render(request, 'blog/index.html',{'blogs' : blogs})

def blog_list(request):
    blogs = Post.objects.select_related('category', 'author').prefetch_related('tags')
    categories = Category.objects.values('id','name').distinct()
    query = request.GET.get('q')
    category_id = request.GET.get('category')

    if category_id:
        blogs = blogs.filter(category_id=category_id)
    if query:
        blogs = blogs.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(category__name__icontains=query) |
            Q(tags__name__icontains=query)
        ).distinct()

    # Count only user's own posts
    if request.user.is_authenticated:
        user_posts_count = Post.objects.filter(author=request.user).count()
    else:
        user_posts_count = 0

    context = {
        'blogs': blogs,
        'categories' : categories,
        'user_posts_count': user_posts_count,
        'current_year': timezone.now().year,
    }
    return render(request, 'blog/blog_list.html', context)

def blog_detail(request,slug):

    blog = get_object_or_404(Post, slug=slug)
    # Session-based unique view counting
    session_key = f'post_viewed_{blog.id}'
    if not request.session.get(session_key, False):
        blog.views = blog.views + 1
        blog.save(update_fields=['views'])
        request.session[session_key] = True  # mark as viewed

    return render(request, 'blog/blog_detail.html', {'blog': blog})

@login_required
def user_dashboard(request):
    blogs = Post.objects.filter(author=request.user)
    return render(request,'blog/user_dashboard.html',{'blogs': blogs})
    
@login_required
def create_blog(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, user=request.user)
        
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user

            # Handle new category BEFORE saving post
            new_category = form.cleaned_data.get('new_category')
            if new_category:
                category_obj, created = Category.objects.get_or_create(
                    name=new_category, 
                    user=request.user
                )
                post.category = category_obj

            post.save()  # Save after assigning category

            form.save_m2m()  # Save selected tags from form
            # Now handle tags AFTER post.save()
            new_tags = form.cleaned_data.get('new_tags')
            if new_tags:
                tag_list = [tag.strip() for tag in new_tags.split(',')]
                for tag_name in tag_list:
                    tag_obj, created = Tag.objects.get_or_create(
                        name=tag_name, 
                        user=request.user
                    )
                    post.tags.add(tag_obj)

            return redirect('blog_list')

    else:
        form = PostForm(user=request.user)

    return render(request, 'blog/blog_form.html', {'form': form})

@login_required
def update_blog(request, pk):
    blog = get_object_or_404(Post, pk=pk)

    if request.method == 'POST':
        form = PostForm(request.POST, instance=blog,user = request.user)   # bind instance
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()

            # Handle new category
            new_category = form.cleaned_data.get('new_category')
            if new_category:
                category_obj, created = Category.objects.get_or_create(
                    name=new_category,
                    user=request.user
                )
                post.category = category_obj
                post.save()

            # Handle new tags
            new_tags = form.cleaned_data.get('new_tags')
            if new_tags:
                tag_list = [tag.strip() for tag in new_tags.split(',')]
                for tag_name in tag_list:
                    tag_obj, created = Tag.objects.get_or_create(
                        name=tag_name,
                        user=request.user
                    )
                    post.tags.add(tag_obj)

            form.save_m2m()
            return redirect('blog_list')
    else:
        form = PostForm(instance=blog,user = request.user)  # Pre-filled form in GET

    return render(request, 'blog/blog_form.html', {'form': form})

@login_required
def delete_blog(request,pk):
    blog = get_object_or_404(Post, pk=pk)
    blog.delete()
    return redirect('blog_list')

@login_required
def profile_view(request):
    user = request.user  # No need to query
    return render(request, 'blog/user_profile.html', {'userdata': user})


@login_required
def edit_profile_view(request):
    user = request.user
    profile = user.profile

    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, initial={'user_id': user.id})
        
        if form.is_valid():
            # Update User model
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.username = form.cleaned_data['username']
            user.email = form.cleaned_data['email']
            user.save()

            # Update Profile model (profile_pic only)
            if form.cleaned_data.get('profile_pic'):
                profile.profile_pic = form.cleaned_data.get('profile_pic')
            profile.save()

            messages.success(request, "Profile updated successfully!")
            return redirect('blog_list')

    else:
        form = ProfileUpdateForm(
            initial={
                'first_name': user.first_name,
                'last_name': user.last_name,
                'username': user.username,
                'email': user.email,
                'user_id': user.id
            }
        )

    return render(request, 'blog/edit_profile.html', {'form': form})

@login_required
def user_posts(request):
    posts = Post.objects.filter(author=request.user)
    categories = Category.objects.values('id','name').distinct()
    query = request.GET.get('q')
    category_id = request.GET.get('category')
    if category_id:
        posts = posts.filter(category_id=category_id)
    
    if query:
        posts = posts.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(category__name__icontains=query) |
            Q(tags__name__icontains=query)
        ).distinct()
    return render(request, 'blog/user_posts.html', {'posts': posts,'categories': categories})

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # prevents logout
            messages.success(request, 'Your password was successfully updated!')
            return redirect('view_profile')
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'blog/change_password.html', {'form': form})