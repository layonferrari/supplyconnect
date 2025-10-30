# 🔒 Ilpea SupplyConnect – Documentação Completa v3.0

Este documento contém **todo o contexto técnico, implementações realizadas, estrutura do projeto e próximos passos** para continuar o desenvolvimento do sistema.

**Última Atualização:** 29/10/2025  
**Versão:** 3.0  
**Status:** Sistema de autenticação multi-país COMPLETO e FUNCIONANDO

---

## 🧭 Como o assistente deve se comportar

- Ser **extremamente didático** e **guiar passo a passo** (um arquivo por vez)
- Explicar **onde criar/editar** cada arquivo (com caminho completo)
- Confirmar ao fim de cada passo com: 👉 "Pronto? Me confirme para irmos ao próximo passo."
- Entregar **blocos de código completos**, prontos para colar
- Não pedir confirmações desnecessárias
- Se houver erro, identificar claramente a causa provável e o arquivo a corrigir
- Linguagem: **português do Brasil**, formal e clara
- Nunca mostrar variáveis sensíveis do `.env`
- Seguir sempre a estrutura e segurança já definidas

---

## 🌐 Contexto do Sistema

O **Ilpea SupplyConnect** é o sistema global da ILPEA para controle e comunicação com fornecedores.  
Centraliza contratos, planos de ação, reclamações e comunicações entre fornecedores e filiais globais.

### Empresas ILPEA por País:
- 🇧🇷 **Brasil**: Matriz em Joinville/SC
- 🇦🇷 **Argentina**: Buenos Aires
- 🇲🇽 **México**: Cidade do México
- 🇩🇪 **Alemanha**: Frankfurt
- 🇮🇹 **Itália**: Milão
- 🇨🇳 **China**: Xangai
- 🇺🇸 **Estados Unidos**: Miami

---

## ⚙️ Arquitetura Técnica

| Componente | Tecnologia | Detalhes |
|------------|------------|----------|
| **Backend** | Django 5.0.7 + Django REST Framework | Python 3.13.2 |
| **Banco de Dados** | PostgreSQL | Com extensão `pgvector` |
| **Autenticação** | Multi-método | Admin Local + LDAP + Fornecedores |
| **Criptografia** | AES-256-ECB | PyCryptodome com `CRYPTO_MASTER_KEY` |
| **LDAP** | ldap3 | Biblioteca Python para Active Directory |
| **SMTP** | HCL Notes (IBM) | Servidor corporativo |
| **SSL** | Certificado wildcard | `*.ilpea.com.br` |
| **Infraestrutura** | FortiGate 90G | Domínio: `supplyconnect.ilpea.com.br` |
| **Idiomas** | 6 idiomas | PT-BR, EN, ES, DE, IT, ZH-HANS |

---

## 🗂️ Estrutura Completa do Projeto

```
D:\Projeto\SupplyConnect\
├── accounts/
│   ├── migrations/
│   │   ├── 0001_initial.py
│   │   └── 0002_user_is_supplier_user_preferred_language.py
│   ├── templates/
│   │   └── accounts/
│   │       ├── home_choice.html
│   │       ├── partner_login.html
│   │       ├── collaborator_login.html
│   │       ├── supplier_dashboard.html
│   │       ├── collaborator_dashboard.html
│   │       ├── user_settings.html
│   │       └── forbidden.html
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── backends.py        # ✅ NOVO - Backend LDAP multi-país
│   ├── forms.py           # PartnerLoginForm, CollaboratorLoginForm, UserLanguagePreferenceForm
│   ├── middleware.py      # UserLanguageMiddleware
│   ├── models.py          # User (customizado com preferred_language, country_code)
│   ├── urls.py            # Rotas de autenticação e dashboard
│   └── views.py           # Views de login, dashboard, settings, logout
├── adminpanel/
│   ├── migrations/
│   ├── models.py          # LdapDirectory, SmtpConfiguration, LdapConfig, SmtpConfig, SslConfig
│   ├── encryption.py      # Funções AES (encrypt_text, decrypt_text, test_encryption)
│   ├── urls.py
│   ├── views.py
│   └── admin.py
├── core/
│   ├── models.py          # CompanyUnit e outros modelos base
│   └── ...
├── suppliers/             # App para gestão de fornecedores (em desenvolvimento)
├── contracts/             # App para gestão de contratos (em desenvolvimento)
├── quality/               # App para gestão de qualidade (em desenvolvimento)
├── notifications/         # App para notificações (em desenvolvimento)
├── reports/               # App para relatórios (em desenvolvimento)
├── templates/
│   └── (vazio por enquanto)
├── static/
│   └── (vazio por enquanto)
├── media/
├── locale/                # Sistema de traduções
│   ├── en/LC_MESSAGES/
│   │   ├── django.po
│   │   └── django.mo
│   ├── es/LC_MESSAGES/
│   │   ├── django.po
│   │   └── django.mo
│   ├── de/LC_MESSAGES/
│   │   ├── django.po
│   │   └── django.mo
│   ├── it/LC_MESSAGES/
│   │   ├── django.po
│   │   └── django.mo
│   └── zh_Hans/LC_MESSAGES/
│       ├── django.po
│       └── django.mo
├── supplyconnect/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py        # Configurações completas (i18n, middleware, backends, logging)
│   ├── urls.py            # URLs principais com i18n_patterns
│   └── wsgi.py
├── .env                   # Variáveis de ambiente (não versionado)
├── .gitignore
├── manage.py
└── requirements.txt
```

