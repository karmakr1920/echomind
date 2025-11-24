from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('blog/', views.blog_list, name='blog_list'),
    path('blog/<slug:slug>',views.blog_detail,name='blog_detail'),
    path('add/blog/',views.create_blog,name= 'create_blog'),
    path('edit/blog/<int:pk>',views.update_blog,name= 'update_blog'),
    path('delete/blog/<int:pk>',views.delete_blog,name= 'delete_blog'),

]