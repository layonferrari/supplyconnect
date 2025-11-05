"""
adminpanel/views.py
Views para configuração de LDAP, SMTP e SSL.
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext as _
from .models import LdapDirectory, SmtpConfiguration, SslConfig
from .forms import LdapDirectoryForm, SmtpConfigurationForm, SslConfigForm


@login_required
def index(request):
    """Página inicial do painel administrativo."""
    return render(request, 'adminpanel/index.html')


@login_required
def ldap_config(request):
    """Configuração do LDAP/Active Directory."""
    # Tenta pegar uma configuração existente ou cria uma nova
    ldap = LdapDirectory.objects.first()
    
    if request.method == 'POST':
        form = LdapDirectoryForm(request.POST, instance=ldap)
        if form.is_valid():
            config = form.save(commit=False)
            config.created_by = request.user
            config.updated_by = request.user
            
            # Criptografa a senha se foi fornecida
            password = request.POST.get('bind_password')
            if password:
                config.set_password(password)
            
            config.save()
            messages.success(request, _('Configuração LDAP salva com sucesso!'))
            return redirect('adminpanel:ldap_config')
    else:
        form = LdapDirectoryForm(instance=ldap)
    
    return render(request, 'adminpanel/ldap_config.html', {'form': form})


@login_required
def smtp_config(request):
    """Configuração do servidor SMTP."""
    # Tenta pegar uma configuração existente ou cria uma nova
    smtp = SmtpConfiguration.objects.first()
    
    if request.method == 'POST':
        form = SmtpConfigurationForm(request.POST, instance=smtp)
        if form.is_valid():
            config = form.save(commit=False)
            config.created_by = request.user
            
            # Criptografa a senha se foi fornecida
            password = request.POST.get('password')
            if password:
                config.set_password(password)
            
            config.save()
            messages.success(request, _('Configuração SMTP salva com sucesso!'))
            return redirect('adminpanel:smtp_config')
    else:
        form = SmtpConfigurationForm(instance=smtp)
    
    return render(request, 'adminpanel/smtp_config.html', {'form': form})


@login_required
def ssl_config(request):
    """Configuração de certificados SSL."""
    ssl = SslConfig.objects.first()
    
    if request.method == 'POST':
        form = SslConfigForm(request.POST, request.FILES, instance=ssl)
        if form.is_valid():
            form.save()
            messages.success(request, _('Certificados SSL salvos com sucesso!'))
            return redirect('adminpanel:ssl_config')
    else:
        form = SslConfigForm(instance=ssl)
    
    return render(request, 'adminpanel/ssl_config.html', {'form': form})
