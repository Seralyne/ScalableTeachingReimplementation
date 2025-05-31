from django import forms 
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class SignupForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update({
            'required': '',
            'name': 'username',
            'class': 'form-control',
            'id': 'username',
            'aria-describedby': 'usernameHelp'

        })
        self.fields["password1"].widget.attrs.update({
            'required': '',
            'type': 'password',
            'name': 'password1',
            'class': 'form-control',
            'id': 'password1',
            'aria-describedby': 'passwordHelp'

        })
        self.fields["password2"].widget.attrs.update({
            'required': '',
            'type': 'password',
            'name': 'password2',
            'class': 'form-control',
            'id': 'password2',
            'aria-describedby': 'password2Help'

        })

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']
