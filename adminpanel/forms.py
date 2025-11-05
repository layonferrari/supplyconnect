# adminpanel/forms.py
# ==========================================================
# FORMULÁRIOS DO ADMINPANEL - VERSÃO SIMPLIFICADA
# ==========================================================

from django import forms
from .models import LdapDirectory, SmtpConfiguration, SslConfig


# ==========================================================
# 🔐 ACTIVE DIRECTORY (SIMPLIFICADO)
# ==========================================================
class LdapDirectoryForm(forms.ModelForm):
    """
    Formulário simplificado de configuração do Active Directory.
    Apenas os campos essenciais: Servidor, Porta, Usuário, Senha e Base DN.
    """
    bind_password = forms.CharField(
        label="Senha AD",
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Digite a senha da conta de serviço..."
        }),
        required=False,
    )

    class Meta:
        model = LdapDirectory
        fields = ['ldap_server', 'port', 'bind_user_dn', 'base_dn']
        labels = {
            'ldap_server': 'Servidor AD',
            'port': 'Porta',
            'bind_user_dn': 'Usuário AD',
            'base_dn': 'Base DN',
        }
        widgets = {
            'ldap_server': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: BR.ILPEAORG.COM'
            }),
            'port': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '389'
            }),
            'bind_user_dn': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: admin@BR.ILPEAORG.COM'
            }),
            'base_dn': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: DC=br,DC=ilpeaorg,DC=com'
            }),
        }


# ==========================================================
# ✉️ CONFIGURAÇÃO SMTP
# ==========================================================
class SmtpConfigurationForm(forms.ModelForm):
    """Formulário de configuração do servidor SMTP."""
    password = forms.CharField(
        label="Senha do E-mail",
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Digite a senha do e-mail..."
        }),
        required=False,
    )

    class Meta:
        model = SmtpConfiguration
        fields = ['host', 'port', 'username', 'password', 'use_ssl', 'use_tls']
        labels = {
            'host': 'Servidor SMTP',
            'port': 'Porta',
            'username': 'E-mail de Envio',
            'password': 'Senha',
            'use_ssl': 'Usar SSL',
            'use_tls': 'Usar TLS',
        }
        widgets = {
            'host': forms.TextInput(attrs={'class': 'form-control'}),
            'port': forms.NumberInput(attrs={'class': 'form-control'}),
            'username': forms.EmailInput(attrs={'class': 'form-control'}),
            'use_ssl': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'use_tls': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


# ==========================================================
# 🔒 SSL
# ==========================================================
class SslConfigForm(forms.ModelForm):
    class Meta:
        model = SslConfig
        fields = ['cert_file', 'key_file']
        widgets = {
            'cert_file': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'key_file': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        }
