"""
Script para adicionar as 3 funções que faltam no views.py
"""
from pathlib import Path

views_file = Path(r'D:\Projeto\SupplyConnect\access_control\views.py')

# Ler o conteúdo atual
content = views_file.read_text(encoding='utf-8')

# Verificar se as funções já existem
if 'def country_toggle_group_permission(' in content:
    print("✅ As funções já foram adicionadas!")
else:
    print("❌ Funções não encontradas. Adicionando...")
    
    # Código das 3 funções
    functions_to_add = '''

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
'''
    
    # Adicionar as funções no final do arquivo
    content += functions_to_add
    
    # Salvar o arquivo
    views_file.write_text(content, encoding='utf-8')
    print("✅ Funções adicionadas com sucesso!")
    print("\nAgora execute: python clear_cache.py")
    print("E depois: python manage.py makemigrations")
