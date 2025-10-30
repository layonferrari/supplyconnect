"""Script corrigido para preencher traduções nos arquivos .po"""
import re

TRANSLATIONS = {
    'en': {
        'Ilpea SupplyConnect': 'Ilpea SupplyConnect',
        'Bem-vindo ao Portal': 'Welcome to the Portal',
        'Sou Parceiro': 'I am a Partner',
        'Sou Colaborador': 'I am an Employee',
        'Idioma': 'Language',
        'Login Parceiro': 'Partner Login',
        'Portal do Parceiro': 'Partner Portal',
        'E-mail': 'E-mail',
        'Senha': 'Password',
        'Entrar': 'Sign In',
        'Voltar': 'Back',
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
        'Acesso Negado': 'Access Denied',
        'Você não tem permissão para acessar esta página.': 'You do not have permission to access this page.',
        'Esta área é exclusiva para fornecedores autorizados.': 'This area is exclusive to authorized suppliers.',
        'Página Inicial': 'Home',
        'Fazer Login': 'Login',
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
        'Configurações': 'Settings',
        'Personalize sua experiência no sistema': 'Customize your system experience',
        'Escolha o idioma que será usado em todo o sistema. Esta configuração será salva na sua conta.': 'Choose the language to be used throughout the system. This setting will be saved to your account.',
        'Salvar Configurações': 'Save Settings',
        'Cancelar': 'Cancel',
        'Dica': 'Tip',
        'Após salvar, todas as páginas do sistema serão automaticamente exibidas no idioma escolhido.': 'After saving, all system pages will automatically be displayed in the chosen language.',
    },
    'es': {
        'Ilpea SupplyConnect': 'Ilpea SupplyConnect',
        'Bem-vindo ao Portal': 'Bienvenido al Portal',
        'Sou Parceiro': 'Soy Socio',
        'Sou Colaborador': 'Soy Empleado',
        'Idioma': 'Idioma',
        'Login Parceiro': 'Inicio de Sesión Socio',
        'Portal do Parceiro': 'Portal del Socio',
        'E-mail': 'Correo electrónico',
        'Senha': 'Contraseña',
        'Entrar': 'Entrar',
        'Voltar': 'Volver',
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
        'Acesso Negado': 'Acceso Denegado',
        'Você não tem permissão para acessar esta página.': 'No tiene permiso para acceder a esta página.',
        'Esta área é exclusiva para fornecedores autorizados.': 'Esta área es exclusiva para proveedores autorizados.',
        'Página Inicial': 'Página Inicial',
        'Fazer Login': 'Iniciar Sesión',
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
        'Ilpea SupplyConnect': 'Ilpea SupplyConnect',
        'Bem-vindo ao Portal': 'Willkommen im Portal',
        'Sou Parceiro': 'Ich bin Partner',
        'Sou Colaborador': 'Ich bin Mitarbeiter',
        'Idioma': 'Sprache',
        'Login Parceiro': 'Partner-Anmeldung',
        'Portal do Parceiro': 'Partner-Portal',
        'E-mail': 'E-Mail',
        'Senha': 'Passwort',
        'Entrar': 'Anmelden',
        'Voltar': 'Zurück',
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
        'Acesso Negado': 'Zugriff verweigert',
        'Você não tem permissão para acessar esta página.': 'Sie haben keine Berechtigung, auf diese Seite zuzugreifen.',
        'Esta área é exclusiva para fornecedores autorizados.': 'Dieser Bereich ist ausschließlich für autorisierte Lieferanten.',
        'Página Inicial': 'Startseite',
        'Fazer Login': 'Anmelden',
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
        'Ilpea SupplyConnect': 'Ilpea SupplyConnect',
        'Bem-vindo ao Portal': 'Benvenuto al Portale',
        'Sou Parceiro': 'Sono un Partner',
        'Sou Colaborador': 'Sono un Dipendente',
        'Idioma': 'Lingua',
        'Login Parceiro': 'Login Partner',
        'Portal do Parceiro': 'Portale Partner',
        'E-mail': 'E-mail',
        'Senha': 'Password',
        'Entrar': 'Accedi',
        'Voltar': 'Indietro',
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
        'Acesso Negado': 'Accesso Negato',
        'Você não tem permissão para acessar esta página.': 'Non hai il permesso di accedere a questa pagina.',
        'Esta área é exclusiva para fornecedores autorizados.': 'Quest\'area è esclusiva per fornitori autorizzati.',
        'Página Inicial': 'Pagina Iniziale',
        'Fazer Login': 'Accedi',
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
        'Ilpea SupplyConnect': 'Ilpea SupplyConnect',
        'Bem-vindo ao Portal': '欢迎来到门户',
        'Sou Parceiro': '我是合作伙伴',
        'Sou Colaborador': '我是员工',
        'Idioma': '语言',
        'Login Parceiro': '合作伙伴登录',
        'Portal do Parceiro': '合作伙伴门户',
        'E-mail': '电子邮件',
        'Senha': '密码',
        'Entrar': '登录',
        'Voltar': '返回',
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
        'Acesso Negado': '访问被拒绝',
        'Você não tem permissão para acessar esta página.': '您没有权限访问此页面。',
        'Esta área é exclusiva para fornecedores autorizados.': '此区域仅限授权供应商访问。',
        'Página Inicial': '首页',
        'Fazer Login': '登录',
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

def fix_po_file(lang_code, translations):
    po_file = f'locale/{lang_code}/LC_MESSAGES/django.po'
    with open(po_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    new_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        new_lines.append(line)
        
        # Procura por msgid
        if line.startswith('msgid "') and not line.startswith('msgid ""'):
            # Extrai o texto do msgid (pode estar em múltiplas linhas)
            msgid_text = line[7:-2]  # Remove 'msgid "' e '"\n'
            
            # Verifica se continua na próxima linha
            j = i + 1
            while j < len(lines) and lines[j].startswith('"') and not lines[j].startswith('msgstr'):
                msgid_text += lines[j][1:-2]  # Remove '"' e '"\n'
                j += 1
            
            # Procura pela linha msgstr vazia
            if j < len(lines) and lines[j].strip() == 'msgstr ""':
                # Verifica se temos tradução para este texto
                if msgid_text in translations:
                    translated = translations[msgid_text]
                    new_lines.append(f'msgstr "{translated}"\n')
                    i = j + 1
                    continue
        
        i += 1
    
    with open(po_file, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print(f"✅ {lang_code} - Traduções corrigidas")

def main():
    print("🔧 Corrigindo arquivos de tradução...\n")
    for lang_code, translations in TRANSLATIONS.items():
        fix_po_file(lang_code, translations)
    print("\n✅ Concluído! Execute: python manage.py compilemessages")

if __name__ == "__main__":
    main()