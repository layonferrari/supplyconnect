from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    # Página inicial
    path("", views.home_choice, name="home_choice"),
    
    # Login
    path("login/partner/", views.partner_login, name="partner_login"),
    path("login/collaborator/", views.collaborator_login, name="collaborator_login"),
    
    # Dashboards
    path("dashboard/supplier/", views.supplier_dashboard, name="supplier_dashboard"),
    path("dashboard/collaborator/", views.collaborator_dashboard, name="collaborator_dashboard"),
    
    # Configurações e logout
    path("settings/", views.user_settings, name="user_settings"),
    path("logout/", views.user_logout, name="logout"),
]