"""
Utilitários avançados para Active Directory - SupplyConnect
Funções para listar Grupos, OUs (Organizational Units) e Usuários do AD
"""

from ldap3 import Server, Connection, ALL, SUBTREE
from ldap3.core.exceptions import LDAPException
import logging

logger = logging.getLogger(__name__)


class ADConnection:
    """
    Classe para gerenciar conexão com Active Directory.
    """
    
    def __init__(self, ldap_config):
        """
        Inicializa a conexão com o AD usando a configuração do banco.
        
        Args:
            ldap_config: Objeto LdapDirectory com as configurações do AD
        """
        self.ldap_config = ldap_config
        self.server = None
        self.connection = None
    
    def connect(self):
        """
        Estabelece conexão com o servidor AD.
        
        Returns:
            bool: True se conectou com sucesso, False caso contrário
        """
        try:
            # Criar servidor
            self.server = Server(
                self.ldap_config.ldap_server,
                port=self.ldap_config.port,
                get_info=ALL,
                use_ssl=self.ldap_config.use_ssl
            )
            
            # Criar conexão
            self.connection = Connection(
                self.server,
                user=self.ldap_config.bind_user_dn,
                password=self.ldap_config.get_password(),
                auto_bind=True
            )
            
            logger.info(f"✅ Conectado ao AD: {self.ldap_config.ldap_server}")
            return True
            
        except LDAPException as e:
            logger.error(f"❌ Erro ao conectar ao AD: {str(e)}")
            return False
    
    def disconnect(self):
        """Desconecta do servidor AD."""
        if self.connection:
            self.connection.unbind()
            logger.info("🔌 Desconectado do AD")
    
    def __enter__(self):
        """Suporte para uso com 'with' statement."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Fecha conexão automaticamente."""
        self.disconnect()


def list_ad_groups(ldap_config, search_base=None):
    """
    Lista todos os grupos do Active Directory.
    
    Args:
        ldap_config: Configuração do LDAP (objeto LdapDirectory)
        search_base: Base DN para busca (opcional, usa base_dn se não especificado)
    
    Returns:
        list: Lista de dicionários com informações dos grupos
              [{'dn': '...', 'name': '...', 'description': '...', 'member_count': 0}]
    """
    groups = []
    
    try:
        with ADConnection(ldap_config) as ad:
            if not ad.connection:
                return groups
            
            # Define base de busca
            base = search_base or ldap_config.base_dn
            
            # Filtro para buscar grupos
            # objectClass=group para grupos do AD
            search_filter = '(objectClass=group)'
            
            # Atributos que queremos retornar
            attributes = [
                'cn',              # Nome comum
                'name',            # Nome
                'description',     # Descrição
                'distinguishedName',  # DN completo
                'member',          # Membros do grupo
                'objectClass',     # Classes do objeto
                'sAMAccountName'   # Nome da conta SAM
            ]
            
            # Realizar busca
            ad.connection.search(
                search_base=base,
                search_filter=search_filter,
                search_scope=SUBTREE,
                attributes=attributes
            )
            
            # Processar resultados
            for entry in ad.connection.entries:
                group_info = {
                    'dn': str(entry.distinguishedName),
                    'name': str(entry.cn) if hasattr(entry, 'cn') else str(entry.name),
                    'sam_account': str(entry.sAMAccountName) if hasattr(entry, 'sAMAccountName') else '',
                    'description': str(entry.description) if hasattr(entry, 'description') else '',
                    'member_count': len(entry.member) if hasattr(entry, 'member') else 0,
                    'members': [str(m) for m in entry.member] if hasattr(entry, 'member') else []
                }
                groups.append(group_info)
            
            logger.info(f"✅ Encontrados {len(groups)} grupos no AD")
    
    except LDAPException as e:
        logger.error(f"❌ Erro ao listar grupos do AD: {str(e)}")
    except Exception as e:
        logger.error(f"❌ Erro inesperado ao listar grupos: {str(e)}")
    
    return groups


def list_organizational_units(ldap_config, search_base=None):
    """
    Lista todas as Organizational Units (OUs) do Active Directory.
    
    Args:
        ldap_config: Configuração do LDAP (objeto LdapDirectory)
        search_base: Base DN para busca (opcional, usa base_dn se não especificado)
    
    Returns:
        list: Lista de dicionários com informações das OUs
              [{'dn': '...', 'name': '...', 'description': '...', 'path': '...'}]
    """
    ous = []
    
    try:
        with ADConnection(ldap_config) as ad:
            if not ad.connection:
                return ous
            
            # Define base de busca
            base = search_base or ldap_config.base_dn
            
            # Filtro para buscar OUs
            search_filter = '(objectClass=organizationalUnit)'
            
            # Atributos que queremos retornar
            attributes = [
                'ou',              # Nome da OU
                'name',            # Nome
                'description',     # Descrição
                'distinguishedName'  # DN completo
            ]
            
            # Realizar busca
            ad.connection.search(
                search_base=base,
                search_filter=search_filter,
                search_scope=SUBTREE,
                attributes=attributes
            )
            
            # Processar resultados
            for entry in ad.connection.entries:
                # Extrair caminho hierárquico da OU
                dn = str(entry.distinguishedName)
                path_parts = dn.split(',')
                path = ' > '.join([p.split('=')[1] for p in path_parts if p.startswith('OU=')])
                
                ou_info = {
                    'dn': dn,
                    'name': str(entry.ou) if hasattr(entry, 'ou') else str(entry.name),
                    'description': str(entry.description) if hasattr(entry, 'description') else '',
                    'path': path,
                    'level': len([p for p in path_parts if p.startswith('OU=')])
                }
                ous.append(ou_info)
            
            # Ordenar por nível hierárquico
            ous.sort(key=lambda x: (x['level'], x['name']))
            
            logger.info(f"✅ Encontradas {len(ous)} OUs no AD")
    
    except LDAPException as e:
        logger.error(f"❌ Erro ao listar OUs do AD: {str(e)}")
    except Exception as e:
        logger.error(f"❌ Erro inesperado ao listar OUs: {str(e)}")
    
    return ous


