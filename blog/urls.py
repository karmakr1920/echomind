from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('blog/', views.blog_list, name='blog_list'),
    path('blog/<slug:slug>',views.blog_detail,name='blog_detail'),
    path('add/blog/',views.create_blog,name= 'create_blog'),
    path('edit/blog/<int:pk>',views.update_blog,name= 'update_blog'),
    path('delete/blog/<int:pk>',views.delete_blog,name= 'delete_blog'),
    path('register/',views.register_view, name= 'register'),
    path('login/',views.login_view, name= 'login'),
    path('logout/',views.logout_view, name= 'logout'),
    path('profile/view/', views.profile_view, name='view_profile'),
    path('profile/edit/', views.edit_profile_view, name='edit_profile'),
    path('profile/change-password/', views.change_password, name='change_password'),
    path('my-posts/', views.user_posts, name='user_posts'),
    path('dashboard',views.user_dashboard,name='user_dashboard'),
    path('post/<int:post_id>/like/', views.like_post, name='like_post'),
    path('post/<int:post_id>/bookmark/', views.bookmark_post, name='add_bookmark'),
    path('saved-posts/', views.saved_posts, name='saved_posts'),



]