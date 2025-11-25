from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify

class Category(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name
    
class Tag(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name

class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    content = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    tags = models.ManyToManyField(Tag, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10, choices=[('draft','Draft'),('published','Published')])
    views = models.IntegerField(default=0)
    read_time = models.IntegerField(null=True, blank=True)  # 4 min read

    def save(self, *args, **kwargs):
        # Slug generation (only on first save)
        if not self.slug:
            base_slug = slugify(self.title)
            unique_slug = base_slug
            counter = 1

            while Post.objects.filter(slug=unique_slug).exclude(pk=self.pk).exists():
                unique_slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = unique_slug

        # Read time calculation
        if self.content:
            word_count = len(self.content.split())
            self.read_time = max(1, round(word_count / 200))  # 200 WPM reading speed

        super().save(*args, **kwargs)



        def __str__(self):
            return self.title

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    profile_pic = models.ImageField(upload_to='profiles/', null=True, blank=True)

    def __str__(self):
        return self.user.username
