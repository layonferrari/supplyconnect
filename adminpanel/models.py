"""
Modelos do painel administrativo.
Gerencia configurações de LDAP, SMTP, SSL e outras configurações do sistema.
"""

from django.db import models
from django.conf import settings
from adminpanel.encryption import AESCipher

# Instância global do cipher
aes = AESCipher()

# Choices de países
COUNTRY_CHOICES = [
    ('BR', '🇧🇷 Brasil'),
    ('AR', '🇦🇷 Argentina'),
    ('MX', '🇲🇽 México'),
    ('DE', '🇩🇪 Alemanha'),
    ('IT', '🇮🇹 Itália'),
    ('CN', '🇨🇳 China'),
    ('US', '🇺🇸 Estados Unidos'),
]


# ============================================
# MODELOS LEGADOS (mantidos por compatibilidade)
# ============================================

class LdapConfig(models.Model):
    """
    MODELO LEGADO - Mantido por compatibilidade.
    Use LdapDirectory para novas implementações.
    """
    host = models.CharField(max_length=255)
    base_dn = models.CharField(max_length=255)
    bind_user = models.CharField(max_length=255)
    bind_password_encrypted = models.TextField()
    group_search = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def set_password(self, password):
        self.bind_password_encrypted = aes.encrypt(password)

    def get_password(self):
        return aes.decrypt(self.bind_password_encrypted or '')

    def __str__(self):
        return f"LDAP Config ({self.host})"
    
    class Meta:
        verbose_name = "LDAP Config (Legado)"
        verbose_name_plural = "LDAP Configs (Legado)"


class SmtpConfig(models.Model):
    """
    MODELO LEGADO - Mantido por compatibilidade.
    Use SmtpConfiguration para novas implementações.
    """
    host = models.CharField(max_length=255)
    port = models.IntegerField(default=465)
    username = models.CharField(max_length=255)
    password_encrypted = models.TextField()
    use_ssl = models.BooleanField(default=True)
    use_tls = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def set_password(self, password):
        self.password_encrypted = aes.encrypt(password)

    def get_password(self):
        return aes.decrypt(self.password_encrypted or '')

    def __str__(self):
        return f"SMTP Config ({self.host})"
    
    class Meta:
        verbose_name = "SMTP Config (Legado)"
        verbose_name_plural = "SMTP Configs (Legado)"


