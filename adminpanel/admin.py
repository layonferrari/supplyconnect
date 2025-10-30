from django.contrib import admin
from django.utils.html import format_html
from .models import (
    LdapDirectory,
    SmtpConfiguration,
    LdapConfig,
    SmtpConfig,
    SslConfig
)
from .encryption import decrypt_text


@admin.register(LdapDirectory)
class LdapDirectoryAdmin(admin.ModelAdmin):
    """Admin para configurações de LDAP."""
    
    list_display = [
        'name',
        'country_display',
        'ldap_server',
        'port',
        'is_global',
        'is_active'
    ]
    
    list_filter = [
        'country_code',
        'is_active',
        'is_global',
        'use_ssl',
        'use_tls'
    ]
    
    search_fields = [
        'name',
        'ldap_server',
        'base_dn'
    ]
    
    readonly_fields = ['created_by', 'created_at', 'updated_at', 'updated_by']
    
    fieldsets = (
        ('Identificação', {
            'fields': ('country_code', 'name', 'is_global')
        }),
        ('Servidor LDAP', {
            'fields': (
                'ldap_server',
                'port',
                'base_dn',
                'use_ssl',
                'use_tls'
            )
        }),
        ('Credenciais', {
            'fields': (
                'bind_user_dn',
                'bind_password_encrypted'
            ),
            'classes': ('collapse',)
        }),
        ('Busca de Usuários', {
            'fields': (
                'user_search_base',
                'search_filter'
            )
        }),
        ('Mapeamento de Atributos', {
            'fields': (
                'attr_first_name',
                'attr_last_name',
                'attr_email'
            ),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Auditoria', {
            'fields': ('created_by', 'created_at', 'updated_by', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def country_display(self, obj):
        """Exibe país com bandeira."""
        return obj.get_country_code_display()
    country_display.short_description = 'País'
    
    def save_model(self, request, obj, form, change):
        """Salva o modelo e registra quem criou/atualizou."""
        if not change:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(SmtpConfiguration)
class SmtpConfigurationAdmin(admin.ModelAdmin):
    """Admin para configurações de SMTP."""
    
    list_display = [
        'name',
        'host',
        'port',
        'is_global',
        'is_active'
    ]
    
    list_filter = [
        'is_active',
        'is_global',
        'use_tls',
        'use_ssl'
    ]
    
    search_fields = [
        'name',
        'host',
        'username'
    ]
    
    readonly_fields = ['created_by', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Identificação', {
            'fields': ('name', 'is_global')
        }),
        ('Servidor SMTP', {
            'fields': (
                'host',
                'port',
                'use_tls',
                'use_ssl'
            )
        }),
        ('Credenciais', {
            'fields': (
                'username',
                'password_encrypted'
            ),
            'classes': ('collapse',)
        }),
        ('Remetente Padrão', {
            'fields': (
                'from_email',
                'from_name'
            )
        }),
        ('Limites', {
            'fields': (
                'max_emails',
                'timeout'
            )
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Auditoria', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """Salva o modelo e registra quem criou."""
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


# Registros simples para modelos legados
@admin.register(LdapConfig)
class LdapConfigAdmin(admin.ModelAdmin):
    """Admin para LDAP Config (modelo legado)."""
    list_display = ['host', 'base_dn', 'created_at']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Servidor', {
            'fields': ('host', 'base_dn')
        }),
        ('Credenciais', {
            'fields': ('bind_user', 'bind_password_encrypted'),
            'classes': ('collapse',)
        }),
        ('Busca', {
            'fields': ('group_search',)
        }),
        ('Auditoria', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(SmtpConfig)
class SmtpConfigAdmin(admin.ModelAdmin):
    """Admin para SMTP Config (modelo legado)."""
    list_display = ['host', 'port', 'username', 'use_ssl', 'use_tls', 'created_at']
    list_filter = ['use_ssl', 'use_tls']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Servidor', {
            'fields': ('host', 'port')
        }),
        ('Credenciais', {
            'fields': ('username', 'password_encrypted'),
            'classes': ('collapse',)
        }),
        ('Segurança', {
            'fields': ('use_ssl', 'use_tls')
        }),
        ('Auditoria', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(SslConfig)
class SslConfigAdmin(admin.ModelAdmin):
    """Admin para SSL Config."""
    list_display = ['cert_file', 'key_file', 'uploaded_at']
    readonly_fields = ['uploaded_at']
    
    fieldsets = (
        ('Certificados', {
            'fields': ('cert_file', 'key_file')
        }),
        ('Auditoria', {
            'fields': ('uploaded_at',),
            'classes': ('collapse',)
        }),
    )