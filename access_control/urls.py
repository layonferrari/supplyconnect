"""
URLs do painel administrativo — versão final consolidada.
Compatível com o views.py simplificado e funcional.
"""

from django.urls import path
from . import views

app_name = 'access_control'

urlpatterns = [
    # ==========================================================
    # DASHBOARD PRINCIPAL
    # ==========================================================
    path('', views.admin_panel_home, name='home'),

    # ==========================================================
    # ADMIN GLOBAL
    # ==========================================================
    path('global/', views.global_dashboard, name='global_dashboard'),
    path('admin-login/', views.admin_login, name='admin_login'),
    path('global/create/', views.global_admin_create, name='global_admin_create'),
    path('global/system-config/', views.system_default_config, name='system_default_config'),

    # ==========================================================
    # ADMIN DE PAÍS
    # ==========================================================
    path('country/dashboard/', views.country_admin_dashboard, name='country_dashboard'),  # ✅ CORRIGIDO
    path('country/ad-config/', views.country_ad_config, name='country_ad_config'),
    path('country/smtp-config/', views.country_smtp_config, name='country_smtp_config'),
    path('country/test-ldap/', views.test_ldap_connection, name='test_ldap_connection'),
    path('country/ad-sync/', views.country_ad_sync, name='country_ad_sync'),
    path('country/supplier-permissions/', views.country_supplier_permissions, name='country_supplier_permissions'),
    path('country/groups/', views.country_groups_list, name='country_groups_list'),
    path('country/users/', views.country_users_list, name='country_users_list'),
    path('country/suppliers/sync-groups/', views.country_ad_sync_groups, name='country_ad_sync_groups'),
    path('country/suppliers/group/<int:group_id>/toggle/', views.country_toggle_group_permission, name='country_toggle_group_permission'),
    path('country/suppliers/user/<int:user_id>/toggle/', views.country_toggle_user_permission, name='country_toggle_user_permission'),
    path('country/suppliers/user/<int:user_id>/edit/', views.country_edit_user_permissions, name='country_edit_user_permissions'),
    path('country/ad/sync-users/', views.country_ad_sync_users, name='country_ad_sync_users'),
]