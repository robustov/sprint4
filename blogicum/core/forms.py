from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

User = get_user_model()


class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email"]


class UserEditForm(UserChangeForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]
