# 📘 Ilpea SupplyConnect – Contexto Técnico Atualizado (27/10/2025)

## 🌍 Visão Geral
O **Ilpea SupplyConnect** é o sistema global da ILPEA para controle e comunicação segura com fornecedores.  
Tem como objetivo centralizar contratos, planos de ação, reclamações e comunicações entre fornecedores e filiais da ILPEA no mundo.

---

## ⚙️ Arquitetura Técnica

| Componente | Tecnologia / Detalhe |
|-------------|----------------------|
| **Backend** | Django + Django REST Framework |
| **Banco de Dados** | PostgreSQL (com extensão `pgvector`) |
| **Mensageria / Tarefas** | Redis + Celery *(planejado)* |
| **Autenticação** | Active Directory (LDAP) + Usuário Local (`admin_local`) |
| **Criptografia** | AES (PyCryptodome) com chave `CRYPTO_MASTER_KEY` |
| **SMTP** | Servidor HCL Notes da IBM |
| **SSL** | Certificado wildcard `*.ilpea.com.br` |
| **Infraestrutura** | Firewall FortiGate 90G / Domínio global `supplyconnect.ilpea.com.br` |

---

## 🧩 Estrutura do Projeto Django

**Caminho:** `D:\Projeto\SupplyConnect\`

| Pasta | Descrição |
|-------|------------|
| `accounts/` | App customizado para usuários (`User` com `is_admin_local`) |
| `core/` | Estruturas centrais (`CompanyUnit`, timestamps, configs globais) |
| `adminpanel/` | Painel de configuração (LDAP, SMTP, SSL) — ✅ Criado |
| `contracts/` | (Futuro) Gestão de contratos e auditoria |
| `suppliers/` | (Futuro) Cadastro e gestão de fornecedores |
| `quality/` | (Futuro) Reclamações, 8D, planos de ação |
| `notifications/` | (Futuro) E-mails e alertas automáticos |
| `reports/` | (Futuro) Relatórios e exportações PDF/BI |
| `templates/` | Template base global (`base.html`) para herança |
| `.env` | Configurações seguras (PostgreSQL, SMTP, LDAP, SSL etc.) |

---

## 🧱 Banco de Dados
- **Database:** `supplyconnect`  
- **Usuário:** `admin`  
- **Extensão:** `pgvector`  
- **Charset:** `UTF8`  
- **Conexão:** validada e operacional  

---

## 👤 Usuário e Autenticação
- Modelo customizado: `accounts.User` herdando de `AbstractUser`
- Campos adicionais:
  - `is_admin_local` (autenticação local)
  - `company_unit` (ligação com `core.CompanyUnit`)
- Superusuário local criado:
  - **username:** `admin_local`
  - **email:** `admin@ilpea.com.br`
- Filial inicial: **Ilpea Brasil (BR)**

---

## 🔒 Segurança e Configuração
- `.env` contém:
  - `DJANGO_SECRET_KEY`, `CRYPTO_MASTER_KEY`
  - Credenciais de PostgreSQL, SMTP e placeholders LDAP
- `CRYPTO_MASTER_KEY` carregado via `os.getenv()` em `settings.py`
- Conexão com PostgreSQL testada e migrações aplicadas
- Certificados SSL e scripts AES funcionando corretamente

---

## 🧮 App `adminpanel` (criado e funcional)

### 🧱 Estrutura
- Modelos: `LdapConfig`, `SmtpConfig`, `SslConfig`
- Criptografia AES integrada via `encryption.py`
- Formulários e views configurados
- Templates:
  - `index.html` (menu principal)
  - `ldap_config.html`
  - `smtp_config.html`
  - `ssl_config.html`

### 🔧 Ajustes aplicados
- Decoradores de login (`@login_required`) **comentados** para testes livres
- Erro 404 resolvido (redirecionamento removido)
- Template base ausente corrigido (`base.html` criado)
- Painel acessível diretamente em:



---

## ✅ Status Atual

| Item | Situação |
|------|-----------|
| Estrutura Django criada | ✅ |
| Banco PostgreSQL configurado | ✅ |
| pgvector instalado | ✅ |
| Apps principais (`core`, `accounts`, `adminpanel`) | ✅ |
| Painel `/admin/` acessível | ✅ |
| `adminpanel` funcional (sem login) | ✅ |
| Template base global criado (`base.html`) | ✅ |
| Autenticação AD + Local | 🚧 Em desenvolvimento |
| IA local (pgvector / embeddings) | 🚧 Em desenvolvimento |
| Painel SupplyConnect (frontend visual completo) | 🚧 Em desenvolvimento |

---

## 🧭 Próximos Passos

| Etapa | Módulo | Objetivo |
|-------|---------|----------|
| 1️⃣ | **Tela de login customizada (accounts)** | Permitir login local e futuro via AD |
| 2️⃣ | **Função “Testar Conexão” no AdminPanel** | Validar LDAP e SMTP diretamente no painel |
| 3️⃣ | **Painel visual SupplyConnect** | Interface para fornecedores e contratos |
| 4️⃣ | **Integração IA (pgvector)** | Busca semântica e inteligência offline |
| 5️⃣ | **CompanyUnits e Permissões AD** | Vincular usuários a filiais e grupos AD |
| 6️⃣ | **Deploy seguro** | Preparar ambiente de produção (Fortinet + SSL) |

---

## 💡 Prompt de Continuidade

> Estou continuando o desenvolvimento do sistema **Ilpea SupplyConnect**, criado anteriormente.  
> O projeto está localizado em `D:\Projeto\SupplyConnect`, rodando em Django + PostgreSQL com `pgvector`.  
> O app `adminpanel` já está criado e funcional (LDAP, SMTP, SSL com AES).  
> O painel pode ser acessado sem login e o arquivo `base.html` foi criado.  
> O próximo passo é implementar a tela de **login customizada (accounts)** e a função **“Testar Conexão”** no AdminPanel.  
>  
> Use sempre o mesmo contexto técnico, estrutura e segurança definidos aqui.
