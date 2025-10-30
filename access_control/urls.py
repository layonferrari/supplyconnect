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
    path('global/create/', views.global_admin_create, name='global_admin_create'),

    # ==========================================================
    # ADMIN DE PAÍS
    # ==========================================================
    path('country/dashboard/', views.country_smtp_config, name='country_dashboard'),  # dashboard país ou config unificada
    path('country/ad-config/', views.country_ad_config, name='country_ad_config'),
    path('country/smtp-config/', views.country_smtp_config, name='country_smtp_config'),
    path('country/test-ldap/', views.test_ldap_connection, name='test_ldap_connection'),
]
