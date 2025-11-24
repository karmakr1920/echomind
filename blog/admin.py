from django.contrib import admin
from .models import Post,Tag,Category

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}
    list_display = ("title", "author", "status", "created_at", "views")
    search_fields = ("title", "content")
    list_filter = ("status", "created_at", "category", "tags")

admin.site.register(Tag)
admin.site.register(Category)