---

## 🎨 Identidade Visual

### Cores Oficiais ILPEA:
- **Azul Principal**: `#0091DA`
- **Azul Escuro**: `#005B9A`
- **Branco**: `#FFFFFF`
- **Cinza Escuro (fundos)**: `#0f172a`, `#1e293b`
- **Cinza Claro (textos)**: `#e2e8f0`, `#cbd5e1`

### Design Pattern:
- Gradientes azuis em headers: `linear-gradient(135deg, #005B9A 0%, #0091DA 100%)`
- Cards com border-left azul: `border-left: 4px solid #0091DA`
- Sombras suaves: `box-shadow: 0 8px 16px rgba(0, 145, 218, 0.3)`
- Border-radius arredondados: `16px` para cards, `8px` para botões

---

## 🔐 Modos de Autenticação

| Tipo | Usuário | Método | Rota | Status |
|------|---------|--------|------|--------|
| **Admin Django** | `admin` | Banco local | `/admin/` | ✅ Pronto |
| **Fornecedor** | Externos | Banco local (`is_supplier=True`) | `/login/partner/` | ✅ Funcionando |
| **Colaborador** | Funcionários ILPEA | Active Directory (LDAP) por país | `/login/collaborator/` | ✅ FUNCIONANDO! |

### Como fazer login como Admin:

**Opção 1 - Criar superusuário:**
```bash
python manage.py createsuperuser
# Username: admin
# Email: admin@ilpea.com.br
# Password: [sua senha]
```

**Opção 2 - Usar usuário do AD:**
- Qualquer usuário que fizer login via `/login/collaborator/` automaticamente recebe `is_staff=True`
- Pode acessar `/admin/` com suas credenciais do AD

**Opção 3 - Via shell:**
```python
python manage.py shell

from accounts.models import User
admin = User.objects.create_superuser(
    username='admin_local',
    email='admin@ilpea.com.br',
    password='SenhaForte@2025',
    first_name='Administrador',
    last_name='Sistema',
    is_admin_local=True
)
```

---

## 🌐 Sistema Multilíngue (i18n)

### Implementação Completa:

**Idiomas Suportados:**
1. 🇧🇷 Português (Brasil) - `pt-br` (padrão)
2. 🇺🇸 English - `en`
3. 🇪🇸 Español - `es`
4. 🇩🇪 Deutsch - `de`
5. 🇮🇹 Italiano - `it`
6. 🇨🇳 中文 (简体) - `zh-hans`

### Como Funciona:

**Para usuários NÃO autenticados (páginas públicas):**
- Seletor de idioma discreto no topo direito (fixo)
- Idioma salvo temporariamente na sessão
- Disponível em: Home, Login Parceiro, Login Colaborador

**Para usuários autenticados:**
- Idioma salvo permanentemente no campo `User.preferred_language`
- Configurável em `/settings/` (botão "⚙️ Configurações")
- Aplicado automaticamente via `UserLanguageMiddleware`
- Persiste entre logins

**Após logout:**
- Sessão limpa completamente
- Volta ao idioma padrão (pt-br)
- Cookie de idioma removido

### Arquivos Importantes:

**Configuração (settings.py):**
```python
LANGUAGE_CODE = 'pt-br'
USE_I18N = True
LANGUAGES = [
    ('pt-br', 'Português (Brasil)'),
    ('en', 'English'),
    ('es', 'Español'),
    ('de', 'Deutsch'),
    ('it', 'Italiano'),
    ('zh-hans', '中文 (简体)'),
]
LOCALE_PATHS = [BASE_DIR / 'locale']
```

**Middleware (accounts/middleware.py):**
```python
class UserLanguageMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if not request.user.is_authenticated or request.user.is_anonymous:
            return None
        
        if hasattr(request.user, 'preferred_language') and request.user.preferred_language:
            translation.activate(request.user.preferred_language)
            request.LANGUAGE_CODE = request.user.preferred_language
```

**Modelo User (accounts/models.py):**
```python
class User(AbstractUser):
    preferred_language = models.CharField(
        max_length=10,
        default='pt-br',
        choices=LANGUAGES,
        verbose_name="Idioma Preferido"
    )
    is_supplier = models.BooleanField(default=False)
    country_code = models.CharField(max_length=5, blank=True, null=True, choices=COUNTRY_CHOICES)
    is_admin_local = models.BooleanField(default=False)
```

### Comandos para Atualizar Traduções:

```bash
# Gerar arquivos .po
python manage.py makemessages -l en
python manage.py makemessages -l es
python manage.py makemessages -l de
python manage.py makemessages -l it
python manage.py makemessages -l zh_Hans

# Compilar traduções
python manage.py compilemessages
```

---

## 🔐 Sistema de Criptografia AES-256

### Arquivo: `adminpanel/encryption.py`

