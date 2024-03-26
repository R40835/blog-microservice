from django.urls import path

from . import views

app_name = 'blog'

urlpatterns = [
    path('magazine-feed/', views.magazine_feed),
    path('archived-magazine/', views.archived_magazine),
    path('read-blog/', views.read_blog),
    path('read-user-blogs/', views.user_blogs),
    path('read-user-rejected-blogs/', views.user_rejected_blogs),
    path('read-drafts/', views.user_drafts),
    path('create-blog/', views.create_blog),
    path('update-blog/', views.update_blog),
    path('delete-blog/', views.delete_blog),
    path('delete-file/', views.delete_file),
    path('add-reader/', views.new_reader),
]


