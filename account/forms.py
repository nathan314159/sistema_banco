from django import forms
from banco_america.models import Client, Address
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        self.client = kwargs.pop('client', None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        user = super().save(commit=False)
        if self.client:
            username = self.client.create_user()
            password = self.client.code_generator()  # Replace with your password generation logic
            user.username = username
            user.set_password(password)
            user.email = self.client.email
        if commit:
            user.save()
        return user
    



