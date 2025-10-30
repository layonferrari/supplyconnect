"""
Script para preencher automaticamente os arquivos de tradução do Django.
Execute: python populate_translations.py
"""

import os
import re

# Dicionário com todas as traduções
TRANSLATIONS = {
    'en': {
        # Textos gerais
        'Ilpea SupplyConnect': 'Ilpea SupplyConnect',
        'Bem-vindo ao Portal': 'Welcome to the Portal',
        'Sou Parceiro': 'I am a Partner',
        'Sou Colaborador': 'I am an Employee',
        'Idioma': 'Language',
        
        # Login Parceiro
        'Login Parceiro': 'Partner Login',
        'Portal do Parceiro': 'Partner Portal',
        'E-mail': 'E-mail',
        'Senha': 'Password',
        'Entrar': 'Sign In',
        'Voltar': 'Back',
        
        # Dashboard Fornecedor
        'Portal do Fornecedor': 'Supplier Portal',
        'Sair': 'Logout',
        'Meus Contratos': 'My Contracts',
        'Visualize e gerencie seus contratos ativos com a ILPEA.': 'View and manage your active contracts with ILPEA.',
        'Pendências': 'Pending Items',
        'Acompanhe ações pendentes e prazos importantes.': 'Track pending actions and important deadlines.',
        'Notificações': 'Notifications',
        'Receba atualizações sobre suas interações com as filiais.': 'Receive updates about your interactions with branches.',
        'Relatórios': 'Reports',
        'Acesse relatórios de desempenho e qualidade.': 'Access performance and quality reports.',
        'Em breve': 'Coming soon',
        'Estamos construindo algo incrível!': 'We are building something amazing!',
        'Novas funcionalidades serão adicionadas em breve para melhorar sua experiência.': 'New features will be added soon to improve your experience.',
        'Todos os direitos reservados': 'All rights reserved',
        
        # Acesso Negado
        'Acesso Negado': 'Access Denied',
        'Você não tem permissão para acessar esta página.': 'You do not have permission to access this page.',
        'Esta área é exclusiva para fornecedores autorizados.': 'This area is exclusive to authorized suppliers.',
        'Página Inicial': 'Home',
        'Fazer Login': 'Login',
        
        # Login Colaborador
        'Login Colaborador': 'Employee Login',
        'Área do Colaborador': 'Employee Area',
        'Em Desenvolvimento': 'Under Development',
        'O login para colaboradores está sendo construído com integração ao Active Directory.': 'Employee login is being built with Active Directory integration.',
        'Autenticação via Active Directory por país': 'Authentication via Active Directory by country',
        'Acesso seguro com credenciais corporativas': 'Secure access with corporate credentials',
        'Sincronização automática de permissões': 'Automatic permission synchronization',
        'Suporte multi-idioma': 'Multi-language support',
        'Países suportados': 'Supported Countries',
        'Brasil, Argentina, México, Alemanha, Itália, China e Estados Unidos': 'Brazil, Argentina, Mexico, Germany, Italy, China and United States',
        'Voltar à Página Inicial': 'Back to Home',
    },
    
    'es': {
        # Textos gerais
        'Ilpea SupplyConnect': 'Ilpea SupplyConnect',
        'Bem-vindo ao Portal': 'Bienvenido al Portal',
        'Sou Parceiro': 'Soy Socio',
        'Sou Colaborador': 'Soy Empleado',
        'Idioma': 'Idioma',
        
        # Login Parceiro
        'Login Parceiro': 'Inicio de Sesión Socio',
        'Portal do Parceiro': 'Portal del Socio',
        'E-mail': 'Correo electrónico',
        'Senha': 'Contraseña',
        'Entrar': 'Entrar',
        'Voltar': 'Volver',
        
        # Dashboard Fornecedor
        'Portal do Fornecedor': 'Portal del Proveedor',
        'Sair': 'Salir',
        'Meus Contratos': 'Mis Contratos',
        'Visualize e gerencie seus contratos ativos com a ILPEA.': 'Visualice y gestione sus contratos activos con ILPEA.',
        'Pendências': 'Pendientes',
        'Acompanhe ações pendentes e prazos importantes.': 'Realice seguimiento de acciones pendientes y plazos importantes.',
        'Notificações': 'Notificaciones',
        'Receba atualizações sobre suas interações com as filiais.': 'Reciba actualizaciones sobre sus interacciones con las sucursales.',
        'Relatórios': 'Informes',
        'Acesse relatórios de desempenho e qualidade.': 'Acceda a informes de rendimiento y calidad.',
        'Em breve': 'Próximamente',
        'Estamos construindo algo incrível!': '¡Estamos construyendo algo increíble!',
        'Novas funcionalidades serão adicionadas em breve para melhorar sua experiência.': 'Nuevas funcionalidades se agregarán pronto para mejorar su experiencia.',
        'Todos os direitos reservados': 'Todos los derechos reservados',
        
        # Acesso Negado
        'Acesso Negado': 'Acceso Denegado',
        'Você não tem permissão para acessar esta página.': 'No tiene permiso para acceder a esta página.',
        'Esta área é exclusiva para fornecedores autorizados.': 'Esta área es exclusiva para proveedores autorizados.',
        'Página Inicial': 'Página Inicial',
        'Fazer Login': 'Iniciar Sesión',
        
        # Login Colaborador
        'Login Colaborador': 'Inicio de Sesión Empleado',
        'Área do Colaborador': 'Área del Empleado',
        'Em Desenvolvimento': 'En Desarrollo',
        'O login para colaboradores está sendo construído com integração ao Active Directory.': 'El inicio de sesión para empleados está siendo construido con integración a Active Directory.',
        'Autenticação via Active Directory por país': 'Autenticación vía Active Directory por país',
        'Acesso seguro com credenciais corporativas': 'Acceso seguro con credenciales corporativas',
        'Sincronização automática de permissões': 'Sincronización automática de permisos',
        'Suporte multi-idioma': 'Soporte multiidioma',
        'Países suportados': 'Países Soportados',
        'Brasil, Argentina, México, Alemanha, Itália, China e Estados Unidos': 'Brasil, Argentina, México, Alemania, Italia, China y Estados Unidos',
        'Voltar à Página Inicial': 'Volver a la Página Inicial',
    },
    
    'de': {
        # Textos gerais
        'Ilpea SupplyConnect': 'Ilpea SupplyConnect',
        'Bem-vindo ao Portal': 'Willkommen im Portal',
        'Sou Parceiro': 'Ich bin Partner',
        'Sou Colaborador': 'Ich bin Mitarbeiter',
        'Idioma': 'Sprache',
        
        # Login Parceiro
        'Login Parceiro': 'Partner-Anmeldung',
        'Portal do Parceiro': 'Partner-Portal',
        'E-mail': 'E-Mail',
        'Senha': 'Passwort',
        'Entrar': 'Anmelden',
        'Voltar': 'Zurück',
        
        # Dashboard Fornecedor
        'Portal do Fornecedor': 'Lieferanten-Portal',
        'Sair': 'Abmelden',
        'Meus Contratos': 'Meine Verträge',
        'Visualize e gerencie seus contratos ativos com a ILPEA.': 'Sehen und verwalten Sie Ihre aktiven Verträge mit ILPEA.',
        'Pendências': 'Ausstehend',
        'Acompanhe ações pendentes e prazos importantes.': 'Verfolgen Sie ausstehende Aktionen und wichtige Fristen.',
        'Notificações': 'Benachrichtigungen',
        'Receba atualizações sobre suas interações com as filiais.': 'Erhalten Sie Updates über Ihre Interaktionen mit Niederlassungen.',
        'Relatórios': 'Berichte',
        'Acesse relatórios de desempenho e qualidade.': 'Greifen Sie auf Leistungs- und Qualitätsberichte zu.',
        'Em breve': 'Demnächst',
        'Estamos construindo algo incrível!': 'Wir bauen etwas Unglaubliches!',
        'Novas funcionalidades serão adicionadas em breve para melhorar sua experiência.': 'Neue Funktionen werden bald hinzugefügt, um Ihr Erlebnis zu verbessern.',
        'Todos os direitos reservados': 'Alle Rechte vorbehalten',
        
        # Acesso Negado
        'Acesso Negado': 'Zugriff verweigert',
        'Você não tem permissão para acessar esta página.': 'Sie haben keine Berechtigung, auf diese Seite zuzugreifen.',
        'Esta área é exclusiva para fornecedores autorizados.': 'Dieser Bereich ist ausschließlich für autorisierte Lieferanten.',
        'Página Inicial': 'Startseite',
        'Fazer Login': 'Anmelden',
        
        # Login Colaborador
        'Login Colaborador': 'Mitarbeiter-Anmeldung',
        'Área do Colaborador': 'Mitarbeiterbereich',
        'Em Desenvolvimento': 'In Entwicklung',
        'O login para colaboradores está sendo construído com integração ao Active Directory.': 'Die Mitarbeiter-Anmeldung wird mit Active Directory-Integration entwickelt.',
        'Autenticação via Active Directory por país': 'Authentifizierung über Active Directory nach Land',
        'Acesso seguro com credenciais corporativas': 'Sicherer Zugang mit Unternehmensanmeldedaten',
        'Sincronização automática de permissões': 'Automatische Synchronisierung von Berechtigungen',
        'Suporte multi-idioma': 'Mehrsprachige Unterstützung',
        'Países suportados': 'Unterstützte Länder',
        'Brasil, Argentina, México, Alemanha, Itália, China e Estados Unidos': 'Brasilien, Argentinien, Mexiko, Deutschland, Italien, China und USA',
        'Voltar à Página Inicial': 'Zurück zur Startseite',
    },
    
    'it': {
        # Textos gerais
        'Ilpea SupplyConnect': 'Ilpea SupplyConnect',
        'Bem-vindo ao Portal': 'Benvenuto al Portale',
        'Sou Parceiro': 'Sono un Partner',
        'Sou Colaborador': 'Sono un Dipendente',
        'Idioma': 'Lingua',
        
        # Login Parceiro
        'Login Parceiro': 'Login Partner',
        'Portal do Parceiro': 'Portale Partner',
        'E-mail': 'E-mail',
        'Senha': 'Password',
        'Entrar': 'Accedi',
        'Voltar': 'Indietro',
        
        # Dashboard Fornecedor
        'Portal do Fornecedor': 'Portale Fornitore',
        'Sair': 'Esci',
        'Meus Contratos': 'I Miei Contratti',
        'Visualize e gerencie seus contratos ativos com a ILPEA.': 'Visualizza e gestisci i tuoi contratti attivi con ILPEA.',
        'Pendências': 'In Sospeso',
        'Acompanhe ações pendentes e prazos importantes.': 'Monitora azioni in sospeso e scadenze importanti.',
        'Notificações': 'Notifiche',
        'Receba atualizações sobre suas interações com as filiais.': 'Ricevi aggiornamenti sulle tue interazioni con le filiali.',
        'Relatórios': 'Rapporti',
        'Acesse relatórios de desempenho e qualidade.': 'Accedi ai rapporti di prestazioni e qualità.',
        'Em breve': 'Prossimamente',
        'Estamos construindo algo incrível!': 'Stiamo costruendo qualcosa di incredibile!',
        'Novas funcionalidades serão adicionadas em breve para melhorar sua experiência.': 'Nuove funzionalità saranno aggiunte presto per migliorare la tua esperienza.',
        'Todos os direitos reservados': 'Tutti i diritti riservati',
        
        # Acesso Negado
        'Acesso Negado': 'Accesso Negato',
        'Você não tem permissão para acessar esta página.': 'Non hai il permesso di accedere a questa pagina.',
        'Esta área é exclusiva para fornecedores autorizados.': 'Quest\'area è esclusiva per fornitori autorizzati.',
        'Página Inicial': 'Pagina Iniziale',
        'Fazer Login': 'Accedi',
        
        # Login Colaborador
        'Login Colaborador': 'Login Dipendente',
        'Área do Colaborador': 'Area Dipendente',
        'Em Desenvolvimento': 'In Sviluppo',
        'O login para colaboradores está sendo construído com integração ao Active Directory.': 'Il login per i dipendenti è in fase di sviluppo con integrazione Active Directory.',
        'Autenticação via Active Directory por país': 'Autenticazione tramite Active Directory per paese',
        'Acesso seguro com credenciais corporativas': 'Accesso sicuro con credenziali aziendali',
        'Sincronização automática de permissões': 'Sincronizzazione automatica dei permessi',
        'Suporte multi-idioma': 'Supporto multilingua',
        'Países suportados': 'Paesi Supportati',
        'Brasil, Argentina, México, Alemanha, Itália, China e Estados Unidos': 'Brasile, Argentina, Messico, Germania, Italia, Cina e Stati Uniti',
        'Voltar à Página Inicial': 'Torna alla Pagina Iniziale',
    },
    
    'zh_Hans': {
        # Textos gerais
        'Ilpea SupplyConnect': 'Ilpea SupplyConnect',
        'Bem-vindo ao Portal': '欢迎来到门户',
        'Sou Parceiro': '我是合作伙伴',
        'Sou Colaborador': '我是员工',
        'Idioma': '语言',
        
        # Login Parceiro
        'Login Parceiro': '合作伙伴登录',
        'Portal do Parceiro': '合作伙伴门户',
        'E-mail': '电子邮件',
        'Senha': '密码',
        'Entrar': '登录',
        'Voltar': '返回',
        
        # Dashboard Fornecedor
        'Portal do Fornecedor': '供应商门户',
        'Sair': '退出',
        'Meus Contratos': '我的合同',
        'Visualize e gerencie seus contratos ativos com a ILPEA.': '查看和管理您与ILPEA的有效合同。',
        'Pendências': '待办事项',
        'Acompanhe ações pendentes e prazos importantes.': '跟踪待办事项和重要截止日期。',
        'Notificações': '通知',
        'Receba atualizações sobre suas interações com as filiais.': '接收有关您与分支机构互动的更新。',
        'Relatórios': '报告',
        'Acesse relatórios de desempenho e qualidade.': '访问绩效和质量报告。',
        'Em breve': '即将推出',
        'Estamos construindo algo incrível!': '我们正在构建令人惊叹的东西！',
        'Novas funcionalidades serão adicionadas em breve para melhorar sua experiência.': '新功能即将推出，以改善您的体验。',
        'Todos os direitos reservados': '版权所有',
        
        # Acesso Negado
        'Acesso Negado': '访问被拒绝',
        'Você não tem permissão para acessar esta página.': '您没有权限访问此页面。',
        'Esta área é exclusiva para fornecedores autorizados.': '此区域仅限授权供应商访问。',
        'Página Inicial': '首页',
        'Fazer Login': '登录',
        
        # Login Colaborador
        'Login Colaborador': '员工登录',
        'Área do Colaborador': '员工区域',
        'Em Desenvolvimento': '开发中',
        'O login para colaboradores está sendo construído com integração ao Active Directory.': '员工登录正在开发中，将集成Active Directory。',
        'Autenticação via Active Directory por país': '按国家通过Active Directory进行身份验证',
        'Acesso seguro com credenciais corporativas': '使用公司凭据安全访问',
        'Sincronização automática de permissões': '自动同步权限',
        'Suporte multi-idioma': '多语言支持',
        'Países suportados': '支持的国家',
        'Brasil, Argentina, México, Alemanha, Itália, China e Estados Unidos': '巴西、阿根廷、墨西哥、德国、意大利、中国和美国',
        'Voltar à Página Inicial': '返回首页',
    },
}