class SslConfig(models.Model):
    """Configuração de certificados SSL."""
    cert_file = models.FileField(upload_to='ssl_certs/')
    key_file = models.FileField(upload_to='ssl_keys/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"SSL Cert ({self.cert_file.name})"
    
    class Meta:
        verbose_name = "Configuração SSL"
        verbose_name_plural = "Configurações SSL"


# ============================================
# NOVOS MODELOS (Sistema Multi-País)
# ============================================

class LdapDirectory(models.Model):
    """
    Configuração de Active Directory por país.
    Permite que cada país configure seu próprio AD através do portal administrativo.
    """
    
    country_code = models.CharField(
        max_length=5,
        unique=True,
        choices=COUNTRY_CHOICES,
        verbose_name="País"
    )
    name = models.CharField(
        max_length=100,
        verbose_name="Nome da Configuração",
        help_text="Ex: Active Directory - Brasil"
    )
    
    # Configurações do servidor LDAP
    ldap_server = models.CharField(
        max_length=200,
        verbose_name="Servidor LDAP",
        help_text="Ex: ldap://S28BRDC2-16.BR.ILPEAORG.COM ou S28BRDC2-16.BR.ILPEAORG.COM"
    )
    port = models.IntegerField(
        default=389,
        verbose_name="Porta",
        help_text="389 para LDAP padrão, 636 para LDAPS (SSL)"
    )
    base_dn = models.CharField(
        max_length=300,
        verbose_name="Base DN",
        help_text="Ex: DC=BR,DC=ILPEAORG,DC=COM"
    )
    
    # Credenciais de bind (criptografadas)
    bind_user_dn = models.CharField(
        max_length=300,
        verbose_name="User DN para Bind",
        help_text="Ex: CN=Admin,CN=Users,DC=BR,DC=ILPEAORG,DC=COM"
    )
    bind_password_encrypted = models.TextField(
        verbose_name="Senha de Bind (Criptografada)"
    )
    
    # Configurações de busca
    user_search_base = models.CharField(
        max_length=300,
        verbose_name="Base de Busca de Usuários",
        help_text="Deixe vazio para usar Base DN",
        blank=True
    )
    search_filter = models.CharField(
        max_length=200,
        default="(sAMAccountName={username})",
        verbose_name="Filtro de Busca LDAP",
        help_text="Use {username} como placeholder"
    )
    
    # Mapeamento de atributos AD
    attr_first_name = models.CharField(
        max_length=50,
        default="givenName",
        verbose_name="Atributo: Primeiro Nome"
    )
    attr_last_name = models.CharField(
        max_length=50,
        default="sn",
        verbose_name="Atributo: Sobrenome"
    )
    attr_email = models.CharField(
        max_length=50,
        default="mail",
        verbose_name="Atributo: E-mail"
    )
    
    # Configurações de segurança
    use_ssl = models.BooleanField(
        default=False,
        verbose_name="Usar SSL (LDAPS)",
        help_text="Conexão segura na porta 636"
    )
    use_tls = models.BooleanField(
        default=False,
        verbose_name="Usar START_TLS",
        help_text="Iniciar TLS após conexão (porta 389)"
    )
    
    # Configuração hierárquica
    is_global = models.BooleanField(
        default=False,
        verbose_name="Configuração Global",
        help_text="Se True, esta configuração é gerenciada pelo Admin Global"
    )
    
    # Status e validação
    is_active = models.BooleanField(
        default=True,
        verbose_name="Ativo",
        help_text="Desative para impedir autenticações neste país"
    )
    last_test_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Último Teste de Conexão"
    )
    last_test_status = models.BooleanField(
        default=False,
        verbose_name="Status do Último Teste"
    )
    last_test_message = models.TextField(
        blank=True,
        verbose_name="Mensagem do Último Teste"
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
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ldap_directories_created',
        verbose_name="Criado por"
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ldap_directories_updated',
        verbose_name="Última atualização por"
    )
    
    class Meta:
        verbose_name = "Active Directory"
        verbose_name_plural = "Active Directories"
        ordering = ['country_code']
        db_table = 'adminpanel_ldap_directory'
    
    def set_password(self, raw_password):
        """
        Criptografa a senha antes de salvar no banco.
        Usa o sistema AESCipher existente.
        """
        self.bind_password_encrypted = aes.encrypt(raw_password)
    
    def get_password(self):
        """
        Retorna a senha descriptografada.
        Usa o sistema AESCipher existente.
        """
        try:
            decrypted = aes.decrypt(self.bind_password_encrypted or '')
            return decrypted if decrypted else ''
        except Exception as e:
            print(f"❌ Erro ao descriptografar senha do AD: {str(e)}")
            return ''
    
    def save(self, *args, **kwargs):
        """
        Override do save para garantir que a senha seja criptografada.
        Verifica se a senha está em base64 (criptografada) ou texto plano.
        """
        if self.bind_password_encrypted:
            # Senha criptografada com base64 geralmente tem == no final ou é longa
            # Texto plano da senha do AD é curto (< 30 caracteres normalmente)
            is_likely_encrypted = (
                '==' in self.bind_password_encrypted or 
                len(self.bind_password_encrypted) > 20
            )
            
            if not is_likely_encrypted:
                # Parece texto plano - criptografa
                print(f"🔒 Criptografando senha do AD antes de salvar...")
                self.bind_password_encrypted = aes.encrypt(self.bind_password_encrypted)
                print(f"✅ Senha criptografada: {self.bind_password_encrypted[:30]}...")
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.get_country_code_display()} - {self.name}"
    
    def get_connection_string(self):
        """Retorna a string de conexão completa para o LDAP."""
        server = self.ldap_server.replace('ldap://', '').replace('ldaps://', '')
        protocol = 'ldaps' if self.use_ssl else 'ldap'
        return f"{protocol}://{server}:{self.port}"
    
    def get_user_search_base(self):
        """Retorna a base de busca de usuários."""
        return self.user_search_base or self.base_dn


