from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import translation
from django.utils.translation import gettext_lazy as _
from .forms import PartnerLoginForm, CollaboratorLoginForm, UserLanguagePreferenceForm
from .models import User

def partner_login(request):
    """Login de parceiros externos (usuários com is_supplier=True)."""
    # Para páginas de login não autenticadas, respeita o idioma da sessão
    if not request.user.is_authenticated and 'django_language' not in request.session:
        translation.activate('pt-br')
        request.session['django_language'] = 'pt-br'
    
    if request.method == "POST":
        form = PartnerLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]

            # autentica usando o e-mail como username
            user = authenticate(request, username=email, password=password)

            if user is not None and getattr(user, "is_supplier", False):
                login(request, user)
                messages.success(request, f"Bem-vindo, {user.first_name or user.username}!")
                return redirect("accounts:supplier_dashboard")
            else:
                messages.error(request, "E-mail ou senha inválidos, ou usuário não é parceiro.")
    else:
        form = PartnerLoginForm()

    return render(request, "accounts/partner_login.html", {"form": form})


def home_choice(request):
    """Tela inicial com a escolha de perfil."""
    # Se não houver usuário autenticado e não houver idioma na sessão, força pt-br
    if not request.user.is_authenticated:
        if 'django_language' not in request.session:
            translation.activate('pt-br')
            request.session['django_language'] = 'pt-br'
    
    return render(request, "home_choice.html")


@login_required
def supplier_dashboard(request):
    """
    Dashboard exclusivo para fornecedores.
    Verifica se o usuário logado tem a flag is_supplier=True.
    """
    # Verifica se o usuário é fornecedor
    if not getattr(request.user, "is_supplier", False):
        return render(request, "accounts/forbidden.html", status=403)
    
    # Renderiza o dashboard com informações do usuário
    context = {
        'username': request.user.username,
        'email': request.user.email,
        'first_name': request.user.first_name or 'Fornecedor',
    }
    return render(request, "accounts/supplier_dashboard.html", context)


