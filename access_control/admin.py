from django.contrib import admin
from django.utils.html import format_html
from .models import (
    AdminProfile,
    CountryPermission,
    AdGroup,
    GroupPermission,
    UserPermission
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
        if not change:  # Se está criando
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
                'can_configure_smtp'
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


@admin.register(AdGroup)
class AdGroupAdmin(admin.ModelAdmin):
    """Admin para grupos do AD."""
    
    list_display = [
        'ad_group_name',
        'country_display',
        'member_count',
        'is_active',
        'last_sync'
    ]
    
    list_filter = [
        'country_code',
        'is_active',
        'last_sync'
    ]
    
    search_fields = [
        'ad_group_name',
        'ad_group_dn',
        'description'
    ]
    
    readonly_fields = [
        'last_sync',
        'member_count',
        'created_at',
        'created_by'
    ]
    
    fieldsets = (
        ('Informações do Grupo', {
            'fields': (
                'country_code',
                'ad_group_name',
                'ad_group_dn',
                'description'
            )
        }),
        ('Sincronização', {
            'fields': (
                'last_sync',
                'member_count'
            )
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Auditoria', {
            'fields': ('created_at', 'created_by'),
            'classes': ('collapse',)
        }),
    )
    
    def country_display(self, obj):
        """Exibe país com bandeira."""
        return obj.get_country_code_display()
    country_display.short_description = 'País'
    
    def save_model(self, request, obj, form, change):
        """Salva o modelo e registra quem criou."""
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(GroupPermission)
class GroupPermissionAdmin(admin.ModelAdmin):
    """Admin para permissões de grupos."""
    
    list_display = [
        'group_display',
        'permission_display',
        'granted_at',
        'granted_by'
    ]
    
    list_filter = [
        'ad_group__country_code',
        'permission_code',
        'granted_at'
    ]
    
    search_fields = [
        'ad_group__ad_group_name',
        'permission_code'
    ]
    
    readonly_fields = ['granted_at', 'granted_by']
    
    fieldsets = (
        ('Grupo e Permissão', {
            'fields': ('ad_group', 'permission_code')
        }),
        ('Auditoria', {
            'fields': ('granted_at', 'granted_by'),
            'classes': ('collapse',)
        }),
    )
    
    def group_display(self, obj):
        """Exibe nome do grupo."""
        return f"{obj.ad_group.get_country_code_display()} - {obj.ad_group.ad_group_name}"
    group_display.short_description = 'Grupo'
    
    def permission_display(self, obj):
        """Exibe permissão formatada."""
        return obj.get_permission_code_display()
    permission_display.short_description = 'Permissão'
    
    def save_model(self, request, obj, form, change):
        """Salva o modelo e registra quem concedeu."""
        if not change:
            obj.granted_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(UserPermission)
class UserPermissionAdmin(admin.ModelAdmin):
    """Admin para permissões de usuários."""
    
    list_display = [
        'user_display',
        'permission_display',
        'status_display',
        'granted_at',
        'granted_by'
    ]
    
    list_filter = [
        'is_granted',
        'permission_code',
        'granted_at'
    ]
    
    search_fields = [
        'user__username',
        'user__email',
        'user__first_name',
        'user__last_name',
        'permission_code'
    ]
    
    readonly_fields = ['granted_at', 'granted_by']
    
    fieldsets = (
        ('Usuário e Permissão', {
            'fields': ('user', 'permission_code', 'is_granted')
        }),
        ('Auditoria', {
            'fields': ('granted_at', 'granted_by'),
            'classes': ('collapse',)
        }),
    )
    
    def user_display(self, obj):
        """Exibe nome do usuário."""
        return obj.user.get_full_name() or obj.user.username
    user_display.short_description = 'Usuário'
    
    def permission_display(self, obj):
        """Exibe permissão formatada."""
        return obj.get_permission_code_display()
    permission_display.short_description = 'Permissão'
    
    def status_display(self, obj):
        """Exibe status da permissão."""
        if obj.is_granted:
            return format_html('<span style="color: green;">✅ Concedida</span>')
        return format_html('<span style="color: red;">❌ Revogada</span>')
    status_display.short_description = 'Status'
    
    def save_model(self, request, obj, form, change):
        """Salva o modelo e registra quem modificou."""
        if not change:
            obj.granted_by = request.user
        super().save_model(request, obj, form, change)