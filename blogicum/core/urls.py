from . import views
from django.urls import path

urlpatterns = [
    path("auth/registration/", views.registration, name="registration"),
    path("accounts/profile/", views.accounts_profile, name="profile"),
]
