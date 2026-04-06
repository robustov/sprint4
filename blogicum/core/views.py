from django.http import HttpRequest
from django.shortcuts import redirect, render
from django.contrib.auth import login, get_user_model

from .forms import UserRegistrationForm

User = get_user_model()


# Create your views here.
def registration(request: HttpRequest):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("blog:index")
    else:
        form = UserRegistrationForm()
    return render(
        request, "registration/registration_form.html", {"form": form}
    )


def accounts_profile(request: HttpRequest):
    return redirect("blog:profile", request.user.username)
