from django.urls import path
from . import views

app_name = "blog"

urlpatterns = [
    path("", views.index, name="index"),
    path("posts/<int:id>/", views.post_detail, name="post_detail"),
    path("posts/create/", views.CreatePost.as_view(), name="create_post"),
    path("posts/<int:pk>/edit/", views.EditPost.as_view(), name="edit_post"),
    path(
        "posts/<int:pk>/delete/",
        views.DeletePost.as_view(),
        name="delete_post",
    ),
    path(
        "category/<slug:category_slug>/",
        views.category_posts,
        name="category_posts",
    ),
    path("profile/<str:username>/", views.profile, name="profile"),
    path("edit-profile/", views.edit_profile, name="edit_profile"),
    path(
        "posts/<int:post_id>/add_comment/",
        views.add_comment,
        name="add_comment",
    ),
    path(
        "posts/<int:post_id>/edit_comment/<int:pk>/",
        views.EditComment.as_view(),
        name="edit_comment",
    ),
    path(
        "posts/<int:post_id>/delete_comment/<int:pk>/",
        views.DeleteComment.as_view(),
        name="delete_comment",
    ),
]