class SmtpConfiguration(models.Model):
    """
    Configuração SMTP avançada para envio de e-mails.
    Apenas uma configuração pode estar ativa por vez.
    """
    
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Nome da Configuração",
        help_text="Ex: SMTP HCL Notes - Brasil"
    )
    
    # Configurações do servidor
    host = models.CharField(
        max_length=200,
        verbose_name="Servidor SMTP",
        help_text="Ex: ilpea.smtp001-ce.cloud-y.com"
    )
    port = models.IntegerField(
        default=587,
        verbose_name="Porta",
        help_text="25 (padrão), 465 (SSL), 587 (TLS)"
    )
    
    # Credenciais (criptografadas)
    username = models.CharField(
        max_length=200,
        verbose_name="Usuário SMTP",
        help_text="Ex: signbr@ilpea.com"
    )
    password_encrypted = models.TextField(
        verbose_name="Senha SMTP (Criptografada)"
    )
    
    # Configurações de segurança
    use_tls = models.BooleanField(
        default=True,
        verbose_name="Usar TLS",
        help_text="START_TLS na porta 587"
    )
    use_ssl = models.BooleanField(
        default=False,
        verbose_name="Usar SSL",
        help_text="SSL/TLS direto na porta 465"
    )
    
    # E-mail padrão
    from_email = models.EmailField(
        verbose_name="Remetente Padrão",
        help_text="E-mail que aparecerá como remetente"
    )
    from_name = models.CharField(
        max_length=100,
        default="ILPEA SupplyConnect",
        verbose_name="Nome do Remetente"
    )
    
    # Limites e timeout
    max_emails = models.IntegerField(
        default=5,
        verbose_name="Máximo de E-mails por Conexão"
    )
    timeout = models.IntegerField(
        default=10,
        verbose_name="Timeout (segundos)"
    )
    
    # Configuração hierárquica
    is_global = models.BooleanField(
        default=False,
        verbose_name="Configuração Global",
        help_text="Se True, esta configuração é gerenciada pelo Admin Global"
    )
    
    # Status
    is_active = models.BooleanField(
        default=True,
        verbose_name="Ativo",
        help_text="Apenas uma configuração pode estar ativa"
    )
    last_test_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Último Teste de Envio"
    )
    last_test_status = models.BooleanField(
        default=False,
        verbose_name="Status do Último Teste"
    )
    
    # Metadados
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='smtp_configurations_created',
        verbose_name="Criado por"
    )
    
    class Meta:
        verbose_name = "Configuração SMTP"
        verbose_name_plural = "Configurações SMTP"
        ordering = ['-is_active', 'name']
        db_table = 'adminpanel_smtp_configuration'
    
    def set_password(self, raw_password):
        """Criptografa a senha usando AESCipher."""
        self.password_encrypted = aes.encrypt(raw_password)
    
    def get_password(self):
        """Retorna a senha descriptografada."""
        try:
            decrypted = aes.decrypt(self.password_encrypted or '')
            return decrypted if decrypted else ''
        except Exception as e:
            print(f"❌ Erro ao descriptografar senha SMTP: {str(e)}")
            return ''
    
    def save(self, *args, **kwargs):
        """Override do save para criptografar senha e garantir único ativo."""
        # Criptografa senha se necessário
        if self.password_encrypted:
            is_likely_encrypted = (
                '==' in self.password_encrypted or 
                len(self.password_encrypted) > 20
            )
            
            if not is_likely_encrypted:
                print(f"🔒 Criptografando senha SMTP antes de salvar...")
                self.password_encrypted = aes.encrypt(self.password_encrypted)
                print(f"✅ Senha SMTP criptografada!")
        
        # Se este está sendo marcado como ativo, desativa os outros
        if self.is_active:
            SmtpConfiguration.objects.exclude(pk=self.pk).update(is_active=False)
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        status = "🟢" if self.is_active else "⚪"
        return f"{status} {self.name}"