**Implementação completa:**
```python
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from django.conf import settings

BLOCK_SIZE = 16

class AESCipher:
    def __init__(self):
        key = settings.CRYPTO_MASTER_KEY.encode('utf-8')
        self.key = key[:32].ljust(32, b'\0')
    
    def encrypt(self, raw):
        if not raw:
            return ""
        try:
            raw_bytes = pad(raw.encode('utf-8'), BLOCK_SIZE)
            cipher = AES.new(self.key, AES.MODE_ECB)
            encrypted = cipher.encrypt(raw_bytes)
            return base64.b64encode(encrypted).decode('utf-8')
        except Exception as e:
            print(f"❌ Erro ao criptografar: {e}")
            return ""
    
    def decrypt(self, enc):
        if not enc:
            return ""
        try:
            enc_bytes = base64.b64decode(enc)
            cipher = AES.new(self.key, AES.MODE_ECB)
            decrypted = unpad(cipher.decrypt(enc_bytes), BLOCK_SIZE)
            return decrypted.decode('utf-8')
        except Exception as e:
            print(f"⚠️ Erro ao descriptografar: {e}")
            return enc if len(enc) < 100 else ""

aes = AESCipher()

def encrypt_text(plain_text):
    return aes.encrypt(plain_text)

def decrypt_text(encrypted_text):
    result = aes.decrypt(encrypted_text)
    return result if result else ""

def test_encryption():
    """Testa se a criptografia está funcionando."""
    print("🔐 Testando criptografia AES-256 (modo ECB)...")
    print(f"🔑 Chave definida: {settings.CRYPTO_MASTER_KEY[:10]}...")
    
    test_password = "@Britswt963*"
    print(f"\n📝 Senha original: {test_password}")
    print(f"   Tamanho: {len(test_password)} caracteres")
    
    encrypted = aes.encrypt(test_password)
    print(f"\n🔒 Criptografado:")
    print(f"   {encrypted}")
    print(f"   Tamanho: {len(encrypted)} caracteres")
    
    decrypted = aes.decrypt(encrypted)
    print(f"\n🔓 Descriptografado: {decrypted}")
    print(f"   Tamanho: {len(decrypted)} caracteres")
    
    print("\n" + "="*60)
    if test_password == decrypted:
        print("✅ SUCESSO! Criptografia funcionando perfeitamente!")
        print("="*60)
        return True
    else:
        print("❌ ERRO! Senhas não coincidem!")
        print(f"   Esperado: '{test_password}'")
        print(f"   Recebido: '{decrypted}'")
        print("="*60)
        return False
```

**Teste:**
```bash
python manage.py shell
>>> from adminpanel.encryption import test_encryption
>>> test_encryption()
```

---

## 🔒 Backend de Autenticação LDAP Multi-País

### Arquivo: `accounts/backends.py`

**Características:**
- Suporte a múltiplos países (cada um com seu próprio AD)
- Busca dinâmica de configuração por `country_code`
- Criação/atualização automática de usuários Django
- Logging completo para debug
- Extração de atributos do AD (nome, email, etc)

**Configuração no settings.py:**
```python
AUTHENTICATION_BACKENDS = [
    'accounts.backends.MultiCountryLDAPBackend',  # LDAP multi-país
    'django.contrib.auth.backends.ModelBackend',  # Autenticação padrão
]

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'accounts': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
```

**Fluxo de Autenticação:**
1. Usuário seleciona país no formulário
2. Sistema busca configuração `LdapDirectory` do país
3. Tenta autenticar no AD usando credenciais fornecidas
4. Se bem-sucedido, busca atributos do usuário (nome, email)
5. Cria ou atualiza usuário no Django
6. Define `is_staff=True` automaticamente
7. Faz login no sistema

---

## 🗄️ Modelo LdapDirectory (Active Directory)

### Arquivo: `adminpanel/models.py`

**Campos principais:**
```python
class LdapDirectory(models.Model):
    # Identificação
    country_code = models.CharField(max_length=5, unique=True, choices=COUNTRY_CHOICES)
    name = models.CharField(max_length=100)
    
    # Servidor LDAP
    ldap_server = models.CharField(max_length=200)  # Ex: S28BRDC2-16.BR.ILPEAORG.COM
    port = models.IntegerField(default=389)
    base_dn = models.CharField(max_length=300)      # Ex: DC=BR,DC=ILPEAORG,DC=COM
    
    # Credenciais (criptografadas)
    bind_user_dn = models.CharField(max_length=300)
    bind_password_encrypted = models.TextField()
    
    # Busca de usuários
    user_search_base = models.CharField(max_length=300, blank=True)
    search_filter = models.CharField(max_length=200, default="(sAMAccountName={username})")
    
    # Mapeamento de atributos
    attr_first_name = models.CharField(max_length=50, default="givenName")
    attr_last_name = models.CharField(max_length=50, default="sn")
    attr_email = models.CharField(max_length=50, default="mail")
    
    # Segurança
    use_ssl = models.BooleanField(default=False)
    use_tls = models.BooleanField(default=False)
    
    # Status
    is_active = models.BooleanField(default=True)
    
    def set_password(self, raw_password):
        """Criptografa a senha antes de salvar."""
        self.bind_password_encrypted = aes.encrypt(raw_password)
    
    def get_password(self):
        """Retorna a senha descriptografada."""
        try:
            decrypted = aes.decrypt(self.bind_password_encrypted or '')
            return decrypted if decrypted else ''
        except Exception as e:
            print(f"❌ Erro ao descriptografar senha do AD: {str(e)}")
            return ''
    
    def save(self, *args, **kwargs):
        """Override para criptografar senha automaticamente."""
        if self.bind_password_encrypted:
            is_likely_encrypted = (
                '==' in self.bind_password_encrypted or 
                len(self.bind_password_encrypted) > 20
            )
            if not is_likely_encrypted:
                print(f"🔒 Criptografando senha do AD antes de salvar...")
                self.bind_password_encrypted = aes.encrypt(self.bind_password_encrypted)
                print(f"✅ Senha criptografada: {self.bind_password_encrypted[:30]}...")
        super().save(*args, **kwargs)
```

