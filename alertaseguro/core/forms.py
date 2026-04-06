from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from .models import Feedback

class RegistoForm(forms.ModelForm):
    password = forms.CharField(
        label="Palavra-passe",
        widget=forms.PasswordInput(attrs={
            'class': 'w-full p-[12px] rounded-[12px] bg-gray-100 focus:bg-white focus:outline-none focus:ring-2 focus:ring-red-400 transition',
            'placeholder': 'Digite a sua palavra-passe'
        })
    )

    confirmar_password = forms.CharField(
        label="Confirmar palavra-passe",
        widget=forms.PasswordInput(attrs={
            'class': 'w-full p-[12px] rounded-[12px] bg-gray-100 focus:bg-white focus:outline-none focus:ring-2 focus:ring-red-400 transition',
            'placeholder': 'Confirme a palavra-passe'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'w-full p-[12px] rounded-[12px] bg-gray-100 focus:bg-white focus:outline-none focus:ring-2 focus:ring-red-400 transition',
                'placeholder': 'Nome de utilizador'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full p-[12px] rounded-[12px] bg-gray-100 focus:bg-white focus:outline-none focus:ring-2 focus:ring-red-400 transition',
                'placeholder': 'Email'
            }),
        }

        help_texts = {
            'username': '',
        }

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

class LoginForm(forms.Form):
    username = forms.CharField(
        label="Email ou utilizador",
        widget=forms.TextInput(attrs={
            'class': 'w-full p-[12px] rounded-[12px] bg-gray-100 focus:bg-white focus:outline-none focus:ring-2 focus:ring-red-400 transition',
            'placeholder': 'Email ou utilizador'
        })
    )

    password = forms.CharField(
        label="Palavra-passe",
        widget=forms.PasswordInput(attrs={
            'class': 'w-full p-[12px] rounded-[12px] bg-gray-100 focus:bg-white focus:outline-none focus:ring-2 focus:ring-red-400 transition',
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
            raise forms.ValidationError("Credenciais inválidas")

        self.user = user
        return cleaned

class EditarPerfilForm(forms.ModelForm):
    password = forms.CharField(
        label="Nova palavra-passe",
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'w-full p-[12px] rounded-[12px] bg-gray-100 focus:bg-white focus:outline-none focus:ring-2 focus:ring-red-400 transition',
            'placeholder': 'Nova palavra-passe'
        })
    )

    class Meta:
        model = User
        fields = ['email']

        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'w-full p-[12px] rounded-[12px] bg-gray-100 focus:bg-white focus:outline-none focus:ring-2 focus:ring-red-400 transition',
                'placeholder': 'Email'
            }),
        }

    def save(self, commit=True):
        user = super().save(commit=False)

        password = self.cleaned_data.get("password")
        if password:
            user.set_password(password) 

        if commit:
            user.save()

        return user

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
    


