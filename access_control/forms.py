"""
Formulários do painel administrativo.
"""

from django import forms
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from accounts.models import User
from .models import AdminProfile, CountryPermission, COUNTRY_CHOICES
from adminpanel.models import LdapDirectory


# ============================================
# FORMULÁRIO DE CONFIGURAÇÃO LDAP/AD
# ============================================

class LdapConfigForm(forms.ModelForm):
    """
    Formulário para configuração do Active Directory (LDAP).
    Permite admin de país configurar seu próprio AD.
    """
    
    # Campo extra para senha (não criptografada no formulário)
    bind_password = forms.CharField(
        label=_('Senha do Bind DN'),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('Digite a senha do usuário de bind')
        }),
        required=False,
        help_text=_('Senha do usuário que será usado para conectar ao AD. Deixe em branco para manter a senha atual.')
    )
    
    class Meta:
        model = LdapDirectory
        fields = [
            'name',
            'ldap_server',
            'port',
            'use_ssl',
            'use_tls',
            'bind_user_dn',
            'base_dn',
            'user_search_base',
            'search_filter',
            'attr_first_name',
            'attr_last_name',
            'attr_email',
            'is_active'
        ]
        
        labels = {
            'name': _('Nome da Configuração'),
            'ldap_server': _('Servidor LDAP'),
            'port': _('Porta'),
            'use_ssl': _('Usar SSL (LDAPS)'),
            'use_tls': _('Usar START_TLS'),
            'bind_user_dn': _('User DN para Bind'),
            'base_dn': _('Base DN'),
            'user_search_base': _('Base de Busca de Usuários'),
            'search_filter': _('Filtro de Busca LDAP'),
            'attr_first_name': _('Atributo: Primeiro Nome'),
            'attr_last_name': _('Atributo: Sobrenome'),
            'attr_email': _('Atributo: E-mail'),
            'is_active': _('Ativo'),
        }
        
        help_texts = {
            'name': _('Nome descritivo para esta configuração. Ex: Active Directory - Brasil'),
            'ldap_server': _('Endereço do servidor LDAP/AD. Ex: ad.empresa.com ou 192.168.1.10'),
            'port': _('Porta do servidor LDAP. Padrão: 389 (sem SSL) ou 636 (com SSL)'),
            'use_ssl': _('Use SSL (LDAPS) na porta 636'),
            'use_tls': _('Use START_TLS na porta 389'),
            'bind_user_dn': _('DN completo do usuário de serviço. Ex: CN=Admin,CN=Users,DC=empresa,DC=com'),
            'base_dn': _('DN base para buscas. Ex: DC=empresa,DC=com'),
            'user_search_base': _('Base específica para buscar usuários. Deixe vazio para usar Base DN'),
            'search_filter': _('Filtro LDAP para buscar usuários. Use {username} como placeholder. Ex: (sAMAccountName={username})'),
            'attr_first_name': _('Nome do atributo LDAP para primeiro nome (padrão: givenName)'),
            'attr_last_name': _('Nome do atributo LDAP para sobrenome (padrão: sn)'),
            'attr_email': _('Nome do atributo LDAP para e-mail (padrão: mail)'),
            'is_active': _('Desmarque para desativar temporariamente esta configuração'),
        }
        
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Active Directory - Brasil'
            }),
            'ldap_server': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ad.empresa.com'
            }),
            'port': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '389'
            }),
            'use_ssl': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'use_tls': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'bind_user_dn': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'CN=Admin,CN=Users,DC=empresa,DC=com'
            }),
            'base_dn': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'DC=empresa,DC=com'
            }),
            'user_search_base': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Deixe vazio para usar Base DN'
            }),
            'search_filter': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '(sAMAccountName={username})'
            }),
            'attr_first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'givenName'
            }),
            'attr_last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'sn'
            }),
            'attr_email': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'mail'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        """Construtor customizado para ajustar campos dinamicamente."""
        super().__init__(*args, **kwargs)
        
        if self.instance and self.instance.pk:
            self.fields['bind_password'].required = False
            self.fields['bind_password'].help_text = _(
                'Deixe em branco para manter a senha atual. '
                'Preencha apenas se desejar alterar a senha.'
            )
        else:
            self.fields['bind_password'].required = True
            self.fields['bind_password'].help_text = _(
                'Digite a senha do usuário que será usado para conectar ao Active Directory.'
            )
        
        if not self.instance.pk:
            self.fields['port'].initial = 389
            self.fields['use_ssl'].initial = False
            self.fields['use_tls'].initial = False
            self.fields['is_active'].initial = True
            self.fields['search_filter'].initial = '(sAMAccountName={username})'
            self.fields['attr_first_name'].initial = 'givenName'
            self.fields['attr_last_name'].initial = 'sn'
            self.fields['attr_email'].initial = 'mail'
    
    def clean_ldap_server(self):
        """Validação customizada para o campo servidor."""
        server = self.cleaned_data.get('ldap_server', '').strip()
        if not server:
            raise forms.ValidationError(_('O servidor é obrigatório.'))
        server = server.replace('ldap://', '').replace('ldaps://', '')
        return server
    
    def clean_port(self):
        """Validação da porta LDAP."""
        port = self.cleaned_data.get('port')
        if not port:
            raise forms.ValidationError(_('A porta é obrigatória.'))
        if port < 1 or port > 65535:
            raise forms.ValidationError(_('A porta deve estar entre 1 e 65535.'))
        return port
    
    def clean_bind_user_dn(self):
        """Validação do Bind User DN."""
        bind_user_dn = self.cleaned_data.get('bind_user_dn', '').strip()
        if not bind_user_dn:
            raise forms.ValidationError(_('O User DN para Bind é obrigatório.'))
        if 'DC=' not in bind_user_dn.upper():
            raise forms.ValidationError(
                _('O User DN deve conter pelo menos um componente DC (Domain Component). '
                  'Exemplo: CN=Admin,CN=Users,DC=empresa,DC=com')
            )
        return bind_user_dn
    
    def clean_base_dn(self):
        """Validação do Base DN."""
        base_dn = self.cleaned_data.get('base_dn', '').strip()
        if not base_dn:
            raise forms.ValidationError(_('O Base DN é obrigatório.'))
        if 'DC=' not in base_dn.upper():
            raise forms.ValidationError(
                _('O Base DN deve conter pelo menos um componente DC (Domain Component). '
                  'Exemplo: DC=empresa,DC=com')
            )
        return base_dn
    
    def clean(self):
        """Validação geral do formulário."""
        cleaned_data = super().clean()
        use_ssl = cleaned_data.get('use_ssl')
        use_tls = cleaned_data.get('use_tls')
        port = cleaned_data.get('port')
        
        if use_ssl and use_tls:
            raise forms.ValidationError(
                _('Não é possível usar SSL e TLS simultaneamente. Escolha apenas um.')
            )
        
        if use_ssl and port == 389:
            self.add_error('port', _(
                'Atenção: Você marcou "Usar SSL", mas a porta 389 é geralmente usada sem SSL. '
                'Considere usar a porta 636 para conexões SSL.'
            ))
        
        if not use_ssl and port == 636:
            self.add_error('port', _(
                'Atenção: Você desmarcou "Usar SSL", mas a porta 636 é geralmente usada com SSL. '
                'Considere usar a porta 389 para conexões sem SSL ou marque "Usar SSL".'
            ))
        
        return cleaned_data