**Configuração atual do Brasil:**
```python
# Via shell ou admin
ad_br = LdapDirectory.objects.get(country_code='BR')

# Dados configurados:
# - Servidor: S28BRDC2-16.BR.ILPEAORG.COM
# - Porta: 389
# - Base DN: DC=BR,DC=ILPEAORG,DC=COM
# - Bind User: CN=Admin,CN=Users,DC=BR,DC=ILPEAORG,DC=COM
# - Senha: (criptografada com AES-256)
```

---

## ✅ Funcionalidades Implementadas

### 1️⃣ Autenticação de Fornecedor
- ✅ Formulário de login (`PartnerLoginForm`)
- ✅ View de autenticação (`partner_login`)
- ✅ Template estilizado (`partner_login.html`)
- ✅ Validação por email e flag `is_supplier=True`
- ✅ Redirecionamento para dashboard após login

### 2️⃣ Dashboard do Fornecedor
- ✅ Página principal (`supplier_dashboard`)
- ✅ Cards informativos (Contratos, Pendências, Notificações, Relatórios)
- ✅ Proteção com `@login_required`
- ✅ Verificação de permissão (`is_supplier`)
- ✅ Botões: Configurações e Sair
- ✅ Design responsivo com cores ILPEA

### 3️⃣ Autenticação de Colaborador via LDAP
- ✅ Backend LDAP multi-país (`MultiCountryLDAPBackend`)
- ✅ Formulário com seleção de país (`CollaboratorLoginForm`)
- ✅ View de autenticação (`collaborator_login`)
- ✅ Template estilizado (`collaborator_login.html`)
- ✅ Criação/atualização automática de usuários
- ✅ Extração de dados do AD (nome, email)
- ✅ Logging completo

### 4️⃣ Dashboard do Colaborador
- ✅ Página principal (`collaborator_dashboard`)
- ✅ Exibição de dados do usuário
- ✅ Cards de estatísticas (em desenvolvimento)
- ✅ Design consistente com identidade ILPEA
- ✅ Botões: Configurações e Sair

### 5️⃣ Sistema de Configurações
- ✅ Página de configurações (`/settings/`)
- ✅ Formulário de idioma preferido
- ✅ Salvamento no banco de dados
- ✅ Aplicação imediata do idioma escolhido
- ✅ Template estilizado com feedback visual

### 6️⃣ Logout Seguro
- ✅ Limpeza completa da sessão
- ✅ Remoção de cookies de idioma
- ✅ Reset para idioma padrão (pt-br)
- ✅ Headers de cache para evitar problemas
- ✅ Redirecionamento para home

### 7️⃣ Páginas de Erro
- ✅ Página 403 - Acesso Negado (`forbidden.html`)
- ✅ Redirecionamento inteligente
- ✅ Design consistente

### 8️⃣ Tela Inicial
- ✅ Seleção de perfil (Parceiro/Colaborador)
- ✅ Seletor de idioma no topo direito
- ✅ Design moderno com gradiente ILPEA

### 9️⃣ Painel Administrativo Django
- ✅ Acesso via `/admin/`
- ✅ Gerenciamento de usuários
- ✅ Configurações de LDAP
- ✅ Configurações de SMTP
- ✅ Todos os modelos registrados

---

## 🧪 Como Testar o Sistema Atual

### 1. Testar Login de Fornecedor:

**Criar usuário de teste:**
```bash
python manage.py shell
```

```python
from accounts.models import User

user = User.objects.create_user(
    username="fornecedor@teste.com",
    email="fornecedor@teste.com",
    password="teste123",
    first_name="Fornecedor",
    last_name="Teste",
    is_supplier=True,
    preferred_language='pt-br'
)
print(f"✅ Usuário criado: {user.username}")
exit()
```

**Testar:**
```
http://127.0.0.1:8000/login/partner/
Email: fornecedor@teste.com
Senha: teste123
```

### 2. Testar Login de Colaborador (LDAP):

**Acesse:**
```
http://127.0.0.1:8000/login/collaborator/
```

**Preencha:**
- País: 🇧🇷 Brasil
- Usuário: [seu usuário do AD]
- Senha: [sua senha do AD]

**Resultado esperado:**
- Autenticação no AD
- Criação/atualização do usuário no Django
- Redirecionamento para dashboard do colaborador
- Dados extraídos do AD (nome completo, email)

