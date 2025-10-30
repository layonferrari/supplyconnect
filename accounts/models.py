from django.contrib.auth.models import AbstractUser
from django.db import models
from core.models import CompanyUnit

# Choices de idiomas (se ainda não existir)
LANGUAGES = [
    ('pt-br', 'Português (Brasil)'),
    ('en', 'English'),
    ('es', 'Español'),
    ('de', 'Deutsch'),
    ('it', 'Italiano'),
    ('zh-hans', '中文 (简体)'),
]

# Choices de países
# Países ILPEA
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


class User(AbstractUser):
    """
    Modelo de usuário customizado do SupplyConnect.
    
    Tipos de usuário:
    - Superuser (is_superuser=True): Admin Central - acesso total
    - Country Admin (is_country_admin=True): Admin de um país específico
    - Supplier (is_supplier=True): Fornecedor externo
    - Collaborator: Funcionário ILPEA (padrão)
    """
    is_admin_local = models.BooleanField(
        default=False,
        verbose_name="Admin Local"
    )
    
    # ✅ NOVOS CAMPOS - Adicionar aqui:
    ad_groups = models.TextField(
        blank=True,
        null=True,
        verbose_name="Grupos do AD",
        help_text="Grupos do Active Directory (JSON)"
    )
    
    last_ad_sync = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Última Sincronização AD"
    )

    # Idioma preferido
    preferred_language = models.CharField(
        max_length=10,
        default='pt-br',
        choices=LANGUAGES,
        verbose_name="Idioma Preferido"
    )
    
    # Tipo de usuário
    is_supplier = models.BooleanField(
        default=False,
        verbose_name="É Fornecedor",
        help_text="Usuário externo (fornecedor/parceiro)"
    )
    
    is_country_admin = models.BooleanField(
        default=False,
        verbose_name="Administrador do País",
        help_text="Pode gerenciar configurações do seu país"
    )
    
    # País de origem/responsabilidade
    country_code = models.CharField(
        max_length=5,
        choices=COUNTRY_CHOICES,
        null=True,
        blank=True,
        verbose_name="País",
        help_text="País de origem ou responsabilidade (para Country Admin)"
    )
    
    # Unidade da empresa
    company_unit = models.ForeignKey(
        CompanyUnit,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='users',
        verbose_name="Unidade da Empresa"
    )
    
    # Admin local (legado - manter por compatibilidade)
    is_admin_local = models.BooleanField(
        default=False,
        verbose_name="Admin Local (Legado)"
    )
    
    # Metadados
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Criado em"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Atualizado em"
    )
    
    class Meta:
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"
        ordering = ['-date_joined']
    
    def __str__(self):
        return self.get_full_name() or self.username
    
    def get_user_type_display(self):
        """Retorna o tipo de usuário em formato legível."""
        if self.is_superuser:
            return "🔐 Admin Central"
        elif self.is_country_admin:
            return f"🌍 Admin {self.get_country_code_display()}"
        elif self.is_supplier:
            return "🤝 Fornecedor"
        elif self.is_staff:
            return "👤 Colaborador (Staff)"
        else:
            return "👤 Colaborador"
    
    def can_manage_ldap(self, country_code=None):
        """
        Verifica se o usuário pode gerenciar configurações LDAP.
        
        Args:
            country_code (str, optional): Código do país a verificar
        
        Returns:
            bool: True se pode gerenciar
        """
        # Superuser pode tudo
        if self.is_superuser:
            return True
        
        # Country Admin pode gerenciar apenas seu país
        if self.is_country_admin and country_code:
            return self.country_code == country_code
        
        return False
    
    def can_manage_smtp(self):
        """
        Verifica se o usuário pode gerenciar configurações SMTP.
        Apenas superusers podem gerenciar SMTP.
        
        Returns:
            bool: True se pode gerenciar
        """
        return self.is_superuser
    
    def save(self, *args, **kwargs):
        """
        Override do save para validações.
        """
        # Country Admin deve ter um país definido
        if self.is_country_admin and not self.country_code:
            raise ValueError("Country Admin deve ter um país definido.")
        
        # Fornecedor não pode ser Country Admin
        if self.is_supplier and self.is_country_admin:
            raise ValueError("Fornecedor não pode ser Country Admin.")
        
        super().save(*args, **kwargs)