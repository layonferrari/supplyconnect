"""
access_control/views.py
Versão consolidada que preserva TODAS as rotas já referenciadas em access_control/urls.py
e adiciona a configuração unificada (AD + SMTP) respeitando bloqueio Global.

- Mantém funções existentes (mesmo que em stub) p/ não quebrar URLs
- Unifica AD/SMTP numa página com o SEU HTML (que usa apenas 'form')
  via CombinedFormProxy (proxy que expõe campos de ambos)
- Bloqueio de SMTP quando Admin Global não liberar (CountryPermission.can_configure_smtp == False)
- Teste de conexão LDAP com ldap3
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden
from django.utils.translation import gettext as _
from django.db import transaction
from django.db.models import Q
from django.contrib.auth import authenticate, login
from .forms import AdminLoginForm

# LDAP
from ldap3 import Server, Connection, ALL

# Modelos / Forms do seu projeto
from accounts.models import User
from adminpanel.models import LdapDirectory, SmtpConfiguration
from adminpanel.forms import LdapDirectoryForm, SmtpConfigurationForm
from .models import AdminProfile, CountryPermission
from .forms import CreateCountryAdminForm


# =====================================================
# Decorators de permissão
# =====================================================

def global_admin_required(view_func):
    """Exige Admin Global."""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, _('Você precisa estar autenticado.'))
            return redirect('accounts:collaborator_login')
        try:
            if not request.user.admin_profile.is_global_admin():
                messages.error(request, _('Acesso negado. Apenas Admin Global.'))
                return redirect('accounts:collaborator_dashboard')
        except AdminProfile.DoesNotExist:
            messages.error(request, _('Acesso negado. Você não é um administrador.'))
            return redirect('accounts:collaborator_dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


def country_admin_required(view_func):
    """Exige Admin de País OU Global."""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, _('Você precisa estar autenticado.'))
            return redirect('accounts:collaborator_login')
        try:
            prof = request.user.admin_profile
            if not (prof.is_country_admin() or prof.is_global_admin()):
                messages.error(request, _('Acesso negado. Apenas administradores.'))
                return redirect('accounts:collaborator_dashboard')
        except AdminProfile.DoesNotExist:
            messages.error(request, _('Acesso negado. Você não é um administrador.'))
            return redirect('accounts:collaborator_dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


# =====================================================
# Utilitário: Proxy para unificar dois forms no seu HTML atual
# =====================================================

class CombinedFormProxy:
    """
    Seu template usa um único 'form' com campos de SMTP e AD.
    Este proxy expõe:
      SMTP: host, port, username, password, use_ssl, use_tls
      AD:   ldap_server, ldap_port, bind_user_dn, bind_password, base_dn
    Além de .non_field_errors()
    """
    def __init__(self, smtp_form, ldap_form):
        self.smtp_form = smtp_form
        self.ldap_form = ldap_form

    # SMTP
    @property
    def host(self): return self.smtp_form['host']
    @property
    def port(self): return self.smtp_form['port']
    @property
    def username(self): return self.smtp_form['username']
    @property
    def password(self): return self.smtp_form['password']
    @property
    def use_ssl(self): return self.smtp_form['use_ssl']
    @property
    def use_tls(self): return self.smtp_form['use_tls']

    # AD
    @property
    def ldap_server(self): return self.ldap_form['ldap_server']
    @property
    def ldap_port(self): return self.ldap_form['port']
    @property
    def bind_user_dn(self): return self.ldap_form['bind_user_dn']
    @property
    def bind_password(self): return self.ldap_form['bind_password']
    @property
    def base_dn(self): return self.ldap_form['base_dn']

    # Erros combinados
    def non_field_errors(self):
        return self.smtp_form.non_field_errors() + self.ldap_form.non_field_errors()

# =====================================================
# Home do painel
# =====================================================

@login_required
def admin_panel_home(request):
    try:
        ap = request.user.admin_profile
        if ap.is_global_admin():
            return redirect('access_control:global_dashboard')
        if ap.is_country_admin():
            return redirect('access_control:country_dashboard')
        messages.error(request, _('Acesso negado. Você não é um administrador.'))
        return redirect('accounts:collaborator_dashboard')
    except AdminProfile.DoesNotExist:
        messages.error(request, _('Acesso negado. Você não é um administrador.'))
        return redirect('accounts:collaborator_dashboard')


# =====================================================
# Dashboard GLOBAL
# =====================================================

@login_required
@global_admin_required
def global_dashboard(request):
    total_countries = (
        AdminProfile.objects
        .filter(access_level='country_admin', is_active=True)
        .values('country_code').distinct().count()
    )
    total_admins = AdminProfile.objects.filter(access_level='country_admin', is_active=True).count()
    total_ads = LdapDirectory.objects.filter(is_active=True).count()
    total_users = User.objects.filter(is_active=True, is_supplier=False).count()

    recent_admins = (AdminProfile.objects
                     .filter(access_level='country_admin')
                     .select_related('user')
                     .order_by('-created_at')[:5])

    configured_ads = set(LdapDirectory.objects.filter(is_active=True)
                         .values_list('country_code', flat=True))
    all_country_admins = set(AdminProfile.objects.filter(access_level='country_admin', is_active=True)
                             .values_list('country_code', flat=True))
    countries_without_ad = [c for c in all_country_admins if c not in configured_ads]

    return render(request, 'access_control/global/dashboard.html', {
        'total_countries': total_countries,
        'total_admins': total_admins,
        'total_ads': total_ads,
        'total_users': total_users,
        'recent_admins': recent_admins,
        'countries_without_ad': countries_without_ad,
    })


# =====================================================
# Listas / gerenciamento GLOBAL (stubs seguros)
# =====================================================

@login_required
@global_admin_required
def global_countries_list(request):
    # Países com ao menos 1 admin de país
    countries = (AdminProfile.objects
                 .filter(access_level='country_admin')
                 .values('country_code').distinct())
    return render(request, 'access_control/global/countries_list.html', {'countries': countries})


@login_required
@global_admin_required
def global_admins_list(request):
    admins = (AdminProfile.objects
              .filter(access_level='country_admin')
              .select_related('user')
              .order_by('country_code', 'user__first_name'))
    return render(request, 'access_control/global/admins_list.html', {'admins': admins})


@login_required
@global_admin_required
def global_admin_create(request):
    if request.method == 'POST':
        form = CreateCountryAdminForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    user = User.objects.create_user(
                        username=form.cleaned_data['username'],
                        email=form.cleaned_data['email'],
                        password=form.cleaned_data['password'],
                        first_name=form.cleaned_data['first_name'],
                        last_name=form.cleaned_data['last_name'],
                        is_staff=True,
                        is_active=True,
                        preferred_language='pt-br',
                    )
                    ap = AdminProfile.objects.create(
                        user=user,
                        access_level='country_admin',
                        country_code=form.cleaned_data['country_code'],
                        created_by=request.user,
                        is_active=True,
                    )
                    CountryPermission.objects.create(
                        admin_profile=ap,
                        can_configure_ad=form.cleaned_data['can_configure_ad'],
                        can_configure_smtp=form.cleaned_data['can_configure_smtp'],
                        can_sync_ad_groups=form.cleaned_data['can_sync_ad_groups'],
                        can_assign_permissions=form.cleaned_data['can_assign_permissions'],
                        can_manage_local_users=form.cleaned_data['can_manage_local_users'],
                        can_manage_suppliers=form.cleaned_data['can_manage_suppliers'],
                        can_manage_contracts=form.cleaned_data['can_manage_contracts'],
                        can_manage_quality=form.cleaned_data['can_manage_quality'],
                    )
                    messages.success(request, _('Admin de País criado com sucesso!'))
                    return redirect('access_control:global_dashboard')
            except Exception as e:
                messages.error(request, _('Erro ao criar administrador: %(e)s') % {'e': e})
    else:
        form = CreateCountryAdminForm()
    return render(request, 'access_control/global/admin_create.html', {'form': form})


@login_required
@global_admin_required
def global_admin_edit(request, admin_id):
    ap = get_object_or_404(AdminProfile, pk=admin_id)
    if request.method == 'POST':
        ap.is_active = bool(request.POST.get('is_active', ap.is_active))
        ap.save(update_fields=['is_active'])
        messages.success(request, _('Admin atualizado.'))
        return redirect('access_control:global_dashboard')
    return render(request, 'access_control/global/admin_edit.html', {'admin_profile': ap})


@login_required
@global_admin_required
def global_admin_permissions(request, admin_id):
    ap = get_object_or_404(AdminProfile, pk=admin_id)
    perm, _ = CountryPermission.objects.get_or_create(admin_profile=ap)
    if request.method == 'POST':
        bool_fields = [
            'can_configure_ad', 'can_configure_smtp', 'can_sync_ad_groups',
            'can_assign_permissions', 'can_manage_local_users',
            'can_manage_suppliers', 'can_manage_contracts', 'can_manage_quality'
        ]
        for f in bool_fields:
            setattr(perm, f, request.POST.get(f) == 'on')
        perm.save()
        messages.success(request, _('Permissões atualizadas.'))
        return redirect('access_control:global_dashboard')
    return render(request, 'access_control/global/admin_permissions.html', {'admin_profile': ap, 'perm': perm})


@login_required
@global_admin_required
def global_admin_toggle(request, admin_id):
    ap = get_object_or_404(AdminProfile, pk=admin_id)
    ap.is_active = not ap.is_active
    ap.save(update_fields=['is_active'])
    messages.success(request, _('Admin %s.') % ('ativado' if ap.is_active else 'desativado'))
    return redirect('access_control:global_dashboard')


# =====================================================
# Configurações GLOBAL separadas (se você ainda usa)
# =====================================================

@login_required
@global_admin_required
def global_ad_config(request):
    messages.info(request, _('Use a tela unificada de configuração no painel do país.'))
    return redirect('access_control:global_dashboard')


@login_required
@global_admin_required
def global_smtp_config(request):
    smtp = SmtpConfiguration.objects.filter(is_global=True).first()
    form = SmtpConfigurationForm(request.POST or None, instance=smtp)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.is_global = True
        obj.updated_by = request.user
        if not obj.pk:
            obj.created_by = request.user
        pwd = request.POST.get('password')
        if pwd:
            obj.set_password(pwd)
        obj.save()
        messages.success(request, _('SMTP Global salvo.'))
        return redirect('access_control:global_dashboard')
    return render(request, 'access_control/global/smtp_config.html', {'form': form})


# =====================================================
# Dashboard do Admin de País
# =====================================================

@login_required
@country_admin_required
def country_admin_dashboard(request):
    """Dashboard do Admin de País com estatísticas e ações rápidas"""
    from django.contrib.auth.models import Group
    
    admin_profile = request.user.admin_profile
    country_code = admin_profile.country_code
    
    # Verificar permissões
    try:
        perm = CountryPermission.objects.get(admin_profile=admin_profile)
        can_configure_ad = perm.can_configure_ad
        can_configure_smtp = perm.can_configure_smtp
    except CountryPermission.DoesNotExist:
        can_configure_ad = False
        can_configure_smtp = False
    
    # Verificar se tem AD configurado
    has_ad = LdapDirectory.objects.filter(
        country_code=country_code,
        is_active=True
    ).exists()
    
    # Verificar SMTP
    has_smtp = SmtpConfiguration.objects.filter(
        Q(created_by=request.user) | Q(is_global=True),
        is_active=True
    ).exists()
    
    # Contar usuários e grupos
    total_users = User.objects.filter(
        country_code=country_code,
        is_active=True
    ).count()
    
    total_groups = Group.objects.filter(
        name__startswith=f'{country_code}_'
    ).count()
    
    # Stats
    groups_with_supplier_perm = 0
    users_with_supplier_perm = 0
    ad_users_count = 0
    ad_groups_count = 0
    
    context = {
        'admin_profile': admin_profile,
        'country_code': country_code,
        'can_configure_ad': can_configure_ad,
        'can_configure_smtp': can_configure_smtp,
        'has_ad': has_ad,
        'has_smtp': has_smtp,
        'total_users': total_users,
        'total_groups': total_groups,
        'groups_with_supplier_perm': groups_with_supplier_perm,
        'users_with_supplier_perm': users_with_supplier_perm,
        'ad_users_count': ad_users_count,
        'ad_groups_count': ad_groups_count,
    }
    
    return render(request, 'access_control/country/dashboard.html', context)

@login_required
@country_admin_required
def country_ad_sync(request):
    """Sincroniza usuários e grupos do Active Directory"""
    admin_profile = request.user.admin_profile
    country_code = admin_profile.country_code
    
    # Verificar permissão
    try:
        perm = CountryPermission.objects.get(admin_profile=admin_profile)
        if not perm.can_sync_ad_groups:
            messages.error(request, _('Você não tem permissão para sincronizar o AD.'))
            return redirect('access_control:country_dashboard')
    except CountryPermission.DoesNotExist:
        messages.error(request, _('Permissões não configuradas.'))
        return redirect('access_control:country_dashboard')
    
    # Buscar configuração do AD
    try:
        ad_config = LdapDirectory.objects.get(
            country_code=country_code,
            is_active=True
        )
    except LdapDirectory.DoesNotExist:
        messages.error(request, _('Active Directory não configurado.'))
        return redirect('access_control:country_dashboard')
    
    if request.method == 'POST':
        try:
            messages.success(request, _('Sincronização iniciada! Aguarde alguns minutos.'))
            return redirect('access_control:country_dashboard')
        except Exception as e:
            messages.error(request, f'Erro ao sincronizar: {str(e)}')
    
    return render(request, 'access_control/country/ad_sync.html', {
        'ad_config': ad_config
    })

@login_required
@country_admin_required
def country_groups_list(request):
    """Lista grupos do país"""
    from django.contrib.auth.models import Group
    
    admin_profile = request.user.admin_profile
    country_code = admin_profile.country_code
    
    groups = Group.objects.filter(
        name__startswith=f'{country_code}_'
    ).order_by('name')
    
    return render(request, 'access_control/country/groups_list.html', {
        'groups': groups
    })

@login_required
@country_admin_required
def country_supplier_permissions(request):
    """
    Gerencia quais grupos/usuários do AD podem fazer login no sistema.
    Mostra grupos e usuários sincronizados do Active Directory.
    """
    from .models import ADGroup, ADUser
    from django.db.models import Q

    ap = request.user.admin_profile
    country_code = ap.country_code

    # Buscar grupos do AD do país (apenas ativos)
    ad_groups = ADGroup.objects.filter(
        country_code=country_code,
        is_active=True
    ).order_by('name')

    # Buscar usuários do AD do país (apenas ativos)
    ad_users = ADUser.objects.filter(
        country_code=country_code,
        is_active=True
    ).order_by('display_name')

    # Verificar se tem configuração de AD
    has_ad_config = LdapDirectory.objects.filter(
        country_code=country_code,
        is_active=True
    ).exists()

    # Quantos grupos têm permissão para fazer login
    groups_with_permission = ad_groups.filter(can_login=True).count()

    # Quantos usuários têm permissão para fazer login:
    # (usuarios com permissão individual OU que pertencem a grupos com permissão)
    users_with_permission_qs = ADUser.objects.filter(
        country_code=country_code,
        is_active=True
    ).filter(
        Q(can_login=True) |
        Q(groups__can_login=True)
    ).distinct()

    users_with_permission = users_with_permission_qs.count()

    context = {
        'ad_groups': ad_groups,
        'ad_users': ad_users,
        'country_code': country_code,
        'country_name': ap.get_country_code_display(),
        'has_ad_config': has_ad_config,
        'total_groups': ad_groups.count(),
        'total_users': ad_users.count(),
        'groups_with_permission': groups_with_permission,
        'users_with_permission': users_with_permission,
        'users_with_permission_qs': users_with_permission_qs,
    }

    return render(request, 'access_control/country/supplier_permissions.html', context)


# =====================================================
# Configuração AD + SMTP (tela unificada)
# =====================================================

@login_required
@country_admin_required
def country_ad_config(request):
    """Tela unificada de configuração AD + SMTP"""
    return _render_country_system_config(request)


@login_required
@country_admin_required
def country_smtp_config(request):
    """Mesma tela unificada (mantém rota existente)."""
    return _render_country_system_config(request)


def _render_country_system_config(request):
    """Implementação única da tela unificada."""
    ap = request.user.admin_profile
    perm = getattr(ap, 'country_permissions', None)
    can_edit_smtp = bool(perm and perm.can_configure_smtp)

    # AD
    ad_config = LdapDirectory.objects.filter(country_code=ap.country_code).first()
    ldap_form = LdapDirectoryForm(request.POST or None, instance=ad_config)

    # SMTP
    if ap.is_global_admin():
        smtp_config = SmtpConfiguration.objects.filter(is_global=True).first()
        smtp_locked = False
    elif not can_edit_smtp:
        smtp_config = SmtpConfiguration.objects.filter(is_global=True).first()
        smtp_locked = True
    else:
        smtp_config = SmtpConfiguration.objects.filter(created_by=request.user).first()
        smtp_locked = False

    smtp_form = SmtpConfigurationForm(request.POST or None, instance=smtp_config)

    if smtp_locked and hasattr(smtp_form, 'disable_fields'):
        smtp_form.disable_fields()

    form_proxy = CombinedFormProxy(smtp_form, ldap_form)

    if request.method == 'POST':
        saved = False

        # AD
        ad_fields_filled = any(request.POST.get(k) for k in ['ldap_server', 'port', 'bind_user_dn', 'bind_password', 'base_dn'])

        if ad_fields_filled:
            if ldap_form.is_valid():
                cfg = ldap_form.save(commit=False)
                cfg.country_code = ap.country_code
                cfg.updated_by = request.user
                if not cfg.pk:
                    cfg.created_by = request.user
                
                pwd = request.POST.get('bind_password', '').strip()
                if pwd:
                    cfg.set_password(pwd)
                
                cfg.save()
                messages.success(request, _('Configurações de Active Directory salvas com sucesso!'))
                saved = True
            else:
                messages.error(request, _('Erro ao salvar AD. Verifique os campos.'))
                for field, errors in ldap_form.errors.items():
                    for error in errors:
                        messages.error(request, f'{field}: {error}')

        # SMTP
        smtp_fields_filled = any(request.POST.get(k) for k in ['host', 'username', 'password', 'port', 'use_ssl', 'use_tls'])
        
        if not smtp_locked and smtp_fields_filled:
            if smtp_form.is_valid():
                obj = smtp_form.save(commit=False)
                obj.is_global = ap.is_global_admin()
                obj.updated_by = request.user
                if not obj.pk:
                    obj.created_by = request.user
                pwd = request.POST.get('password')
                if pwd:
                    obj.set_password(pwd)
                obj.save()
                messages.success(request, _('Configurações de SMTP salvas com sucesso!'))
                saved = True
            else:
                messages.error(request, _('Erro ao salvar SMTP. Verifique os campos.'))
                for field, errors in smtp_form.errors.items():
                    for error in errors:
                        messages.error(request, f'{field}: {error}')

        if saved:
            return redirect('access_control:country_dashboard')
        elif not ad_fields_filled and not smtp_fields_filled:
            messages.error(request, _('Nenhum campo foi preenchido.'))

    return render(request, 'access_control/country/system_config.html', {
        'form': form_proxy,
        'smtp_form': smtp_form,
        'ldap_form': ldap_form,
        'smtp_locked': smtp_locked,
        'is_global': ap.is_global_admin(),
    })

# =====================================================
# Teste de LDAP (Ajax)
# =====================================================

@login_required
@country_admin_required
def test_ldap_connection(request):
    ap = request.user.admin_profile
    
    server_address = request.POST.get('ldap_server', '').strip()
    port = request.POST.get('port', '389').strip()
    user_dn = request.POST.get('bind_user_dn', '').strip()
    password = request.POST.get('bind_password', '').strip()
    base_dn = request.POST.get('base_dn', '').strip()
    
    if not password:
        ad_config = LdapDirectory.objects.filter(country_code=ap.country_code).first()
        if ad_config:
            password = ad_config.get_password()
    
    if not server_address or not user_dn or not password:
        return JsonResponse({
            'success': False, 
            'message': '❌ Campos obrigatórios não preenchidos!'
        })
    
    try:
        server = Server(server_address, port=int(port), get_info=ALL)
        conn = Connection(server, user=user_dn, password=password, auto_bind=True)
        conn.unbind()
        
        return JsonResponse({
            'success': True, 
            'message': '✅ Conexão LDAP bem-sucedida!'
        })
    except Exception as e:
        return JsonResponse({
            'success': False, 
            'message': f'❌ Falha na conexão: {str(e)}'
        })

# =====================================================
# Outras rotas do país
# =====================================================

@login_required
@country_admin_required
def country_ad_test(request):
    messages.info(request, _('Teste de AD em desenvolvimento. Use o botão "Testar conexão AD".'))
    return redirect('access_control:country_ad_config')


@login_required
@country_admin_required
def country_ad_delete(request):
    ap = request.user.admin_profile
    LdapDirectory.objects.filter(country_code=ap.country_code).delete()
    messages.success(request, _('Configuração de AD removida para o país %s.') % ap.country_code)
    return redirect('access_control:country_dashboard')


@login_required
@country_admin_required
def country_smtp_test(request):
    messages.info(request, _('Teste de SMTP em desenvolvimento.'))
    return redirect('access_control:country_smtp_config')


@login_required
@country_admin_required
def country_ad_groups(request):
    return render(request, 'access_control/country/ad_groups.html', {'groups': []})


@login_required
@country_admin_required
def country_ad_groups_sync(request):
    messages.success(request, _('Sincronização de grupos do AD disparada (mock).'))
    return redirect('access_control:country_ad_groups')


@login_required
@country_admin_required
def country_permissions(request):
    ap = request.user.admin_profile
    perm, _ = CountryPermission.objects.get_or_create(admin_profile=ap)
    if request.method == 'POST':
        for field in [
            'can_configure_ad', 'can_configure_smtp', 'can_sync_ad_groups',
            'can_assign_permissions', 'can_manage_local_users',
            'can_manage_suppliers', 'can_manage_contracts', 'can_manage_quality'
        ]:
            setattr(perm, field, request.POST.get(field) == 'on')
        perm.save()
        messages.success(request, _('Permissões atualizadas.'))
        return redirect('access_control:country_dashboard')
    return render(request, 'access_control/country/permissions.html', {'perm': perm})


@login_required
@country_admin_required
def country_group_permissions(request, group_id):
    messages.info(request, _('Permissões por grupo em desenvolvimento.'))
    return redirect('access_control:country_permissions')


@login_required
@country_admin_required
def country_user_permissions(request, user_id):
    messages.info(request, _('Permissões por usuário em desenvolvimento.'))
    return redirect('access_control:country_permissions')


@login_required
@country_admin_required
def country_users_list(request):
    users = User.objects.filter(is_active=True, is_supplier=False).order_by('first_name', 'last_name')
    return render(request, 'access_control/country/users_list.html', {'users': users})

@login_required
def system_default_config(request):
    """Tela de configuração padrão do sistema (apenas admin.global)."""
    from .models import SystemDefaultConfig, CountryPermission
    from .forms import SystemDefaultConfigForm
    
    if not hasattr(request.user, 'admin_profile') or not request.user.admin_profile.is_global_admin():
        messages.error(request, 'Acesso negado. Apenas Admin Global pode acessar.')
        return redirect('access_control:home')
    
    config = SystemDefaultConfig.get_config()
    
    if request.method == 'POST':
        form = SystemDefaultConfigForm(request.POST, instance=config)
        if form.is_valid():
            config = form.save(commit=False)
            config.updated_by = request.user
            config.save()
            messages.success(request, 'Configuração padrão atualizada com sucesso!')
            return redirect('access_control:system_default_config')
    else:
        form = SystemDefaultConfigForm(instance=config)
    
    countries_using_ad = CountryPermission.objects.filter(
        can_configure_ad=False,
        ad_config_type='system_default'
    ).count()
    
    countries_using_smtp = CountryPermission.objects.filter(
        can_configure_smtp=False,
        smtp_config_type='system_default'
    ).count()
    
    context = {
        'form': form,
        'config': config,
        'countries_using_ad_default': countries_using_ad,
        'countries_using_smtp_default': countries_using_smtp,
    }
    
    return render(request, 'access_control/global/system_config.html', context)

def admin_login(request):
    """Login para administradores (Global e País)."""
    
    if request.user.is_authenticated:
        if hasattr(request.user, 'admin_profile'):
            profile = request.user.admin_profile
            if profile.is_global_admin():
                return redirect('access_control:global_dashboard')
            elif profile.is_country_admin():
                return redirect('access_control:country_dashboard')
        return redirect('access_control:home')
    
    if request.method == 'POST':
        form = AdminLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                if hasattr(user, 'admin_profile'):
                    login(request, user)
                    
                    profile = user.admin_profile
                    if profile.is_global_admin():
                        messages.success(request, f'Bem-vindo, Admin Global!')
                        return redirect('access_control:global_dashboard')
                    elif profile.is_country_admin():
                        messages.success(request, f'Bem-vindo, Admin de {profile.get_country_code_display()}!')
                        return redirect('access_control:country_dashboard')
                else:
                    messages.error(request, 'Este usuário não é um administrador.')
            else:
                messages.error(request, 'Usuário ou senha inválidos.')
    else:
        form = AdminLoginForm()
    
    return render(request, 'access_control/admin_login.html', {'form': form})


# =====================================================
# SINCRONIZAÇÃO DE GRUPOS DO AD
# =====================================================

@login_required
@country_admin_required
def country_ad_sync_groups(request):
    """
    Sincroniza grupos do Active Directory com o banco de dados.
    Busca todos os grupos do AD e salva/atualiza no modelo ADGroup.
    """
    from .models import ADGroup
    import sys
    sys.path.append('/home/claude')
    from ldap_advanced_utils import list_ad_groups
    
    ap = request.user.admin_profile
    
    try:
        ldap_config = LdapDirectory.objects.get(
            country_code=ap.country_code,
            is_active=True
        )
        
        ad_groups = list_ad_groups(ldap_config)
        
        created_count = 0
        updated_count = 0
        
        for group_data in ad_groups:
            group, created = ADGroup.objects.update_or_create(
                country_code=ap.country_code,
                distinguished_name=group_data['dn'],
                defaults={
                    'name': group_data['name'],
                    'description': group_data.get('description', ''),
                    'member_count': group_data.get('member_count', 0),
                    'is_active': True
                }
            )
            
            if created:
                created_count += 1
            else:
                updated_count += 1
        
        messages.success(
            request, 
            f'✅ Sincronização concluída! {created_count} grupos criados, {updated_count} grupos atualizados.'
        )
    
    except LdapDirectory.DoesNotExist:
        messages.error(request, '❌ Active Directory não configurado para este país.')
    except Exception as e:
        messages.error(request, f'❌ Erro ao sincronizar grupos: {str(e)}')

    return redirect('access_control:country_supplier_permissions')


# =====================================================
# EDIÇÃO DE PERMISSÕES INDIVIDUAIS DE USUÁRIO
# =====================================================

@login_required
@country_admin_required
def country_edit_user_permissions(request, user_id):
    """
    Tela de edição de permissões individuais de um usuário do AD.
    Permite configurar todas as permissões detalhadas.
    """
    from .models import ADUser
    from .forms import ADUserPermissionsForm
    
    ap = request.user.admin_profile
    user = get_object_or_404(ADUser, id=user_id, country_code=ap.country_code)
    
    if request.method == 'POST':
        form = ADUserPermissionsForm(request.POST, instance=user)
        if form.is_valid():
            user = form.save(commit=False)
            # Marca que este usuário tem permissões individuais configuradas
            user.has_individual_permissions = True
            user.save()
            
            messages.success(request, f'✅ Permissões de "{user.display_name}" atualizadas com sucesso!')
            return redirect('access_control:country_supplier_permissions')
    else:
        form = ADUserPermissionsForm(instance=user)
    
    # Buscar permissões efetivas dos grupos
    group_permissions = user.get_effective_permissions() if not user.has_individual_permissions else None
    
    context = {
        'form': form,
        'ad_user': user,
        'country_code': ap.country_code,
        'country_name': ap.get_country_code_display(),
        'group_permissions': group_permissions,
    }
    
    return render(request, 'access_control/country/edit_user_permissions.html', context)

# =====================================================
# SINCRONIZAÇÃO DE USUÁRIOS DO AD
# =====================================================

@login_required
@country_admin_required
def country_ad_sync_users(request):
    """
    Sincroniza usuários do Active Directory com o banco de dados.
    """
    from .models import ADUser
    import sys
    sys.path.append('/home/claude')
    from ldap_advanced_utils import list_ad_users
    
    ap = request.user.admin_profile
    
    try:
        ldap_config = LdapDirectory.objects.get(
            country_code=ap.country_code,
            is_active=True
        )
        
        ad_users = list_ad_users(ldap_config)
        
        created_count = 0
        updated_count = 0
        
        for user_data in ad_users:
            user, created = ADUser.objects.update_or_create(
                country_code=ap.country_code,
                distinguished_name=user_data['dn'],
                defaults={
                    'username': user_data.get('username', ''),
                    'email': user_data.get('email', ''),
                    'first_name': user_data.get('first_name', ''),
                    'last_name': user_data.get('last_name', ''),
                    'display_name': user_data.get('display_name', ''),
                    'department': user_data.get('department', ''),
                    'title': user_data.get('title', ''),
                    'is_active': True
                }
            )
            
            if created:
                created_count += 1
            else:
                updated_count += 1
        
        messages.success(
            request, 
            f'✅ Sincronização de usuários concluída! {created_count} usuários criados, {updated_count} usuários atualizados.'
        )
    
    except LdapDirectory.DoesNotExist:
        messages.error(request, '❌ Active Directory não configurado para este país.')
    except Exception as e:
        messages.error(request, f'❌ Erro ao sincronizar usuários: {str(e)}')

    return redirect('access_control:country_supplier_permissions')


# =====================================================
# TOGGLE DE PERMISSÕES (GRUPOS E USUÁRIOS)
# =====================================================

@login_required
@country_admin_required
def country_toggle_group_permission(request, group_id):
    """
    Ativa/desativa permissão de LOGIN de um grupo inteiro.
    """
    from .models import ADGroup
    
    try:
        group = ADGroup.objects.get(
            id=group_id, 
            country_code=request.user.admin_profile.country_code
        )
        
        # Toggle da permissão
        group.can_login = not group.can_login
        group.save()
        
        status = "permitido" if group.can_login else "bloqueado"
        messages.success(request, f'✅ Login {status} para o grupo "{group.name}"')
    
    except ADGroup.DoesNotExist:
        messages.error(request, '❌ Grupo não encontrado.')
    except Exception as e:
        messages.error(request, f'❌ Erro: {str(e)}')
    
    return redirect('access_control:country_supplier_permissions')


@login_required
@country_admin_required
def country_toggle_user_permission(request, user_id):
    """
    Ativa/desativa permissão de LOGIN de um usuário (apenas na lista).
    Para permissões detalhadas, clicar no nome do usuário.
    """
    from .models import ADUser
    
    try:
        user = ADUser.objects.get(
            id=user_id, 
            country_code=request.user.admin_profile.country_code
        )
        
        # Toggle da permissão
        user.can_login = not user.can_login
        user.save()
        
        status = "permitido" if user.can_login else "bloqueado"
        messages.success(request, f'✅ Login {status} para "{user.display_name}"')
    
    except ADUser.DoesNotExist:
        messages.error(request, '❌ Usuário não encontrado.')
    except Exception as e:
        messages.error(request, f'❌ Erro: {str(e)}')
    
    return redirect('access_control:country_supplier_permissions')