### 3. Testar Login como Admin:

**Opção 1 - Criar superusuário:**
```bash
python manage.py createsuperuser
```

**Opção 2 - Usar usuário do AD:**
```
http://127.0.0.1:8000/admin/
Usuário: [seu usuário que fez login via LDAP]
Senha: [sua senha do AD]
```

### 4. Testar Fluxo Completo:

| Passo | URL | Ação | Resultado Esperado |
|-------|-----|------|-------------------|
| 1 | `http://127.0.0.1:8000/` | Acessar home | Mostra "Sou Parceiro / Sou Colaborador" |
| 2 | Trocar idioma | Selecionar "English" no topo | Página muda para inglês |
| 3 | Clicar "Sou Colaborador" | Ir para login | Formulário em inglês |
| 4 | Login | País: Brasil<br>User: [AD user]<br>Senha: [AD pass] | Redireciona para dashboard |
| 5 | Dashboard | Ver conteúdo | Dados do usuário + cards |
| 6 | Configurações | Clicar "⚙️ Configurações" | Abre página de idioma |
| 7 | Trocar idioma | Selecionar "Español" e salvar | Volta ao dashboard em espanhol |
| 8 | Logout | Clicar "Sair" | Volta à home em português |

---

## 🛠️ Comandos Úteis

### Migrations:
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py showmigrations
```

### Usuários:
```bash
python manage.py createsuperuser
python manage.py shell
```

### Servidor:
```bash
python manage.py runserver
python manage.py runserver 0.0.0.0:8000  # Acesso externo
```

### Traduções:
```bash
python manage.py makemessages -l en
python manage.py compilemessages
```

### Banco de Dados:
```bash
python manage.py dbshell
python manage.py dumpdata > backup.json
python manage.py loaddata backup.json
```

### Testar Criptografia:
```bash
python manage.py shell
>>> from adminpanel.encryption import test_encryption
>>> test_encryption()
```

### Verificar Configuração LDAP:
```bash
python manage.py shell
>>> from adminpanel.models import LdapDirectory
>>> ads = LdapDirectory.objects.all()
>>> for ad in ads:
...     print(f"✅ {ad.get_country_code_display()} - {ad.name}")
...     print(f"   Servidor: {ad.get_connection_string()}")
...     print(f"   Ativo: {ad.is_active}")
```

---

## 📋 Dependências (requirements.txt)

```txt
Django==5.0.7
djangorestframework==3.14.0
psycopg2-binary==2.9.9
python-dotenv==1.0.0
pycryptodome==3.19.0
django-cors-headers==4.3.1
ldap3==2.9.1
```

**Instalar:**
```bash
pip install -r requirements.txt
```

---

## 🔐 Variáveis de Ambiente (.env)

```env
# Django
DJANGO_SECRET_KEY=sua-chave-secreta-aqui
DJANGO_DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost,supplyconnect.ilpea.com.br

# Database
DB_NAME=supplyconnect
DB_USER=admin
DB_PASSWORD=sua-senha-aqui
DB_HOST=127.0.0.1
DB_PORT=5432

# Encryption
CRYPTO_MASTER_KEY=Ilpea_SUPPLYCONNECT_2025_MASTER_KEY

# SMTP (HCL Notes)
SMTP_HOST=mail.ilpea.com.br
SMTP_PORT=587
SMTP_USER=system@ilpea.com.br
SMTP_PASSWORD=senha-smtp-aqui
SMTP_USE_TLS=True
```

---

## 🧱 Troubleshooting

### Problema: Traduções não aparecem
**Solução:**
```bash
python manage.py compilemessages
# Reiniciar o servidor
```

### Problema: Idioma não muda após logout
**Solução:** Limpar cache do navegador (Ctrl+Shift+Del) ou testar em aba anônima

### Problema: Erro 404 em rotas
**Solução:** Verificar `urls.py` e `app_name` nos arquivos de rotas

### Problema: Static files não carregam
**Solução:**
```bash
python manage.py collectstatic
```

### Problema: Erro ao conectar no banco
**Solução:** Verificar `.env` e garantir que PostgreSQL está rodando

### Problema: Erro "No module named 'accounts.backends'"
**Solução:** Verificar se o arquivo `accounts/backends.py` existe. Se não, criá-lo.

### Problema: Erro LDAP ao fazer login
**Solução:**
1. Verificar se a configuração do país está ativa no admin
2. Verificar se a senha do bind está criptografada corretamente
3. Testar conexão LDAP:
```python
python manage.py shell
>>> from adminpanel.models import LdapDirectory
>>> ad = LdapDirectory.objects.get(country_code='BR')
>>> senha = ad.get_password()
>>> print(f"Senha descriptografada: {senha}")
```

### Problema: Template não encontrado
**Solução:** Verificar se o arquivo existe no caminho correto e se `APP_DIRS = True` no settings.py

---

## 🚧 Próximos Passos (Prioridades)

### **Fase 2 - Gestão de Fornecedores:**

#### 1️⃣ **CRUD de Fornecedores** (ALTA PRIORIDADE)

**App:** `suppliers`

**Modelos a criar:**
```python
# suppliers/models.py

