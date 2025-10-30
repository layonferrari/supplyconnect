from django.shortcuts import render, redirect
# Comentado para testes sem autenticação
# from django.contrib.auth.decorators import login_required, user_passes_test
from .models import LdapConfig, SmtpConfig, SslConfig
from .forms import LdapDirectoryForm, SmtpConfigurationForm, SslConfigForm


# Comentado para desativar verificação de admin_local temporariamente
# def admin_only(user):
#     return getattr(user, 'is_admin_local', False)


# ===============================
# ⚙️ PÁGINA PRINCIPAL DO PAINEL
# ===============================

# @login_required
# @user_passes_test(admin_only)
def index(request):
    return render(request, 'adminpanel/index.html')


# ===============================
# 🔐 CONFIGURAÇÃO LDAP
# ===============================

# @login_required
# @user_passes_test(admin_only)
def ldap_config(request):
    config = LdapConfig.objects.first()
    form = LdapConfigForm(request.POST or None, instance=config)

    if request.method == 'POST' and form.is_valid():
        instance = form.save(commit=False)
        if request.POST.get('bind_password'):
            instance.set_password(request.POST['bind_password'])
        instance.save()
        return redirect('adminpanel_index')

    return render(request, 'adminpanel/ldap_config.html', {'form': form})


# ===============================
# ✉️ CONFIGURAÇÃO SMTP
# ===============================

# @login_required
# @user_passes_test(admin_only)
def smtp_config(request):
    config = SmtpConfig.objects.first()
    form = SmtpConfigForm(request.POST or None, instance=config)

    if request.method == 'POST' and form.is_valid():
        instance = form.save(commit=False)
        if request.POST.get('password'):
            instance.set_password(request.POST['password'])
        instance.save()
        return redirect('adminpanel_index')

    return render(request, 'adminpanel/smtp_config.html', {'form': form})


# ===============================
# 🔒 CONFIGURAÇÃO SSL
# ===============================

# @login_required
# @user_passes_test(admin_only)
def ssl_config(request):
    config = SslConfig.objects.first()
    form = SslConfigForm(request.POST or None, request.FILES or None, instance=config)

    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('adminpanel_index')

    return render(request, 'adminpanel/ssl_config.html', {'form': form})
