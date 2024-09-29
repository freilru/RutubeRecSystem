from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    age = forms.IntegerField(required=False, label="Возраст (не обязательно)")
    gender = forms.BooleanField(required=False, label="Пол М - 0 Ж - 1 (не обязательно)")

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = UserCreationForm.Meta.fields + ('age', 'gender')

class CustomAuthenticationForm(AuthenticationForm):
    class Meta:
        model = CustomUser
