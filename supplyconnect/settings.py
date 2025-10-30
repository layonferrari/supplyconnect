import os
from pathlib import Path
from dotenv import load_dotenv

# === Carrega variáveis de ambiente ===
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

# === Segurança ===
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "unsafe-dev-key")
DEBUG = os.getenv("DJANGO_DEBUG", "False").lower() == "true"
ALLOWED_HOSTS = [h.strip() for h in os.getenv("ALLOWED_HOSTS", "127.0.0.1,localhost").split(",") if h.strip()]
CRYPTO_MASTER_KEY = os.getenv("CRYPTO_MASTER_KEY")

# === Aplicativos instalados ===
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # --- Apps externos ---
    "rest_framework",
    "corsheaders",
    # --- Apps internos ---
    "core",
    "accounts",       # App customizado de usuários
    "suppliers",
    "contracts",
    "quality",
    "notifications",
    "reports",
    "adminpanel",
    "access_control",
]

# === Middleware ===
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.locale.LocaleMiddleware",  # Middleware de idioma
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "accounts.middleware.UserLanguageMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# === URLs principais ===
ROOT_URLCONF = "supplyconnect.urls"

# === Templates ===
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # Pasta global para templates do sistema
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.i18n",  # Contexto de idioma
            ],
        },
    },
]

# === WSGI/ASGI ===
WSGI_APPLICATION = "supplyconnect.wsgi.application"
ASGI_APPLICATION = "supplyconnect.asgi.application"

# === Banco de Dados (PostgreSQL) ===
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME", "supplyconnect"),
        "USER": os.getenv("DB_USER", "admin"),
        "PASSWORD": os.getenv("DB_PASSWORD", ""),
        "HOST": os.getenv("DB_HOST", "127.0.0.1"),
        "PORT": os.getenv("DB_PORT", "5432"),
    }
}

# === Autenticação ===
AUTH_USER_MODEL = "accounts.User"

# URLs de autenticação (CORRIGIDO)
LOGIN_URL = "accounts:home_choice"  # ✅ Redireciona para home quando não autenticado
LOGIN_REDIRECT_URL = "accounts:home_choice"  # ✅ Após login bem-sucedido
LOGOUT_REDIRECT_URL = "accounts:home_choice"  # ✅ Após logout

# Backend de autenticação customizado
AUTHENTICATION_BACKENDS = [
    'accounts.backends.MultiCountryLDAPBackend',  # LDAP multi-país
    'django.contrib.auth.backends.ModelBackend',  # Autenticação padrão (admin, fornecedores)
]

# === Internacionalização ===
LANGUAGE_CODE = "pt-br"  # Idioma padrão
TIME_ZONE = "America/Sao_Paulo"  # Fuso horário do Brasil
USE_I18N = True  # Habilita internacionalização
USE_L10N = True  # Habilita localização de formatos (datas, números)
USE_TZ = True  # Habilita suporte a fusos horários

# Idiomas disponíveis no sistema
LANGUAGES = [
    ('pt-br', 'Português (Brasil)'),
    ('en', 'English'),
    ('es', 'Español'),
    ('de', 'Deutsch'),
    ('it', 'Italiano'),
    ('zh-hans', '中文 (简体)'),
]

# Diretórios onde o Django procurará arquivos de tradução
LOCALE_PATHS = [
    BASE_DIR / 'locale',
]

# === Arquivos estáticos e mídia ===
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]  # adiciona suporte a pasta local "static"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# === Configuração CORS (caso use AJAX / API) ===
CORS_ALLOW_ALL_ORIGINS = True  # pode ser refinado depois

# === REST Framework ===
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}

# === Outras configurações ===
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Configuração de logging
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