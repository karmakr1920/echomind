from django.shortcuts import render,redirect,get_object_or_404
from .models import Post,Category,Tag
from .forms import PostForm

def index(request):
    return render(request, 'blog/index.html')

def blog_list(request):
    blogs = Post.objects.all()
    context = {'blogs' : blogs}
    return render(request, 'blog/blog_list.html',context)

def blog_detail(request,slug):

    blog = get_object_or_404(Post, slug=slug)
    # Session-based unique view counting
    session_key = f'post_viewed_{blog.id}'
    if not request.session.get(session_key, False):
        blog.views = blog.views + 1
        blog.save(update_fields=['views'])
        request.session[session_key] = True  # mark as viewed

    return render(request, 'blog/blog_detail.html', {'blog': blog})

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

def delete_blog(request,pk):
    blog = get_object_or_404(Post, pk=pk)
    blog.delete()
    return redirect('blog_list')
