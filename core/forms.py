from django import forms
from django.contrib.auth.models import User
from .models import Project

class UserRegisterForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput, 
        label="Senha"
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput, 
        label="Confirmar Senha"
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password']
        labels = {
            'username': 'Nome de Usuário',
            'first_name': 'Nome',
            'last_name': 'Sobrenome',
            'email': 'E-mail',
        }

    def clean_password_confirm(self):
        pw1 = self.cleaned_data.get('password')
        pw2 = self.cleaned_data.get('password_confirm')
        if pw1 != pw2:
            raise forms.ValidationError("As senhas não coincidem")
        return pw2

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description']
        labels = {
            'name': 'Nome do Projeto',
            'description': 'Descrição',
        }