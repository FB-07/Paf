from django import forms
from django.contrib.auth.models import User

class RegistoForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirmar_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get("password")
        p2 = cleaned.get("confirmar_password")

        if p1 != p2:
            raise forms.ValidationError("As palavras-passe não coincidem!")

        return cleaned
