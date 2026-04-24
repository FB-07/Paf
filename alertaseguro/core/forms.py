from django import forms
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from .models import Feedback
import re


# -------------------------
# REGISTO
# -------------------------
class RegistoForm(forms.ModelForm):
    username = forms.CharField(
        max_length=12,
        label="Nome de utilizador",
        widget=forms.TextInput(attrs={
            'class': 'w-full p-[12px] rounded-[12px] bg-gray-100 focus:bg-white focus:outline-none focus:ring-2 focus:ring-red-400 transition',
            'placeholder': 'Nome de utilizador'
        })
    )

    password = forms.CharField(
        label="Palavra-passe",
        widget=forms.PasswordInput(attrs={
            'class': 'w-full',
            'placeholder': 'Digite a sua palavra-passe'
        })
    )

    confirmar_password = forms.CharField(
        label="Confirmar palavra-passe",
        widget=forms.PasswordInput(attrs={
            'class': 'w-full',
            'placeholder': 'Confirme a palavra-passe'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'w-full p-[12px] rounded-[12px] bg-gray-100 focus:bg-white focus:outline-none focus:ring-2 focus:ring-red-400 transition',
                'placeholder': 'Email'
            }),
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')

        if len(username) > 15:
            raise ValidationError("Máximo 15 caracteres.")

        if User.objects.filter(username=username).exists():
            raise ValidationError("Este nome de utilizador já existe.")

        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')

        if email and User.objects.filter(email=email).exists():
            raise ValidationError("Este email já está em uso.")

        return email

    def clean_password(self):
        password = self.cleaned_data.get('password')

        if len(password) < 6:
            raise ValidationError("Mínimo 6 caracteres.")

        if not re.search(r'\d', password):
            raise ValidationError("Deve conter pelo menos um número.")

        if not re.search(r'[!@#$%^&*(),.?\":{}|<>]', password):
            raise ValidationError("Deve conter pelo menos um carácter especial.")

        return password

    def clean(self):
        cleaned = super().clean()

        p1 = cleaned.get("password")
        p2 = cleaned.get("confirmar_password")

        if p1 and p2 and p1 != p2:
            self.add_error('confirmar_password', "As palavras-passe não coincidem!")

        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])

        if commit:
            user.save()

        return user

# -------------------------
# LOGIN
# -------------------------
class LoginForm(forms.Form):
    username = forms.CharField(
        label="Email ou utilizador",
        widget=forms.TextInput(attrs={
            'class': 'w-full p-[12px] rounded-[12px] bg-gray-100 focus:bg-white focus:outline-none focus:ring-2 focus:ring-red-400 transition',
            'placeholder': 'Email ou utilizador'
        })
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full',
            'placeholder': 'Palavra-passe'
        })
    )

    def clean(self):
        cleaned = super().clean()
        identifier = cleaned.get("username")
        password = cleaned.get("password")

        user = authenticate(username=identifier, password=password)

        if not user:
            try:
                user_obj = User.objects.get(email=identifier)
                user = authenticate(username=user_obj.username, password=password)
            except User.DoesNotExist:
                user = None

        if not user:
            raise ValidationError("Credenciais inválidas")

        self.user = user
        return cleaned

# -------------------------
# EDITAR PERFIL
# -------------------------
class EditarPerfilForm(forms.ModelForm):
    password_atual = forms.CharField(
        label="Palavra-passe atual",
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'w-full',
            'placeholder': 'Palavra-passe atual'
        })
    )

    password = forms.CharField(
        label="Nova palavra-passe",
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'w-full',
            'placeholder': 'Nova palavra-passe'
        })
    )

    confirmar_password = forms.CharField(
        label="Confirmar nova palavra-passe",
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'w-full',
            'placeholder': 'Confirmar nova palavra-passe'
        })
    )

    username = forms.CharField(
        max_length=12,
        label="Nome de utilizador",
        widget=forms.TextInput(attrs={
            'class': 'w-full p-[12px] rounded-[12px] bg-gray-100 focus:bg-white focus:outline-none focus:ring-2 focus:ring-red-400 transition',
            'placeholder': 'Nome de utilizador'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'w-full p-[12px] rounded-[12px] bg-gray-100 focus:bg-white focus:outline-none focus:ring-2 focus:ring-red-400 transition',
                'placeholder': 'Email'
            }),
        }

    def clean_password_atual(self):
        password_atual = self.cleaned_data.get("password_atual")

        if password_atual and not self.instance.check_password(password_atual):
            raise ValidationError("Palavra-passe atual incorreta.")

        return password_atual

    def clean_password(self):
        password = self.cleaned_data.get("password")

        if password:
            if len(password) < 6:
                raise ValidationError("Mínimo 6 caracteres.")

            if not re.search(r'\d', password):
                raise ValidationError("Deve conter pelo menos um número.")

            if not re.search(r'[!@#$%^&*(),.?\":{}|<>]', password):
                raise ValidationError("Deve conter pelo menos um carácter especial.")

        return password

    def clean_username(self):
        username = self.cleaned_data.get('username')

        if username and User.objects.filter(username=username).exclude(pk=self.instance.pk).exists():
            raise ValidationError("Este username já existe.")

        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')

        if email and User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError("Este email já está em uso.")

        return email

    def clean(self):
        cleaned = super().clean()

        p1 = cleaned.get("password")
        p2 = cleaned.get("confirmar_password")
        password_atual = cleaned.get("password_atual")

        if p1 or p2:
            if not password_atual:
                self.add_error("password_atual", "Tem de introduzir a palavra-passe atual.")

            if p1 != p2:
                self.add_error("confirmar_password", "As palavras-passe não coincidem!")

        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)

        user.username = self.cleaned_data.get("username", user.username)
        user.email = self.cleaned_data.get("email", user.email)

        password = self.cleaned_data.get("password")
        if password:
            user.set_password(password)

        if commit:
            user.save()

        return user

# -------------------------
# FEEDBACK
# -------------------------
class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['tipo', 'pagina', 'titulo', 'descricao']

        widgets = {
            'tipo': forms.Select(attrs={
                'class': 'w-full p-[12px] rounded-[12px] bg-gray-100 focus:bg-white focus:outline-none focus:ring-2 focus:ring-red-400 transition'
            }),
            'pagina': forms.Select(attrs={
                'class': 'w-full p-[12px] rounded-[12px] bg-gray-100 focus:bg-white focus:outline-none focus:ring-2 focus:ring-red-400 transition'
            }),
            'titulo': forms.TextInput(attrs={
                'class': 'w-full p-[12px] rounded-[12px] bg-gray-100 focus:bg-white focus:outline-none focus:ring-2 focus:ring-red-400 transition',
                'placeholder': 'Título'
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'w-full p-[12px] rounded-[12px] bg-gray-100 focus:bg-white focus:outline-none focus:ring-2 focus:ring-red-400 transition',
                'placeholder': 'Descrição'
            }),
        }

        labels = {
            'tipo': 'Tipo',
            'pagina': 'Página',
            'titulo': 'Título',
            'descricao': 'Descrição',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tipo'].required = True
        self.fields['titulo'].required = True
        self.fields['descricao'].required = True