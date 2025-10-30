"""
Backend de autenticação LDAP multi-país.
Permite autenticação usando Active Directory de diferentes países.
"""

import logging
from ldap3 import Server, Connection, ALL, NTLM
from ldap3.core.exceptions import LDAPException
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from adminpanel.models import LdapDirectory

User = get_user_model()
logger = logging.getLogger(__name__)


class MultiCountryLDAPBackend(ModelBackend):
    """
    Backend de autenticação LDAP com suporte a múltiplos países.
    Cada país tem sua própria configuração de Active Directory.
    """
    
    def authenticate(self, request, username=None, password=None, country_code=None, **kwargs):
        """
        Autentica um usuário usando o Active Directory do país especificado.
        
        Args:
            request: Request HTTP
            username (str): Nome de usuário (sAMAccountName)
            password (str): Senha do usuário
            country_code (str): Código do país (BR, AR, MX, etc)
        
        Returns:
            User: Objeto do usuário autenticado ou None
        """
        # Validação básica
        if not username or not password or not country_code:
            logger.warning("❌ Autenticação LDAP: parâmetros faltando")
            return None
        
        try:
            # Buscar configuração do AD do país
            ldap_config = LdapDirectory.objects.get(
                country_code=country_code,
                is_active=True
            )
        except LdapDirectory.DoesNotExist:
            logger.error(f"❌ Configuração LDAP não encontrada para país: {country_code}")
            return None
        
        # Tentar autenticar no AD
        try:
            user_info = self._authenticate_ldap(
                ldap_config=ldap_config,
                username=username,
                password=password
            )
            
            if not user_info:
                logger.warning(f"❌ Autenticação LDAP falhou para: {username}")
                return None
            
            # Criar ou atualizar usuário no Django
            user = self._get_or_create_user(
                username=username,
                user_info=user_info,
                country_code=country_code
            )
            
            logger.info(f"✅ Autenticação LDAP bem-sucedida: {username} ({country_code})")
            return user
        
        except Exception as e:
            logger.error(f"❌ Erro na autenticação LDAP: {str(e)}")
            return None
    
    def _authenticate_ldap(self, ldap_config, username, password):
        """
        Realiza a autenticação no servidor LDAP.
        
        Args:
            ldap_config (LdapDirectory): Configuração do AD
            username (str): Nome de usuário
            password (str): Senha
        
        Returns:
            dict: Informações do usuário ou None se falhar
        """
        try:
            # Configurar servidor LDAP
            server = Server(
                ldap_config.get_connection_string(),
                get_info=ALL
            )
            
            # Montar DN do usuário para bind
            # Formato: usuario@dominio ou DOMINIO\usuario
            user_dn = f"{username}@{ldap_config.base_dn.replace('DC=', '').replace(',', '.')}"
            
            # Tentar conectar com credenciais do usuário
            conn = Connection(
                server,
                user=user_dn,
                password=password,
                auto_bind=True
            )
            
            if not conn.bind():
                logger.warning(f"❌ Bind LDAP falhou para: {username}")
                return None
            
            # Buscar informações do usuário
            search_filter = ldap_config.search_filter.format(username=username)
            search_base = ldap_config.get_user_search_base()
            
            conn.search(
                search_base=search_base,
                search_filter=search_filter,
                attributes=[
                    ldap_config.attr_first_name,
                    ldap_config.attr_last_name,
                    ldap_config.attr_email,
                    'sAMAccountName'
                ]
            )
            
            if not conn.entries:
                logger.warning(f"❌ Usuário não encontrado no AD: {username}")
                return None
            
            # Extrair informações do primeiro resultado
            entry = conn.entries[0]
            user_info = {
                'username': str(entry['sAMAccountName']),
                'first_name': str(entry[ldap_config.attr_first_name]) if entry[ldap_config.attr_first_name] else '',
                'last_name': str(entry[ldap_config.attr_last_name]) if entry[ldap_config.attr_last_name] else '',
                'email': str(entry[ldap_config.attr_email]) if entry[ldap_config.attr_email] else '',
            }
            
            conn.unbind()
            
            logger.info(f"✅ Informações obtidas do AD: {user_info['username']}")
            return user_info
        
        except LDAPException as e:
            logger.error(f"❌ Erro LDAP: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"❌ Erro inesperado na autenticação LDAP: {str(e)}")
            return None
    
    def _get_or_create_user(self, username, user_info, country_code):
        """
        Busca ou cria um usuário no Django com base nas informações do AD.
        
        Args:
            username (str): Nome de usuário
            user_info (dict): Informações do AD
            country_code (str): Código do país
        
        Returns:
            User: Objeto do usuário
        """
        try:
            # Buscar usuário existente
            user = User.objects.get(username=username)
            
            # Atualizar informações do AD
            user.first_name = user_info.get('first_name', '')
            user.last_name = user_info.get('last_name', '')
            user.email = user_info.get('email', '')
            user.country_code = country_code
            user.is_staff = True  # Colaborador tem acesso ao admin
            user.save()
            
            logger.info(f"✅ Usuário atualizado: {username}")
        
        except User.DoesNotExist:
            # Criar novo usuário
            user = User.objects.create_user(
                username=username,
                email=user_info.get('email', ''),
                first_name=user_info.get('first_name', ''),
                last_name=user_info.get('last_name', ''),
                country_code=country_code,
                is_staff=True,  # Colaborador tem acesso ao admin
                is_supplier=False
            )
            
            # Usuário LDAP não tem senha no Django (autentica sempre no AD)
            user.set_unusable_password()
            user.save()
            
            logger.info(f"✅ Novo usuário criado: {username}")
        
        return user
    
    def get_user(self, user_id):
        """
        Retorna um usuário pelo ID.
        
        Args:
            user_id (int): ID do usuário
        
        Returns:
            User: Objeto do usuário ou None
        """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None