class Supplier(models.Model):
    """Dados principais do fornecedor."""
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    legal_name = models.CharField(max_length=200)
    tax_id = models.CharField(max_length=50)  # CNPJ/CPF/Tax ID
    country = models.CharField(max_length=5, choices=COUNTRY_CHOICES)
    
    # Endereço
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    
    # Contato
    phone = models.CharField(max_length=50)
    email = models.EmailField()
    website = models.URLField(blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    
    # Relacionamento
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Auditoria
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, related_name='suppliers_created', on_delete=models.SET_NULL, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, related_name='suppliers_updated', on_delete=models.SET_NULL, null=True)

class SupplierContact(models.Model):
    """Contatos do fornecedor."""
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='contacts')
    name = models.CharField(max_length=200)
    role = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=50)
    is_primary = models.BooleanField(default=False)

class SupplierDocument(models.Model):
    """Documentos anexados ao fornecedor."""
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='documents')
    name = models.CharField(max_length=200)
    document_type = models.CharField(max_length=50, choices=DOCUMENT_TYPES)
    file = models.FileField(upload_to='suppliers/documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

class SupplierEvaluation(models.Model):
    """Avaliações de qualidade do fornecedor."""
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='evaluations')
    evaluation_date = models.DateField()
    score = models.DecimalField(max_digits=5, decimal_places=2)
    category = models.CharField(max_length=50)
    comments = models.TextField(blank=True)
    evaluated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
```

**Views a criar:**
- `supplier_list` - Lista de fornecedores
- `supplier_detail` - Detalhes do fornecedor
- `supplier_create` - Cadastrar novo fornecedor
- `supplier_update` - Editar fornecedor
- `supplier_delete` - Deletar fornecedor
- `supplier_documents` - Gerenciar documentos
- `supplier_contacts` - Gerenciar contatos
- `supplier_evaluations` - Gerenciar avaliações

#### 2️⃣ **Melhorias no Dashboard do Colaborador**

**Adicionar:**
- Gráfico de fornecedores por país
- Lista de últimas atividades
- Estatísticas reais (total de fornecedores, contratos ativos, pendências)
- Quick actions (cadastrar fornecedor, novo contrato)
- Notificações recentes

#### 3️⃣ **Sistema de Permissões**

**Grupos a criar:**
- `Global Admin` - Acesso total
- `Country Admin` - Admin do país
- `Purchasing Manager` - Gerente de compras
- `Quality Manager` - Gerente de qualidade
- `Viewer` - Apenas leitura

**Permissões por país:**
- Colaboradores só veem dados do seu país (exceto admins globais)
- Filtros automáticos baseados em `user.country_code`

#### 4️⃣ **Gestão de Contratos**

**App:** `contracts`

**Modelos a criar:**
```python
class Contract(models.Model):
    """Contrato com fornecedor."""
    contract_number = models.CharField(max_length=50, unique=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    
    # Datas
    start_date = models.DateField()
    end_date = models.DateField()
    renewal_date = models.DateField(null=True, blank=True)
    
    # Valores
    total_value = models.DecimalField(max_digits=15, decimal_places=2)
    currency = models.CharField(max_length=3, default='BRL')
    
    # Status
    status = models.CharField(max_length=20, choices=CONTRACT_STATUS)
    
    # Documentos
    document_file = models.FileField(upload_to='contracts/')
    
    # Auditoria
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

class ContractItem(models.Model):
    """Itens/produtos do contrato."""
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name='items')
    product_code = models.CharField(max_length=50)
    description = models.TextField()
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=15, decimal_places=2)

class ContractAmendment(models.Model):
    """Aditivos de contrato."""
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name='amendments')
    amendment_number = models.CharField(max_length=50)
    description = models.TextField()
    effective_date = models.DateField()
    document_file = models.FileField(upload_to='contracts/amendments/')
