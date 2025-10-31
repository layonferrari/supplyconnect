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
    def ldap_port(self): return self.ldap_form['port']  # ← ADICIONADO
    @property
    def bind_user_dn(self): return self.ldap_form['bind_user_dn']
    @property
    def bind_password(self): return self.ldap_form['bind_password']
    @property
    def base_dn(self): return self.ldap_form['base_dn']  # ← ADICIONADO

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
    # Você pode trocar por um ModelForm próprio. Mantendo simples p/ não quebrar.
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
        # Chaves esperadas; se não vierem, mantém valor atual
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
    # Redireciona para a tela unificada do país do Global? Aqui mantém simples:
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
        # set_password apenas se enviou algo
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
    ap = request.user.admin_profile
    # Números simples só para visual
    has_ad = LdapDirectory.objects.filter(country_code=ap.country_code).exists()
    # Se não liberado, usa global
    smtp_perm = getattr(ap, 'country_permissions', None)
    if ap.is_global_admin():
        smtp = SmtpConfiguration.objects.filter(is_global=True).first()
        smtp_locked = False
    elif smtp_perm and smtp_perm.can_configure_smtp:
        smtp = SmtpConfiguration.objects.filter(created_by=request.user).first()
        smtp_locked = False
    else:
        smtp = SmtpConfiguration.objects.filter(is_global=True).first()
        smtp_locked = True

    return render(request, 'access_control/country/dashboard.html', {
        'has_ad': has_ad,
        'smtp_in_use': smtp,
        'smtp_locked': smtp_locked
    })


# =====================================================
# Configuração AD + SMTP (tela unificada) — COMPATÍVEL COM O SEU HTML
# =====================================================

@login_required
@country_admin_required
def country_ad_config(request):
    """
    Mantemos esta view (nome igual ao seu urls.py) para abrir a MESMA tela unificada.
    Isso evita quebrar rotas existentes e reaproveita seu template atual.
    """
    return _render_country_system_config(request)


@login_required
@country_admin_required
def country_smtp_config(request):
    """Mesma tela unificada (mantém rota existente)."""
    return _render_country_system_config(request)


def _render_country_system_config(request):
    """
    Implementação única da tela unificada.
    - Respeita bloqueio Global p/ SMTP
    - Usa CombinedFormProxy p/ seu template que espera 'form'
    """
    ap = request.user.admin_profile
    perm = getattr(ap, 'country_permissions', None)
    can_edit_smtp = bool(perm and perm.can_configure_smtp)

    # --- AD ---
    ad_config = LdapDirectory.objects.filter(country_code=ap.country_code).first()
    ldap_form = LdapDirectoryForm(request.POST or None, instance=ad_config)

    # --- SMTP (bloqueio/global) ---
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

    # Se bloqueado, desabilita campos no form (método do seu form)
    if smtp_locked and hasattr(smtp_form, 'disable_fields'):
        smtp_form.disable_fields()

    # Proxy p/ seu template atual usar 'form'
    form_proxy = CombinedFormProxy(smtp_form, ldap_form)

    # --- POST handling ---
    if request.method == 'POST':
        saved = False

        # AD: se campos de AD vieram preenchidos, valida e salva
        ad_fields_filled = any(request.POST.get(k) for k in ['ldap_server', 'port', 'bind_user_dn', 'bind_password', 'base_dn'])

        if ad_fields_filled:
            if ldap_form.is_valid():
                cfg = ldap_form.save(commit=False)
                cfg.country_code = ap.country_code
                cfg.updated_by = request.user
                if not cfg.pk:
                    cfg.created_by = request.user
                
                # CORREÇÃO: Pegar senha do POST e verificar se não está vazia
                pwd = request.POST.get('bind_password', '').strip()
                if pwd:
                    cfg.set_password(pwd)
                    print(f"✅ Senha definida para AD (primeiros 5 chars): {pwd[:5]}...")
                else:
                    print("⚠️ Senha não foi fornecida no POST")
                
                cfg.save()
                print(f"✅ Configuração AD salva! ID={cfg.pk}, Servidor={cfg.ldap_server}")
                messages.success(request, _('Configurações de Active Directory salvas com sucesso!'))
                saved = True
            else:
                # Mostrar erros do form
                messages.error(request, _('Erro ao salvar AD. Verifique os campos.'))
                print(f"❌ Erros do formulário AD: {ldap_form.errors}")
                for field, errors in ldap_form.errors.items():
                    for error in errors:
                        messages.error(request, f'{field}: {error}')

        # SMTP: só salva se não estiver bloqueado
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
                # Mostrar erros do form
                messages.error(request, _('Erro ao salvar SMTP. Verifique os campos.'))
                for field, errors in smtp_form.errors.items():
                    for error in errors:
                        messages.error(request, f'{field}: {error}')

        if saved:
            return redirect('access_control:country_dashboard')
        elif not ad_fields_filled and not smtp_fields_filled:
            # Se nenhum dos dois foi preenchido
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
    
    # Pegar dados do POST
    server_address = request.POST.get('ldap_server', '').strip()
    port = request.POST.get('port', '389').strip()
    user_dn = request.POST.get('bind_user_dn', '').strip()
    password = request.POST.get('bind_password', '').strip()
    base_dn = request.POST.get('base_dn', '').strip()
    
    # Se senha não foi fornecida, pegar do banco
    if not password:
        ad_config = LdapDirectory.objects.filter(country_code=ap.country_code).first()
        if ad_config:
            password = ad_config.get_password()
            print(f"🔑 Usando senha do banco (primeiros 5 chars): {password[:5] if password else 'VAZIA'}...")
    
    # Validar campos obrigatórios
    if not server_address or not user_dn or not password:
        return JsonResponse({
            'success': False, 
            'message': '❌ Campos obrigatórios não preenchidos!'
        })
    
    try:
        print(f"🔄 Testando conexão LDAP...")
        print(f"   Servidor: {server_address}:{port}")
        print(f"   Usuário: {user_dn}")
        print(f"   Base DN: {base_dn}")
        
        server = Server(server_address, port=int(port), get_info=ALL)
        conn = Connection(server, user=user_dn, password=password, auto_bind=True)
        conn.unbind()
        
        print(f"✅ Conexão LDAP bem-sucedida!")
        return JsonResponse({
            'success': True, 
            'message': '✅ Conexão LDAP bem-sucedida!'
        })
    except Exception as e:
        print(f"❌ Erro na conexão LDAP: {e}")
        return JsonResponse({
            'success': False, 
            'message': f'❌ Falha na conexão: {str(e)}'
        })

# =====================================================
# Outras rotas do país (stubs — não quebram e você evolui depois)
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
    # Lista grupos do AD (a implementar com seu conector AD)
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
    # Em breve: permissões por grupo
    messages.info(request, _('Permissões por grupo em desenvolvimento.'))
    return redirect('access_control:country_permissions')


@login_required
@country_admin_required
def country_user_permissions(request, user_id):
    # Em breve: permissões por usuário
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
    
    # Verifica se é admin global
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
    
    # Conta países usando configs
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
        # Se já está logado, redireciona pro dashboard correto
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
            
            # Autenticar
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                # Verificar se é admin
                if hasattr(user, 'admin_profile'):
                    login(request, user)
                    
                    # Redirecionar baseado no tipo de admin
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