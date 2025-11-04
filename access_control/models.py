from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError


# Choices para países
COUNTRY_CHOICES = [
    ('BR', '🇧🇷 Brasil'),
    ('AR', '🇦🇷 Argentina'),
    ('MX', '🇲🇽 México'),
    ('DE', '🇩🇪 Alemanha'),
    ('IT', '🇮🇹 Itália'),
    ('CN', '🇨🇳 China'),
    ('US', '🇺🇸 Estados Unidos'),
    ('ES', '🇪🇸 Espanha'),
    ('FR', '🇫🇷 França'),
    ('GB', '🇬🇧 Reino Unido'),
    ('JP', '🇯🇵 Japão'),
    ('IN', '🇮🇳 Índia'),
    ('CA', '🇨🇦 Canadá'),
    ('AU', '🇦🇺 Austrália'),
    ('CL', '🇨🇱 Chile'),
    ('CO', '🇨🇴 Colômbia'),
    ('PE', '🇵🇪 Peru'),
    ('UY', '🇺🇾 Uruguai'),
    ('PY', '🇵🇾 Paraguai'),
    ('PT', '🇵🇹 Portugal'),
    ('NL', '🇳🇱 Holanda'),
    ('BE', '🇧🇪 Bélgica'),
    ('CH', '🇨🇭 Suíça'),
    ('AT', '🇦🇹 Áustria'),
    ('PL', '🇵🇱 Polônia'),
    ('CZ', '🇨🇿 República Tcheca'),
    ('RU', '🇷🇺 Rússia'),
    ('ZA', '🇿🇦 África do Sul'),
    ('EG', '🇪🇬 Egito'),
    ('KR', '🇰🇷 Coreia do Sul'),
    ('TH', '🇹🇭 Tailândia'),
    ('VN', '🇻🇳 Vietnã'),
    ('ID', '🇮🇩 Indonésia'),
    ('MY', '🇲🇾 Malásia'),
    ('SG', '🇸🇬 Singapura'),
    ('TR', '🇹🇷 Turquia'),
    ('SA', '🇸🇦 Arábia Saudita'),
    ('AE', '🇦🇪 Emirados Árabes'),
]


# Choices para níveis de acesso
ACCESS_LEVEL_CHOICES = [
    ('global_admin', 'Administrador Global'),
    ('country_admin', 'Administrador de País'),
    ('manager', 'Gerente'),
    ('user', 'Usuário'),
]