```

#### 5️⃣ **Sistema de Notificações**

**App:** `notifications`

**Funcionalidades:**
- Notificações em tempo real (WebSocket ou polling)
- Email automático via SMTP configurado
- Centro de notificações no dashboard
- Marcação de lido/não lido
- Tipos: Pendências, Vencimentos, Aprovações, Alertas

**Modelo:**
```python
class Notification(models.Model):
    """Notificação para usuário."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)
    
    # Relacionamentos
    related_object_type = models.CharField(max_length=50, blank=True)
    related_object_id = models.IntegerField(blank=True, null=True)
    
    # Status
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    
    # Auditoria
    created_at = models.DateTimeField(auto_now_add=True)
```

#### 6️⃣ **Relatórios e Analytics**

**App:** `reports`

**Dashboards:**
- Performance de fornecedores (por país, categoria, período)
- Status de contratos (ativos, vencendo, vencidos)
- Qualidade por período (gráficos de tendência)
- Análise de custos
- Exportação para Excel/PDF

**Bibliotecas sugeridas:**
- `django-import-export` - Exportação de dados
- `reportlab` - Geração de PDFs
- `openpyxl` - Manipulação de Excel
- `chart.js` ou `plotly` - Gráficos interativos

#### 7️⃣ **Sistema de Qualidade**

**App:** `quality`

**Modelos:**
```python
class NonConformity(models.Model):
    """Registro de não conformidade."""
    nc_number = models.CharField(max_length=50, unique=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    description = models.TextField()
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    status = models.CharField(max_length=20, choices=NC_STATUS)
    
    # Datas
    detected_date = models.DateField()
    response_deadline = models.DateField()
    closed_date = models.DateField(null=True, blank=True)
    
    # Responsáveis
    reported_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    assigned_to = models.ForeignKey(User, related_name='assigned_ncs', on_delete=models.SET_NULL, null=True)

class ActionPlan(models.Model):
    """Plano de ação para não conformidade."""
    non_conformity = models.ForeignKey(NonConformity, on_delete=models.CASCADE, related_name='action_plans')
    action_description = models.TextField()
    responsible = models.CharField(max_length=200)
    deadline = models.DateField()
    status = models.CharField(max_length=20, choices=ACTION_STATUS)
    completion_date = models.DateField(null=True, blank=True)
    evidence = models.FileField(upload_to='quality/evidences/', null=True, blank=True)
```

---

## 📊 Status do Projeto

### Completo (100%):
- ✅ Estrutura base do Django
- ✅ Modelo User customizado
- ✅ Sistema multilíngue (i18n) - 6 idiomas
- ✅ Autenticação de fornecedores (banco local)
- ✅ Autenticação de colaboradores (LDAP multi-país)
- ✅ Backend LDAP customizado
- ✅ Sistema de criptografia AES-256
- ✅ Dashboard de fornecedores
- ✅ Dashboard de colaboradores
- ✅ Sistema de configurações de usuário
- ✅ Logout seguro
- ✅ Design com identidade visual ILPEA
- ✅ Logging implementado
- ✅ Painel administrativo Django

### Em Desenvolvimento (0%):
- 🚧 CRUD de fornecedores
- 🚧 Dashboard colaborador (melhorias)
- 🚧 Gestão de contratos
- 🚧 Sistema de notificações
- 🚧 Relatórios e analytics
- 🚧 Sistema de qualidade
- 🚧 Sistema de permissões por país

### Planejado (0%):
- 📋 Planos de ação
- 📋 Reclamações
- 📋 Comunicações
- 📋 API REST completa
- 📋 Testes automatizados
- 📋 Deploy em produção
- 📋 Integração com ERP
- 📋 Sistema de aprovação (workflow)

---

## 🎯 Prompt para Retomar o Desenvolvimento

```
Continuar o desenvolvimento do Ilpea SupplyConnect (D:\Projeto\SupplyConnect).

SITUAÇÃO ATUAL:
✅ Sistema multilíngue completo (6 idiomas) funcionando
✅ Login de fornecedor implementado e testado
✅ Login de colaborador com Active Directory FUNCIONANDO!
✅ Backend LDAP multi-país implementado
✅ Sistema de criptografia AES-256 das senhas do AD
✅ Dashboards básicos para fornecedor e colaborador
✅ Sistema de configurações de idioma por usuário
✅ Logout seguro com limpeza de sessão
✅ Templates responsivos com identidade visual ILPEA
✅ Painel administrativo Django configurado
✅ Logging implementado

PRÓXIMO PASSO:
[Descreva o que deseja implementar - ex: CRUD de fornecedores, melhorias no dashboard, etc]

Seguir sempre o estilo didático passo a passo, indicando caminho completo dos arquivos.
```

---

## 🔒 Configuração de Segurança para Produção

### 1. SSL/HTTPS:
```python
# settings.py (produção)
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
```

### 2. URL do Admin Customizada:
```env
# .env
ADMIN_URL=painel-secreto-2025/
```

```python
# urls.py
from django.conf import settings
admin_url = getattr(settings, 'ADMIN_URL', 'admin/')
urlpatterns = [
    path(admin_url, admin.site.urls),
]
```

### 3. ALLOWED_HOSTS:
```python
# settings.py (produção)
ALLOWED_HOSTS = [
    'supplyconnect.ilpea.com.br',
    'www.supplyconnect.ilpea.com.br',
]
```

### 4. DEBUG:
```python
# settings.py (produção)
DEBUG = False
```

### 5. Secret Key:
```bash
# Gerar nova chave para produção
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

## 📝 Notas Importantes

### Sobre o Active Directory:
- ✅ Sistema testado e funcionando com AD do Brasil
- ✅ Configuração: `S28BRDC2-16.BR.ILPEAORG.COM:389`
- ✅ Senha do bind criptografada com AES-256
- ✅ Autenticação testada com sucesso (usuário: layon)
- ✅ Dados extraídos do AD: nome completo, email
- ⚠️ Outros países (AR, MX, DE, IT, CN, US) precisam configurar seus próprios ADs

### Sobre Traduções:
- ✅ Arquivos .po criados para todos os 6 idiomas
- ✅ Arquivos .mo compilados
- ⚠️ Algumas strings podem precisar de revisão por nativos
- ⚠️ Novos textos precisam ser traduzidos manualmente nos .po

### Sobre Criptografia:
- ✅ Modo ECB escolhido para compatibilidade
- ✅ Chave AES-256 configurada
- ✅ Funções de teste implementadas
- ⚠️ Para produção, considerar migrar para modo CBC ou GCM

### Sobre o Banco de Dados:
- ✅ PostgreSQL configurado
- ✅ Usuário: admin
- ✅ Banco: supplyconnect
- ⚠️ Fazer backups regulares em produção

---

## 🏆 Meta Final

Um sistema completo e robusto que permita:

1. **Fornecedores** acessarem informações de contratos, pendências e comunicações
2. **Colaboradores** gerenciarem fornecedores, contratos e processos de qualidade
3. **Administradores** configurarem o sistema e gerenciarem acessos
4. **Multi-idioma** para operação global (6 idiomas)
5. **Segurança** robusta com criptografia e autenticação corporativa (LDAP)
6. **Multi-país** com configurações independentes por país
7. **Escalável** e **manutenível** para crescimento futuro
8. **Auditoria** completa de todas as operações
9. **Notificações** automáticas para eventos importantes
10. **Relatórios** gerenciais para tomada de decisão

---

## 📞 Informações de Contato (Contexto)

**Empresa:** ILPEA  
**Projeto:** SupplyConnect  
**Ambiente de Desenvolvimento:** Windows 10/11  
**IDE:** Visual Studio Code  
**Python:** 3.13.2  
**Django:** 5.0.7  
**Banco:** PostgreSQL 16  

---

## 🎓 Recursos de Aprendizado

### Documentação Oficial:
- Django: https://docs.djangoproject.com/
- Django REST Framework: https://www.django-rest-framework.org/
- ldap3: https://ldap3.readthedocs.io/
- PyCryptodome: https://pycryptodome.readthedocs.io/

### Comandos Django Essenciais:
```bash
# Criar app
python manage.py startapp nome_do_app

# Migrations
python manage.py makemigrations
python manage.py migrate
python manage.py showmigrations

# Usuários
python manage.py createsuperuser
python manage.py changepassword username

# Shell
python manage.py shell
python manage.py shell_plus  # Requer django-extensions

# Servidor
python manage.py runserver
python manage.py runserver 0.0.0.0:8000

# Static files
python manage.py collectstatic

# Testes
python manage.py test
python manage.py test app_name

# Banco de dados
python manage.py dbshell
python manage.py dumpdata > backup.json
python manage.py loaddata backup.json

# Traduções
python manage.py makemessages -l en
python manage.py makemessages -a  # Todas as línguas
python manage.py compilemessages
```

---

## ✅ Checklist de Implementação Completa

### Autenticação e Usuários:
- [x] Modelo User customizado
- [x] Login de fornecedor (banco local)
- [x] Login de colaborador (LDAP)
- [x] Backend LDAP multi-país
- [x] Logout seguro
- [x] Sistema de permissões básico
- [ ] Grupos e permissões avançadas
- [ ] Recuperação de senha
- [ ] Primeiro acesso (change password)

### Interface:
- [x] Tela inicial (home choice)
- [x] Templates de login (parceiro e colaborador)
- [x] Dashboard do fornecedor
- [x] Dashboard do colaborador
- [x] Página de configurações
- [ ] Dashboard do administrador
- [ ] Página 404 customizada
- [ ] Página 500 customizada

### Internacionalização:
- [x] Sistema i18n configurado
- [x] 6 idiomas implementados
- [x] Middleware de idioma por usuário
- [x] Seletor de idioma em páginas públicas
- [x] Preferência de idioma salva no banco
- [ ] Revisão de traduções por nativos

### Segurança:
- [x] Criptografia AES-256
- [x] Senhas do AD criptografadas
- [x] CSRF protection
- [x] Logging implementado
- [ ] Rate limiting
- [ ] Two-factor authentication (2FA)
- [ ] Auditoria de acessos

### Fornecedores:
- [ ] CRUD de fornecedores
- [ ] Documentos anexados
- [ ] Contatos
- [ ] Histórico de avaliações
- [ ] Filtros e buscas
- [ ] Exportação de dados

### Contratos:
- [ ] CRUD de contratos
- [ ] Itens do contrato
- [ ] Aditivos
- [ ] Upload de documentos
- [ ] Versionamento
- [ ] Alertas de vencimento

### Qualidade:
- [ ] Não conformidades
- [ ] Planos de ação
- [ ] Follow-up automático
- [ ] Relatórios de qualidade
- [ ] Indicadores (KPIs)

### Notificações:
- [ ] Sistema de notificações in-app
- [ ] Email automático (SMTP)
- [ ] Centro de notificações
- [ ] Preferências de notificação
- [ ] Templates de email

### Relatórios:
- [ ] Dashboard com estatísticas
- [ ] Gráficos interativos
- [ ] Exportação para Excel
- [ ] Exportação para PDF
- [ ] Relatórios agendados

### Deploy:
- [ ] Configuração de produção
- [ ] SSL/HTTPS
- [ ] Backup automático
- [ ] Monitoramento
- [ ] CI/CD

---

**FIM DO DOCUMENTO DE CONTEXTO**

*Última atualização: 29/10/2025*  
*Versão: 3.0*  
*Status: Sistema de autenticação COMPLETO e FUNCIONANDO!*