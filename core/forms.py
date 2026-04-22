from django import forms
from django.contrib.auth.models import User
from .models import Project

class UserRegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

    def clean_password_confirm(self):
        pw1 = self.cleaned_data.get('password')
        pw2 = self.cleaned_data.get('password_confirm')
        if pw1 != pw2:
            raise forms.ValidationError("Passwords do not match")
        return pw2

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description']