class AdminProfile(models.Model):
    """
    Perfil de administrador com país e nível de acesso.
    Complementa o modelo User com informações de administração.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='admin_profile',
        verbose_name='Usuário'
    )
    
    # Nível de acesso
    access_level = models.CharField(
        max_length=20,
        choices=ACCESS_LEVEL_CHOICES,
        default='user',
        verbose_name='Nível de Acesso'
    )
    
    # País de responsabilidade (null = global)
    country_code = models.CharField(
        max_length=5,
        choices=COUNTRY_CHOICES,
        blank=True,
        null=True,
        verbose_name='País'
    )
    
    # Criado por (quem criou este admin)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='admins_created',
        verbose_name='Criado Por'
    )
    
    # Auditoria
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado Em')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Atualizado Em')
    
    # Status
    is_active = models.BooleanField(default=True, verbose_name='Ativo')
    
    class Meta:
        verbose_name = 'Perfil de Administrador'
        verbose_name_plural = 'Perfis de Administradores'
        ordering = ['access_level', 'country_code', 'user__first_name']
    
    def __str__(self):
        country = f" - {self.get_country_code_display()}" if self.country_code else " (Global)"
        return f"{self.user.get_full_name()} - {self.get_access_level_display()}{country}"
    
    def is_global_admin(self):
        """Verifica se é administrador global."""
        return self.access_level == 'global_admin'
    
    def is_country_admin(self):
        """Verifica se é administrador de país."""
        return self.access_level == 'country_admin'
    
    def clean(self):
        """Validações customizadas."""
        # Admin global não pode ter país
        if self.access_level == 'global_admin' and self.country_code:
            raise ValidationError('Administrador Global não pode ter país específico.')
        
        # Admin de país DEVE ter país
        if self.access_level == 'country_admin' and not self.country_code:
            raise ValidationError('Administrador de País deve ter um país definido.')
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class CountryPermission(models.Model):
    """
    Permissões específicas de um Admin de País.
    Define o que cada admin pode fazer em seu país.
    """
    
    # Choices para tipo de configuração
    CONFIG_TYPE_CHOICES = [
        ('own', 'Configuração Própria'),
        ('manual', 'Configuração Manual (definida pelo Global Admin)'),
        ('system_default', 'Usar Padrão do Sistema'),
    ]
    
    admin_profile = models.OneToOneField(
        AdminProfile,
        on_delete=models.CASCADE,
        related_name='country_permissions',
        verbose_name='Perfil de Admin'
    )
    
    # Permissões de configuração AD
    can_configure_ad = models.BooleanField(
        default=False,
        verbose_name='Pode Configurar Active Directory'
    )
    
    ad_config_type = models.CharField(
        max_length=20,
        choices=CONFIG_TYPE_CHOICES,
        default='own',
        verbose_name='Tipo de Configuração AD',
        help_text='Se "Pode Configurar AD" = False, define qual configuração usar'
    )
    
    # Permissões de configuração SMTP
    can_configure_smtp = models.BooleanField(
        default=False,
        verbose_name='Pode Configurar SMTP'
    )
    
    smtp_config_type = models.CharField(
        max_length=20,
        choices=CONFIG_TYPE_CHOICES,
        default='own',
        verbose_name='Tipo de Configuração SMTP',
        help_text='Se "Pode Configurar SMTP" = False, define qual configuração usar'
    )
    
    # Permissões de usuários
    can_sync_ad_groups = models.BooleanField(
        default=True,
        verbose_name='Pode Sincronizar Grupos do AD'
    )
    
    can_assign_permissions = models.BooleanField(
        default=True,
        verbose_name='Pode Atribuir Permissões'
    )
    
    can_manage_local_users = models.BooleanField(
        default=True,
        verbose_name='Pode Gerenciar Usuários Locais'
    )
    
    # Permissões de fornecedores
    can_manage_suppliers = models.BooleanField(
        default=True,
        verbose_name='Pode Gerenciar Fornecedores'
    )
    
    # Permissões de contratos
    can_manage_contracts = models.BooleanField(
        default=True,
        verbose_name='Pode Gerenciar Contratos'
    )
    
    # Permissões de qualidade
    can_manage_quality = models.BooleanField(
        default=True,
        verbose_name='Pode Gerenciar Qualidade'
    )
    
    # Auditoria
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado Em')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Atualizado Em')
    
    class Meta:
        verbose_name = 'Permissão de País'
        verbose_name_plural = 'Permissões de Países'
    
    def __str__(self):
        return f"Permissões de {self.admin_profile.user.get_full_name()}"


class SystemDefaultConfig(models.Model):
    """
    Configurações padrão do sistema (AD e SMTP global).
    Usado quando um país não pode configurar próprio e escolhe 'usar padrão do sistema'.
    Deve ter apenas 1 registro no banco.
    """
    
    # ===== CONFIGURAÇÕES AD PADRÃO =====
    ad_enabled = models.BooleanField(
        default=False,
        verbose_name='AD Padrão Ativo',
        help_text='Habilitar configuração AD padrão do sistema'
    )
    
    ad_server = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Servidor AD',
        help_text='Exemplo: ad.empresa.com'
    )
    
    ad_port = models.IntegerField(
        default=389,
        verbose_name='Porta AD'
    )
    
    ad_use_ssl = models.BooleanField(
        default=False,
        verbose_name='Usar SSL (LDAPS)'
    )
    
    ad_use_tls = models.BooleanField(
        default=False,
        verbose_name='Usar START_TLS'
    )
    
    ad_bind_user_dn = models.CharField(
        max_length=500,
        blank=True,
        verbose_name='User DN para Bind',
        help_text='Exemplo: CN=Admin,CN=Users,DC=empresa,DC=com'
    )
    
    ad_bind_password = models.CharField(
        max_length=500,
        blank=True,
        verbose_name='Senha do Bind (criptografada)'
    )
    
    ad_base_dn = models.CharField(
        max_length=500,
        blank=True,
        verbose_name='Base DN',
        help_text='Exemplo: DC=empresa,DC=com'
    )
    
    ad_user_search_base = models.CharField(
        max_length=500,
        blank=True,
        verbose_name='Base de Busca de Usuários'
    )
    
    ad_search_filter = models.CharField(
        max_length=255,
        blank=True,
        default='(sAMAccountName={username})',
        verbose_name='Filtro de Busca LDAP'
    )
    
    # ===== CONFIGURAÇÕES SMTP PADRÃO =====
    smtp_enabled = models.BooleanField(
        default=False,
        verbose_name='SMTP Padrão Ativo',
        help_text='Habilitar configuração SMTP padrão do sistema'
    )
    
    smtp_host = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Servidor SMTP',
        help_text='Exemplo: smtp.gmail.com'
    )
    
    smtp_port = models.IntegerField(
        default=587,
        verbose_name='Porta SMTP'
    )
    
    smtp_use_tls = models.BooleanField(
        default=True,
        verbose_name='Usar TLS'
    )
    
    smtp_username = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Usuário SMTP'
    )
    
    smtp_password = models.CharField(
        max_length=500,
        blank=True,
        verbose_name='Senha SMTP (criptografada)'
    )
    
    smtp_from_email = models.EmailField(
        blank=True,
        verbose_name='Email Remetente',
        help_text='Email que aparecerá como remetente'
    )
    
    # ===== AUDITORIA =====
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado Em')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Atualizado Em')
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='system_configs_updated',
        verbose_name='Atualizado Por'
    )
    
    class Meta:
        verbose_name = 'Configuração Padrão do Sistema'
        verbose_name_plural = 'Configurações Padrão do Sistema'
    
    def __str__(self):
        return "Configuração Padrão do Sistema"
    
    def save(self, *args, **kwargs):
        """Garante que existe apenas 1 registro."""
        if not self.pk and SystemDefaultConfig.objects.exists():
            raise ValidationError('Já existe uma configuração padrão do sistema.')
        super().save(*args, **kwargs)
    
    @classmethod
    def get_config(cls):
        """Retorna ou cria a configuração padrão."""
        config, created = cls.objects.get_or_create(pk=1)
        return config


class ADGroup(models.Model):
    """Grupos sincronizados do Active Directory"""
    country_code = models.CharField(max_length=2, choices=COUNTRY_CHOICES)
    name = models.CharField(max_length=200, default='')
    distinguished_name = models.CharField(max_length=500, unique=True, default='')
    description = models.TextField(blank=True, null=True)
    member_count = models.IntegerField(default=0)
    
    # Permissões
    can_create_suppliers = models.BooleanField(default=False, verbose_name="Pode criar fornecedores")
    can_edit_suppliers = models.BooleanField(default=False, verbose_name="Pode editar fornecedores")
    can_delete_suppliers = models.BooleanField(default=False, verbose_name="Pode excluir fornecedores")
    
    # Auditoria
    last_sync = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Grupo do AD"
        verbose_name_plural = "Grupos do AD"
        ordering = ['country_code', 'name']
        unique_together = ['country_code', 'name']
    
    def __str__(self):
        return f"{self.country_code} - {self.name}"
        return f"{self.country_code} - {self.name}"


class ADUser(models.Model):
    """Usuários sincronizados do Active Directory"""
    country_code = models.CharField(max_length=2, choices=COUNTRY_CHOICES)
    username = models.CharField(max_length=150, default='')
    email = models.EmailField(blank=True, null=True)
    first_name = models.CharField(max_length=150, blank=True, default='')
    last_name = models.CharField(max_length=150, blank=True, default='')
    distinguished_name = models.CharField(max_length=500, unique=True, default='')
    display_name = models.CharField(max_length=300, blank=True, default='')
    department = models.CharField(max_length=200, blank=True, null=True)
    title = models.CharField(max_length=200, blank=True, null=True)
    
    # Relacionamento com grupos
    groups = models.ManyToManyField(ADGroup, related_name='users', blank=True)
    
    # Permissões individuais (sobrescrevem permissões do grupo)
    can_create_suppliers = models.BooleanField(default=False, verbose_name="Pode criar fornecedores")
    can_edit_suppliers = models.BooleanField(default=False, verbose_name="Pode editar fornecedores")
    can_delete_suppliers = models.BooleanField(default=False, verbose_name="Pode excluir fornecedores")
    has_individual_permissions = models.BooleanField(default=False, verbose_name="Tem permissões individuais")
    
    # Auditoria
    last_sync = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Usuário do AD"
        verbose_name_plural = "Usuários do AD"
        ordering = ['country_code', 'display_name']
        unique_together = ['country_code', 'username']
    
    def __str__(self):
        return f"{self.country_code} - {self.display_name or self.username}"
    
    def get_full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.display_name or self.username