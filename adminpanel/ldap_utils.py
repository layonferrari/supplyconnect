"""
Utilitários para conexão e teste LDAP/Active Directory.
"""
import ldap
from django.utils.translation import gettext as _

def test_ldap_connection(ldap_config):
    """
    Testa a conexão com o servidor LDAP/AD.
    """
    try:
        # Configurar conexão LDAP
        if ldap_config.use_ssl:
            ldap_server = f"ldaps://{ldap_config.ldap_server}:{ldap_config.port}"
        else:
            ldap_server = f"ldap://{ldap_config.ldap_server}:{ldap_config.port}"
        
        # Conectar ao servidor
        conn = ldap.initialize(ldap_server)
        
        # Configurar opções
        conn.set_option(ldap.OPT_REFERRALS, 0)
        conn.set_option(ldap.OPT_PROTOCOL_VERSION, 3)
        
        if ldap_config.use_tls:
            conn.start_tls_s()
        
        # Tentar bind com as credenciais
        conn.simple_bind_s(ldap_config.bind_user_dn, ldap_config.get_password())
        
        # Testar busca simples
        search_filter = ldap_config.search_filter.replace('{username}', '*')
        result = conn.search_s(
            ldap_config.get_user_search_base(),
            ldap.SCOPE_SUBTREE,
            search_filter,
            [ldap_config.attr_first_name, ldap_config.attr_last_name, ldap_config.attr_email]
        )
        
        conn.unbind()
        
        return True, _("Conexão bem-sucedida! Encontrados {} usuários.").format(len(result))
        
    except ldap.INVALID_CREDENTIALS:
        return False, _("Credenciais inválidas. Verifique o usuário e senha de bind.")
    except ldap.SERVER_DOWN:
        return False, _("Servidor não encontrado. Verifique o endereço e porta.")
    except ldap.LDAPError as e:
        return False, _("Erro LDAP: {}").format(str(e))
    except Exception as e:
        return False, _("Erro inesperado: {}").format(str(e))