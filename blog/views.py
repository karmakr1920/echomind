from django.shortcuts import render,redirect,get_object_or_404
from .models import Post,Category,Tag
from .forms import PostForm,RegisterForm,LoginForm,ProfileUpdateForm
from django.contrib.auth import login,logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone

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
    return render(request, 'blog/index.html')

def blog_list(request):
    blogs = Post.objects.all()  # All posts (for listing)

    # Count only user's own posts
    user_posts_count = Post.objects.filter(author=request.user).count()


    context = {
        'blogs': blogs,
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
def create_blog(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)     # don't save yet
            post.author = request.user         # set author manually
            post.save()                        # now save
            form.save_m2m()                    # save tags
            return redirect('blog_list')
    else:
        form = PostForm()  # GET request
    return render(request, 'blog/blog_form.html', {'form': form})

@login_required
def update_blog(request, pk):
    blog = get_object_or_404(Post, pk=pk)

    if request.method == 'POST':
        form = PostForm(request.POST, instance=blog)   # bind instance
        if form.is_valid():
            form.save()
            return redirect('blog_list')
    else:
        form = PostForm(instance=blog)  # Pre-filled form in GET

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
    return render(request, 'blog/user_posts.html', {'posts': posts})