from django import forms
from .models import LdapConfig, SmtpConfig, SslConfig

class LdapConfigForm(forms.ModelForm):
    bind_password = forms.CharField(widget=forms.PasswordInput(), required=False)

    class Meta:
        model = LdapConfig
        fields = ['host', 'base_dn', 'bind_user', 'bind_password', 'group_search']


class SmtpConfigForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(), required=False)

    class Meta:
        model = SmtpConfig
        fields = ['host', 'port', 'username', 'password', 'use_ssl', 'use_tls']


class SslConfigForm(forms.ModelForm):
    class Meta:
        model = SslConfig
        fields = ['cert_file', 'key_file']