def update_po_file(language_code, translations):
    """Atualiza um arquivo .po com as traduções fornecidas."""
    po_file = f'locale/{language_code}/LC_MESSAGES/django.po'
    
    if not os.path.exists(po_file):
        print(f"❌ Arquivo não encontrado: {po_file}")
        return False
    
    with open(po_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Para cada tradução, encontrar o msgid e preencher o msgstr
    for original, translated in translations.items():
        # Escapa aspas duplas
        original_escaped = original.replace('"', '\\"')
        translated_escaped = translated.replace('"', '\\"')
        
        # Padrão para encontrar msgid seguido de msgstr vazio
        pattern = f'msgid "{original_escaped}"\\nmsgstr ""'
        replacement = f'msgid "{original_escaped}"\\nmsgstr "{translated_escaped}"'
        
        content = content.replace(pattern, replacement)
    
    # Salva o arquivo atualizado
    with open(po_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Traduções adicionadas: {language_code}")
    return True


def main():
    """Função principal que atualiza todos os arquivos de tradução."""
    print("🌍 Iniciando preenchimento automático das traduções...\n")
    
    for lang_code, translations in TRANSLATIONS.items():
        update_po_file(lang_code, translations)
    
    print("\n✅ Todas as traduções foram preenchidas com sucesso!")
    print("\n📝 Próximo passo: Execute 'python manage.py compilemessages' para compilar as traduções.")


if __name__ == "__main__":
    main()