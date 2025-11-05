"""
Formulários do painel administrativo.
"""

from django import forms
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from accounts.models import User
from .models import AdminProfile, CountryPermission, SystemDefaultConfig, COUNTRY_CHOICES
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
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input', 'id': 'id_can_configure_ad'})
    )
    
    ad_config_type = forms.ChoiceField(
        label=_("Se NÃO pode configurar AD, usar:"),
        choices=[
            ('manual', _('Configuração Manual (você definirá agora)')),
            ('system_default', _('Padrão do Sistema (config global)')),
        ],
        required=False,
        initial='system_default',
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        help_text=_("Esta opção só será usada se desmarcar 'Pode configurar AD próprio'")
    )
    
    can_configure_smtp = forms.BooleanField(
        label=_("Pode configurar SMTP próprio"),
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input', 'id': 'id_can_configure_smtp'}),
        help_text=_("Se desmarcado, usará SMTP Manual ou Global")
    )
    
    smtp_config_type = forms.ChoiceField(
        label=_("Se NÃO pode configurar SMTP, usar:"),
        choices=[
            ('manual', _('Configuração Manual (você definirá agora)')),
            ('system_default', _('Padrão do Sistema (config global)')),
        ],
        required=False,
        initial='system_default',
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        help_text=_("Esta opção só será usada se desmarcar 'Pode configurar SMTP próprio'")
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


# ============================================
# FORMULÁRIO PARA CONFIGURAÇÃO PADRÃO DO SISTEMA
# ============================================

class SystemDefaultConfigForm(forms.ModelForm):
    """
    Formulário simplificado para configurar AD e SMTP padrão do sistema.
    """
    
    # Campos extras para senhas (não criptografadas no form)
    ad_bind_password_input = forms.CharField(
        label=_('Senha do Bind AD'),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('Digite a senha (deixe vazio para manter atual)')
        }),
        required=False,
        help_text=_('Senha para conectar ao AD. Deixe em branco para manter a atual.')
    )
    
    smtp_password_input = forms.CharField(
        label=_('Senha SMTP'),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('Digite a senha (deixe vazio para manter atual)')
        }),
        required=False,
        help_text=_('Senha do servidor SMTP. Deixe em branco para manter a atual.')
    )
    
    class Meta:
        model = SystemDefaultConfig
        fields = [
            # AD
            'ad_enabled',
            'ad_server',
            'ad_port',
            'ad_use_ssl',
            'ad_use_tls',
            'ad_bind_user_dn',
            'ad_base_dn',
            'ad_user_search_base',
            'ad_search_filter',
            # SMTP
            'smtp_enabled',
            'smtp_host',
            'smtp_port',
            'smtp_use_tls',
            'smtp_username',
            'smtp_from_email',
        ]
        
        widgets = {
            # AD Fields
            'ad_enabled': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'ad_server': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ex: ad.empresa.com'
            }),
            'ad_port': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '389'
            }),
            'ad_use_ssl': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'ad_use_tls': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'ad_bind_user_dn': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'CN=Admin,CN=Users,DC=empresa,DC=com'
            }),
            'ad_base_dn': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'DC=empresa,DC=com'
            }),
            'ad_user_search_base': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'OU=Users,DC=empresa,DC=com'
            }),
            'ad_search_filter': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '(sAMAccountName={username})'
            }),
            
            # SMTP Fields
            'smtp_enabled': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'smtp_host': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ex: smtp.gmail.com'
            }),
            'smtp_port': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '587'
            }),
            'smtp_use_tls': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'smtp_username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'usuario@empresa.com'
            }),
            'smtp_from_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'noreply@empresa.com'
            }),
        }
        
        labels = {
            'ad_enabled': _('Ativar AD Padrão'),
            'ad_server': _('Servidor AD'),
            'ad_port': _('Porta'),
            'ad_use_ssl': _('Usar SSL (LDAPS)'),
            'ad_use_tls': _('Usar START_TLS'),
            'ad_bind_user_dn': _('User DN para Bind'),
            'ad_base_dn': _('Base DN'),
            'ad_user_search_base': _('Base de Busca'),
            'ad_search_filter': _('Filtro LDAP'),
            
            'smtp_enabled': _('Ativar SMTP Padrão'),
            'smtp_host': _('Servidor SMTP'),
            'smtp_port': _('Porta SMTP'),
            'smtp_use_tls': _('Usar TLS'),
            'smtp_username': _('Usuário SMTP'),
            'smtp_from_email': _('Email Remetente'),
        }
        
        help_texts = {
            'ad_enabled': _('Ative para que países possam usar este AD como padrão'),
            'ad_server': _('Endereço do servidor LDAP/AD'),
            'ad_port': _('Porta padrão: 389 (sem SSL) ou 636 (com SSL)'),
            'ad_use_ssl': _('Use LDAPS na porta 636'),
            'ad_use_tls': _('Use START_TLS na porta 389 (não use com SSL)'),
            'ad_bind_user_dn': _('DN completo do usuário de serviço'),
            'ad_base_dn': _('DN base para todas as buscas'),
            'ad_user_search_base': _('Base específica para buscar usuários (opcional)'),
            'ad_search_filter': _('Use {username} como placeholder. Ex: (sAMAccountName={username})'),
            
            'smtp_enabled': _('Ative para que países possam usar este SMTP como padrão'),
            'smtp_host': _('Endereço do servidor SMTP'),
            'smtp_port': _('Porta padrão: 587 (TLS), 465 (SSL) ou 25'),
            'smtp_use_tls': _('Ative para conexões seguras (recomendado)'),
            'smtp_username': _('Usuário para autenticação SMTP'),
            'smtp_from_email': _('Email que aparecerá como remetente'),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Se está editando, senhas não são obrigatórias
        if self.instance and self.instance.pk:
            self.fields['ad_bind_password_input'].required = False
            self.fields['smtp_password_input'].required = False
    
    def clean(self):
        """Validações do formulário."""
        cleaned_data = super().clean()
        
        # Validação AD
        ad_enabled = cleaned_data.get('ad_enabled')
        if ad_enabled:
            ad_server = cleaned_data.get('ad_server')
            ad_bind_user_dn = cleaned_data.get('ad_bind_user_dn')
            ad_base_dn = cleaned_data.get('ad_base_dn')
            
            if not ad_server:
                self.add_error('ad_server', _('Servidor AD é obrigatório quando AD está ativo'))
            if not ad_bind_user_dn:
                self.add_error('ad_bind_user_dn', _('User DN é obrigatório quando AD está ativo'))
            if not ad_base_dn:
                self.add_error('ad_base_dn', _('Base DN é obrigatório quando AD está ativo'))
            
            # Senha obrigatória apenas na criação
            if not self.instance.pk:
                if not cleaned_data.get('ad_bind_password_input'):
                    self.add_error('ad_bind_password_input', _('Senha AD é obrigatória na primeira configuração'))
        
        # Validação SMTP
        smtp_enabled = cleaned_data.get('smtp_enabled')
        if smtp_enabled:
            smtp_host = cleaned_data.get('smtp_host')
            smtp_username = cleaned_data.get('smtp_username')
            smtp_from_email = cleaned_data.get('smtp_from_email')
            
            if not smtp_host:
                self.add_error('smtp_host', _('Servidor SMTP é obrigatório quando SMTP está ativo'))
            if not smtp_username:
                self.add_error('smtp_username', _('Usuário SMTP é obrigatório quando SMTP está ativo'))
            if not smtp_from_email:
                self.add_error('smtp_from_email', _('Email remetente é obrigatório quando SMTP está ativo'))
            
            # Senha obrigatória apenas na criação
            if not self.instance.pk:
                if not cleaned_data.get('smtp_password_input'):
                    self.add_error('smtp_password_input', _('Senha SMTP é obrigatória na primeira configuração'))
        
        # Validação SSL/TLS AD
        ad_use_ssl = cleaned_data.get('ad_use_ssl')
        ad_use_tls = cleaned_data.get('ad_use_tls')
        if ad_use_ssl and ad_use_tls:
            raise forms.ValidationError(_('Não é possível usar SSL e TLS simultaneamente no AD'))
        
        return cleaned_data
    
    def save(self, commit=True):
        """Salva o formulário tratando as senhas."""
        instance = super().save(commit=False)
        
        # Processar senha AD se fornecida
        ad_password = self.cleaned_data.get('ad_bind_password_input')
        if ad_password:
            # TODO: Criptografar a senha antes de salvar
            instance.ad_bind_password = ad_password
        
        # Processar senha SMTP se fornecida
        smtp_password = self.cleaned_data.get('smtp_password_input')
        if smtp_password:
            # TODO: Criptografar a senha antes de salvar
            instance.smtp_password = smtp_password
        
        if commit:
            instance.save()
        
        return instance

class ADUserPermissionsForm(forms.ModelForm):
    """Formulário para editar permissões individuais de um usuário do AD."""
    
    class Meta:
        model = None  # Será definido dinamicamente
        fields = [
            'can_login',
            'can_register_suppliers',
            'can_handle_complaints',
            'can_view_dashboards',
            'can_view_contracts',
            'can_manage_contracts',
        ]
        
        labels = {
            'can_login': _('Pode Fazer Login'),
            'can_register_suppliers': _('Pode Cadastrar Fornecedores'),
            'can_handle_complaints': _('Pode Tratar Reclamações'),
            'can_view_dashboards': _('Pode Visualizar Dashboards'),
            'can_view_contracts': _('Pode Visualizar Contratos'),
            'can_manage_contracts': _('Pode Gerenciar Contratos'),
        }
        
        widgets = {
            'can_login': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'can_register_suppliers': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'can_handle_complaints': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'can_view_dashboards': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'can_view_contracts': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'can_manage_contracts': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        
        help_texts = {
            'can_login': _('Permite que o usuário faça login no sistema'),
            'can_register_suppliers': _('Permite cadastrar novos fornecedores'),
            'can_handle_complaints': _('Permite visualizar e gerenciar reclamações'),
            'can_view_dashboards': _('Permite acessar os dashboards do sistema'),
            'can_view_contracts': _('Permite visualizar contratos existentes'),
            'can_manage_contracts': _('Permite criar, editar e excluir contratos'),
        }
    
    def __init__(self, *args, **kwargs):
        # Importar ADUser dinamicamente para evitar circular import
        from .models import ADUser
        self._meta.model = ADUser
        super().__init__(*args, **kwargs)


class AdminLoginForm(forms.Form):
    """Formulário de login para administradores (Global e País)."""
    
    username = forms.CharField(
        label='Usuário',
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite seu usuário',
            'autofocus': True
        })
    )
    
    password = forms.CharField(
        label='Senha',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite sua senha'
        })
    )