def get_ou_users_count(ldap_config, ou_dn):
    """
    Conta quantos usuários existem em uma OU específica.
    
    Args:
        ldap_config: Configuração do LDAP
        ou_dn: Distinguished Name da OU
    
    Returns:
        int: Quantidade de usuários na OU
    """
    try:
        with ADConnection(ldap_config) as ad:
            if not ad.connection:
                return 0
            
            # Filtro para buscar usuários
            search_filter = '(&(objectClass=user)(objectCategory=person))'
            
            # Buscar apenas na OU específica (SCOPE_ONELEVEL = apenas nível atual)
            ad.connection.search(
                search_base=ou_dn,
                search_filter=search_filter,
                search_scope=SUBTREE,
                attributes=['cn']
            )
            
            return len(ad.connection.entries)
    
    except Exception as e:
        logger.error(f"❌ Erro ao contar usuários na OU: {str(e)}")
        return 0


def get_group_members(ldap_config, group_dn):
    """
    Lista todos os membros de um grupo específico.
    
    Args:
        ldap_config: Configuração do LDAP
        group_dn: Distinguished Name do grupo
    
    Returns:
        list: Lista de membros [{'dn': '...', 'name': '...', 'email': '...'}]
    """
    members = []
    
    try:
        with ADConnection(ldap_config) as ad:
            if not ad.connection:
                return members
            
            # Buscar o grupo específico
            ad.connection.search(
                search_base=group_dn,
                search_filter='(objectClass=group)',
                search_scope=SUBTREE,
                attributes=['member']
            )
            
            if not ad.connection.entries:
                return members
            
            # Pegar lista de membros
            entry = ad.connection.entries[0]
            if not hasattr(entry, 'member'):
                return members
            
            # Para cada membro, buscar suas informações
            for member_dn in entry.member:
                ad.connection.search(
                    search_base=str(member_dn),
                    search_filter='(objectClass=*)',
                    search_scope=SUBTREE,
                    attributes=['cn', 'name', 'mail', 'sAMAccountName']
                )
                
                if ad.connection.entries:
                    member_entry = ad.connection.entries[0]
                    member_info = {
                        'dn': str(member_dn),
                        'name': str(member_entry.cn) if hasattr(member_entry, 'cn') else '',
                        'username': str(member_entry.sAMAccountName) if hasattr(member_entry, 'sAMAccountName') else '',
                        'email': str(member_entry.mail) if hasattr(member_entry, 'mail') else ''
                    }
                    members.append(member_info)
    
    except Exception as e:
        logger.error(f"❌ Erro ao listar membros do grupo: {str(e)}")
    
    return members


def test_ad_connection(ldap_config):
    """
    Testa a conexão com o Active Directory.
    
    Args:
        ldap_config: Configuração do LDAP
    
    Returns:
        tuple: (success: bool, message: str, details: dict)
    """
    try:
        with ADConnection(ldap_config) as ad:
            if not ad.connection:
                return False, "Não foi possível conectar ao servidor AD", {}
            
            # Buscar informações do servidor
            server_info = {
                'host': ldap_config.ldap_server,
                'port': ldap_config.port,
                'ssl': ldap_config.use_ssl,
                'base_dn': ldap_config.base_dn
            }
            
            # Tentar buscar 1 usuário para validar
            ad.connection.search(
                search_base=ldap_config.base_dn,
                search_filter='(objectClass=user)',
                search_scope=SUBTREE,
                attributes=['cn'],
                size_limit=1
            )
            
            return True, "✅ Conexão estabelecida com sucesso!", server_info
    
    except Exception as e:
        return False, f"❌ Erro ao testar conexão: {str(e)}", {}
    
def list_ad_users(ldap_config):
    """
    Lista todos os usuários do Active Directory.
    
    Args:
        ldap_config: Instância de LdapDirectory com as configurações
    
    Returns:
        Lista de dicionários com informações dos usuários
    """
    from ldap3 import Server, Connection, ALL, SUBTREE
    
    users = []
    
    try:
        # Conectar ao AD
        server = Server(
            ldap_config.ldap_server,
            port=ldap_config.port,
            get_info=ALL
        )
        
        conn = Connection(
            server,
            user=ldap_config.bind_user_dn,
            password=ldap_config.get_password(),
            auto_bind=True
        )
        
        # Buscar usuários
        conn.search(
            search_base=ldap_config.base_dn,
            search_filter='(&(objectClass=user)(objectCategory=person))',
            search_scope=SUBTREE,
            attributes=[
                'sAMAccountName', 
                'mail', 
                'givenName', 
                'sn', 
                'displayName',
                'department',
                'title',
                'distinguishedName'
            ]
        )
        
        for entry in conn.entries:
            user_data = {
                'dn': str(entry.distinguishedName),
                'username': str(entry.sAMAccountName) if entry.sAMAccountName else '',
                'email': str(entry.mail) if entry.mail else '',
                'first_name': str(entry.givenName) if entry.givenName else '',
                'last_name': str(entry.sn) if entry.sn else '',
                'display_name': str(entry.displayName) if entry.displayName else '',
                'department': str(entry.department) if entry.department else '',
                'title': str(entry.title) if entry.title else '',
            }
            users.append(user_data)
        
        conn.unbind()
        
    except Exception as e:
        print(f"Erro ao listar usuários do AD: {e}")
        raise
    
    return users