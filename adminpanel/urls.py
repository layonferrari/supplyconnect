from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='adminpanel_index'),
    path('ldap/', views.ldap_config, name='ldap_config'),
    path('smtp/', views.smtp_config, name='smtp_config'),
    path('ssl/', views.ssl_config, name='ssl_config'),
]
