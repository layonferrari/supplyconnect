from django import forms
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from .models import User

class PartnerLoginForm(forms.Form):
    email = forms.EmailField(
        label="E-mail",
        widget=forms.EmailInput(attrs={
            "placeholder": "Digite seu e-mail"
        })
    )
    password = forms.CharField(
        label="Senha",
        widget=forms.PasswordInput(attrs={
            "placeholder": "Digite sua senha"
        })
    )


class UserLanguagePreferenceForm(forms.ModelForm):
    
    class Meta:
        model = User
        fields = ['preferred_language']
        widgets = {
            'preferred_language': forms.Select(attrs={
                'class': 'language-select'
            })
        }
        labels = {
            'preferred_language': 'Idioma Preferido'
        }


class CollaboratorLoginForm(forms.Form):
    country_code = forms.ChoiceField(
        label=_("País"),
        choices=[],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    username = forms.CharField(
        label=_("Usuário"),
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Seu usuário'),
            'autocomplete': 'username',
            'required': True
        })
    )
    password = forms.CharField(
        label=_("Senha"),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '••••••••',
            'autocomplete': 'current-password',
            'required': True
        })
    )
    
    def __init__(self, data=None, files=None, available_countries=None, **kwargs):
        super(CollaboratorLoginForm, self).__init__(data=data, files=files, **kwargs)
        if available_countries:
            self.fields['country_code'].choices = available_countries