# ============================================
# FORMULÁRIO DE CRIAÇÃO DE ADMIN DE PAÍS
# ============================================

class CreateCountryAdminForm(forms.Form):
    """Formulário para criar um novo país e seu admin responsável."""
    
    country_code = forms.ChoiceField(
        label=_("País"),
        choices=COUNTRY_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control', 'required': True})
    )
    
    first_name = forms.CharField(
        label=_("Nome"),
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Ex: Mario'), 'required': True})
    )
    
    last_name = forms.CharField(
        label=_("Sobrenome"),
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Ex: Rossi'), 'required': True})
    )
    
    email = forms.EmailField(
        label=_("Email"),
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': _('Ex: mario@ilpea.it'), 'required': True})
    )
    
    username = forms.CharField(
        label=_("Username"),
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Ex: admin_it'), 'required': True})
    )
    
    password = forms.CharField(
        label=_("Senha Inicial"),
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': _('Mínimo 8 caracteres'), 'required': True})
    )
    
    password_confirm = forms.CharField(
        label=_("Confirmar Senha"),
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': _('Digite a senha novamente'), 'required': True})
    )
    
    can_configure_ad = forms.BooleanField(
        label=_("Pode configurar Active Directory próprio"),
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    can_configure_smtp = forms.BooleanField(
        label=_("Pode configurar SMTP próprio"),
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        help_text=_("Se desmarcado, usará o SMTP Global")
    )
    
    can_sync_ad_groups = forms.BooleanField(
        label=_("Pode sincronizar grupos do AD"),
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    can_assign_permissions = forms.BooleanField(
        label=_("Pode atribuir permissões"),
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    can_manage_local_users = forms.BooleanField(
        label=_("Pode gerenciar usuários locais"),
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    can_manage_suppliers = forms.BooleanField(
        label=_("Pode gerenciar fornecedores"),
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    can_manage_contracts = forms.BooleanField(
        label=_("Pode gerenciar contratos"),
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    can_manage_quality = forms.BooleanField(
        label=_("Pode gerenciar qualidade"),
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    def clean_country_code(self):
        """Valida se o país já não tem admin."""
        country_code = self.cleaned_data['country_code']
        if AdminProfile.objects.filter(country_code=country_code, access_level='country_admin').exists():
            raise ValidationError(_('Já existe um administrador para este país. Edite o existente.'))
        return country_code
    
    def clean_username(self):
        """Valida se o username já não existe."""
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise ValidationError(_('Este username já está em uso.'))
        return username
    
    def clean_email(self):
        """Valida se o email já não existe."""
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise ValidationError(_('Este email já está em uso.'))
        return email
    
    def clean(self):
        """Validações gerais."""
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        
        if password and password_confirm:
            if password != password_confirm:
                raise ValidationError({'password_confirm': _('As senhas não coincidem.')})
            try:
                validate_password(password)
            except ValidationError as e:
                raise ValidationError({'password': e})
        
        return cleaned_data