def collaborator_login(request):
    from access_control.models import AdminProfile, COUNTRY_CHOICES
    import logging
    logger = logging.getLogger('accounts')
    
    available_countries = AdminProfile.objects.filter(
        access_level='country_admin',
        is_active=True
    ).values_list('country_code', flat=True).distinct().order_by('country_code')
    
    countries_dict = dict(COUNTRY_CHOICES)
    available_countries_choices = [
        (code, countries_dict.get(code, code)) 
        for code in available_countries
    ]
    
    if request.method == 'POST':
        logger.info("=== TENTATIVA DE LOGIN ===")
        logger.info(f"POST data: {request.POST}")
        
        form = CollaboratorLoginForm(request.POST, available_countries=available_countries_choices)
        logger.info(f"Form válido: {form.is_valid()}")
        
        if form.is_valid():
            country_code = form.cleaned_data['country_code']
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            
            logger.info(f"País: {country_code}")
            logger.info(f"Username: {username}")
            logger.info(f"Senha fornecida: {'***' if password else 'VAZIA'}")
            
            # Verificar se usuário existe no banco e tem perfil admin
            try:
                user = User.objects.get(username=username)
                logger.info(f"✅ Usuário encontrado no banco: {user.username}")
                
                # Se tem perfil admin, tentar login local
                if hasattr(user, 'admin_profile'):
                    admin_profile = user.admin_profile
                    logger.info(f"✅ Tem perfil admin")
                    logger.info(f"   Nível: {admin_profile.access_level}")
                    logger.info(f"   País perfil: {admin_profile.country_code}")
                    logger.info(f"   País selecionado: {country_code}")
                    
                    if admin_profile.is_country_admin() and admin_profile.country_code == country_code:
                        logger.info("✅ É admin de país do país correto")
                        
                        senha_ok = user.check_password(password)
                        logger.info(f"   Senha correta: {senha_ok}")
                        
                        if senha_ok:
                            logger.info("✅ FAZENDO LOGIN COMO ADMIN!")
                            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                            messages.success(request, _('Bem-vindo, %(name)s!') % {'name': user.get_full_name()})
                            return redirect('access_control:country_dashboard')
                        else:
                            logger.error("❌ Senha incorreta para admin!")
                            messages.error(request, _('Senha incorreta.'))
                            # Não tentar LDAP se senha de admin está errada
                            return render(request, 'accounts/collaborator_login.html', {
                                'form': form,
                                'available_countries': available_countries_choices
                            })
                    else:
                        logger.info(f"❌ País não confere ou não é admin de país")
                else:
                    logger.info("ℹ️ Usuário existe mas não tem perfil admin - vai tentar LDAP")
                    
            except User.DoesNotExist:
                logger.info(f"ℹ️ Usuário '{username}' não existe no banco - vai tentar LDAP")
            
            # Tentar autenticação LDAP (para colaboradores ou usuários que não existem)
            from adminpanel.models import LdapDirectory
            
            if not LdapDirectory.objects.filter(country_code=country_code, is_active=True).exists():
                logger.error("❌ AD não configurado para este país")
                messages.error(
                    request,
                    _('Active Directory ainda não foi configurado para este país. Contate o administrador.')
                )
            else:
                logger.info("🔄 Tentando autenticação via LDAP...")
                user = authenticate(
                    request,
                    username=username,
                    password=password,
                    country_code=country_code
                )
                
                if user is not None:
                    logger.info(f"✅ Autenticação LDAP bem-sucedida para: {username}")
                    login(request, user)
                    messages.success(request, _('Bem-vindo, %(name)s!') % {'name': user.get_full_name()})
                    return redirect('accounts:collaborator_dashboard')
                else:
                    logger.error(f"❌ Falha na autenticação LDAP para: {username}")
                    messages.error(request, _('Usuário ou senha inválidos.'))
        else:
            logger.error(f"❌ Form inválido: {form.errors}")
            messages.error(request, _('Por favor, preencha todos os campos corretamente.'))
    else:
        form = CollaboratorLoginForm()
    
    context = {
        'form': form,
        'available_countries': available_countries_choices
    }
    
    return render(request, 'accounts/collaborator_login.html', context)


@login_required
def user_settings(request):
    """Página de configurações do usuário (idioma, etc)."""
    if request.method == 'POST':
        form = UserLanguagePreferenceForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Idioma atualizado com sucesso!")
            # Ativa o novo idioma imediatamente
            translation.activate(request.user.preferred_language)
            # Redirecionar para o dashboard correto baseado no tipo de usuário
            if request.user.is_supplier:
                return redirect('accounts:supplier_dashboard')
            else:
                return redirect('accounts:collaborator_dashboard')
    else:
        form = UserLanguagePreferenceForm(instance=request.user)
    
    return render(request, 'accounts/user_settings.html', {'form': form})


def user_logout(request):
    """Faz logout do usuário e reseta completamente o idioma para o padrão."""
    # Faz logout
    logout(request)
    
    # Limpa TODA a sessão (não apenas o idioma)
    request.session.flush()
    
    # Cria uma nova sessão limpa
    request.session.create()
    
    # Define o idioma padrão explicitamente
    translation.activate('pt-br')
    request.session['django_language'] = 'pt-br'
    
    # Adiciona mensagem de sucesso
    messages.success(request, "Você saiu com sucesso!")
    
    # Cria resposta de redirecionamento
    response = redirect('accounts:home_choice')
    
    # Remove cookie de idioma se existir
    response.delete_cookie('django_language')
    
    # Define novo cookie com idioma padrão
    response.set_cookie('django_language', 'pt-br')
    
    # Headers para evitar cache
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate, private'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    
    return response


@login_required
def collaborator_dashboard(request):
    """
    Dashboard principal para colaboradores ILPEA.
    """
    # Verificar se é colaborador (não fornecedor)
    if request.user.is_supplier:
        messages.error(request, _("Acesso negado. Esta área é para colaboradores."))
        return redirect('accounts:supplier_dashboard')
    
    return render(request, 'accounts/collaborator_dashboard.html', {
        'title': _('Dashboard - Colaborador')
    })