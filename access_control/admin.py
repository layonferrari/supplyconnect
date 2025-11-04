from django.contrib import admin
from django.utils.html import format_html
from .models import (
    AdminProfile,
    CountryPermission,
    ADGroup,
    ADUser,
    SystemDefaultConfig
)


@admin.register(AdminProfile)
class AdminProfileAdmin(admin.ModelAdmin):
    """Admin para perfis de administradores."""
    
    list_display = [
        'user_display',
        'access_level_display',
        'country_display',
        'is_active',
        'created_at'
    ]
    
    list_filter = [
        'access_level',
        'country_code',
        'is_active',
        'created_at'
    ]
    
    search_fields = [
        'user__username',
        'user__email',
        'user__first_name',
        'user__last_name'
    ]
    
    readonly_fields = [
        'created_at',
        'updated_at',
        'created_by'
    ]
    
    fieldsets = (
        ('Usuário', {
            'fields': ('user', 'access_level', 'country_code')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Auditoria', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def user_display(self, obj):
        """Exibe nome completo do usuário."""
        return obj.user.get_full_name() or obj.user.username
    user_display.short_description = 'Usuário'
    
    def access_level_display(self, obj):
        """Exibe nível de acesso com ícone."""
        icons = {
            'global_admin': '🌍',
            'country_admin': '🏢',
            'manager': '👔',
            'user': '👤'
        }
        icon = icons.get(obj.access_level, '❓')
        return format_html(
            '<span>{} {}</span>',
            icon,
            obj.get_access_level_display()
        )
    access_level_display.short_description = 'Nível de Acesso'
    
    def country_display(self, obj):
        """Exibe país ou Global."""
        if obj.country_code:
            return obj.get_country_code_display()
        return format_html('<strong style="color: #0091DA;">Global</strong>')
    country_display.short_description = 'País'
    
    def save_model(self, request, obj, form, change):
        """Salva o modelo e registra quem criou."""
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(CountryPermission)
class CountryPermissionAdmin(admin.ModelAdmin):
    """Admin para permissões de país."""
    
    list_display = [
        'admin_display',
        'can_configure_ad',
        'can_configure_smtp',
        'can_sync_ad_groups',
        'can_assign_permissions',
        'can_manage_suppliers'
    ]
    
    list_filter = [
        'can_configure_ad',
        'can_configure_smtp',
        'can_sync_ad_groups',
        'can_assign_permissions'
    ]
    
    search_fields = [
        'admin_profile__user__username',
        'admin_profile__user__email',
        'admin_profile__user__first_name',
        'admin_profile__user__last_name'
    ]
    
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Administrador', {
            'fields': ('admin_profile',)
        }),
        ('Permissões de Configuração', {
            'fields': (
                'can_configure_ad',
                'ad_config_type',
                'can_configure_smtp',
                'smtp_config_type'
            )
        }),
        ('Permissões de Usuários', {
            'fields': (
                'can_sync_ad_groups',
                'can_assign_permissions',
                'can_manage_local_users'
            )
        }),
        ('Permissões de Módulos', {
            'fields': (
                'can_manage_suppliers',
                'can_manage_contracts',
                'can_manage_quality'
            )
        }),
        ('Auditoria', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def admin_display(self, obj):
        """Exibe nome do admin."""
        return obj.admin_profile.user.get_full_name()
    admin_display.short_description = 'Administrador'


@admin.register(ADGroup)
class ADGroupAdmin(admin.ModelAdmin):
    """Admin para grupos do AD."""
    
    list_display = [
        'name',
        'country_display',
        'member_count',
        'can_create_suppliers',
        'can_edit_suppliers',
        'can_delete_suppliers',
        'is_active',
        'last_sync'
    ]
    
    list_filter = [
        'country_code',
        'is_active',
        'can_create_suppliers',
        'can_edit_suppliers',
        'can_delete_suppliers',
        'last_sync'
    ]
    
    search_fields = [
        'name',
        'distinguished_name',
        'description'
    ]
    
    readonly_fields = [
        'last_sync',
        'created_at'
    ]
    
    fieldsets = (
        ('Informações do Grupo', {
            'fields': (
                'country_code',
                'name',
                'distinguished_name',
                'description',
                'member_count'
            )
        }),
        ('Permissões de Fornecedores', {
            'fields': (
                'can_create_suppliers',
                'can_edit_suppliers',
                'can_delete_suppliers'
            )
        }),
        ('Status e Sincronização', {
            'fields': (
                'is_active',
                'last_sync'
            )
        }),
        ('Auditoria', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def country_display(self, obj):
        """Exibe país com bandeira."""
        return obj.get_country_code_display()
    country_display.short_description = 'País'


@admin.register(ADUser)
class ADUserAdmin(admin.ModelAdmin):
    """Admin para usuários do AD."""
    
    list_display = [
        'display_name',
        'username',
        'country_display',
        'email',
        'department',
        'can_create_suppliers',
        'has_individual_permissions',
        'is_active',
        'last_sync'
    ]
    
    list_filter = [
        'country_code',
        'is_active',
        'has_individual_permissions',
        'can_create_suppliers',
        'can_edit_suppliers',
        'can_delete_suppliers',
        'department',
        'last_sync'
    ]
    
    search_fields = [
        'username',
        'email',
        'display_name',
        'first_name',
        'last_name',
        'department',
        'title'
    ]
    
    readonly_fields = [
        'last_sync',
        'created_at'
    ]
    
    filter_horizontal = ['groups']
    
    fieldsets = (
        ('Informações do Usuário', {
            'fields': (
                'country_code',
                'username',
                'email',
                'first_name',
                'last_name',
                'display_name',
                'distinguished_name'
            )
        }),
        ('Informações Profissionais', {
            'fields': (
                'department',
                'title'
            )
        }),
        ('Grupos', {
            'fields': ('groups',)
        }),
        ('Permissões Individuais', {
            'fields': (
                'has_individual_permissions',
                'can_create_suppliers',
                'can_edit_suppliers',
                'can_delete_suppliers'
            ),
            'description': 'Estas permissões sobrescrevem as permissões do grupo quando "Tem permissões individuais" está marcado.'
        }),
        ('Status e Sincronização', {
            'fields': (
                'is_active',
                'last_sync'
            )
        }),
        ('Auditoria', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def country_display(self, obj):
        """Exibe país com bandeira."""
        return obj.get_country_code_display()
    country_display.short_description = 'País'


@admin.register(SystemDefaultConfig)
class SystemDefaultConfigAdmin(admin.ModelAdmin):
    """Admin para configuração padrão do sistema."""
    
    list_display = [
        '__str__',
        'ad_enabled',
        'smtp_enabled',
        'updated_at'
    ]
    
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Configurações AD Padrão', {
            'fields': (
                'ad_enabled',
                'ad_server',
                'ad_port',
                'ad_use_ssl',
                'ad_use_tls',
                'ad_bind_user_dn',
                'ad_bind_password',
                'ad_base_dn',
                'ad_user_search_base',
                'ad_search_filter'
            )
        }),
        ('Configurações SMTP Padrão', {
            'fields': (
                'smtp_enabled',
                'smtp_host',
                'smtp_port',
                'smtp_use_tls',
                'smtp_username',
                'smtp_password',
                'smtp_from_email'
            )
        }),
        ('Auditoria', {
            'fields': ('created_at', 'updated_at', 'updated_by'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        """Permite apenas 1 configuração padrão."""
        return not SystemDefaultConfig.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        """Não permite deletar a configuração padrão."""
        return False