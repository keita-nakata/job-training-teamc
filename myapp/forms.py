from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class SimpleSignUpForm(UserCreationForm):
    class Meta:
        model = User
        # We only ask for username; password1 & password2 come from UserCreationForm.
        fields = ["username"]
