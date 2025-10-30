"""
Script para corrigir a função collaborator_login
Corrige a lógica de autenticação LDAP que estava quebrada
"""

# Ler o arquivo atual
with open('accounts/views.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Encontrar onde começa a função collaborator_login
start_line = None
for i, line in enumerate(lines):
    if 'def collaborator_login(request):' in line:
        start_line = i
        break

if start_line is None:
    print("❌ Não encontrei a função collaborator_login!")
    exit(1)

# Encontrar onde termina (próxima função ou final do arquivo)
end_line = len(lines)
for i in range(start_line + 1, len(lines)):
    if lines[i].startswith('def ') or lines[i].startswith('@'):
        end_line = i
        break

print(f"✅ Função encontrada: linha {start_line + 1} até {end_line}")

# Nova versão CORRETA da função
new_function = '''def collaborator_login(request):
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


'''

# Construir novo arquivo
new_lines = lines[:start_line] + [new_function] + lines[end_line:]

# Backup do arquivo original
with open('accounts/views.py.backup', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print("✅ Backup criado: accounts/views.py.backup")

# Escrever arquivo corrigido
with open('accounts/views.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("✅ Arquivo corrigido!")
print("\n📋 O que foi mudado:")
print("   1. LDAP agora tenta autenticar SEMPRE (não só quando usuário não existe)")
print("   2. Admins de país autenticam primeiro localmente")
print("   3. Se não for admin, tenta LDAP")
print("   4. Se usuário não existe, tenta LDAP")
print("\n🎯 Agora teste o login do usuário 'layon'!")