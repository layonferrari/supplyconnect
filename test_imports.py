"""
Script para testar importações e identificar problemas.
"""
import os
import sys
import django

# Configurar Django
sys.path.insert(0, r'D:\Projeto\SupplyConnect')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'supplyconnect.settings')
django.setup()

print("✅ Django configurado com sucesso!")

# Testar importações
try:
    print("\n📦 Testando importação de adminpanel.models...")
    from adminpanel import models as adminpanel_models
    print(f"✅ adminpanel.models importado: {dir(adminpanel_models)[:5]}")
except Exception as e:
    print(f"❌ Erro ao importar adminpanel.models: {e}")

try:
    print("\n📦 Testando importação de adminpanel.forms...")
    from adminpanel import forms as adminpanel_forms
    print(f"✅ adminpanel.forms importado")
    print(f"   Forms disponíveis: {[x for x in dir(adminpanel_forms) if 'Form' in x]}")
except Exception as e:
    print(f"❌ Erro ao importar adminpanel.forms: {e}")

try:
    print("\n📦 Testando importação de adminpanel.views...")
    from adminpanel import views as adminpanel_views
    print(f"✅ adminpanel.views importado")
except Exception as e:
    print(f"❌ Erro ao importar adminpanel.views: {e}")

try:
    print("\n📦 Testando importação de access_control.models...")
    from access_control import models as access_models
    print(f"✅ access_control.models importado")
    print(f"   Modelos: AdminProfile={hasattr(access_models, 'AdminProfile')}, CountryPermission={hasattr(access_models, 'CountryPermission')}")
except Exception as e:
    print(f"❌ Erro ao importar access_control.models: {e}")

try:
    print("\n📦 Testando importação de access_control.views...")
    from access_control import views as access_views
    print(f"✅ access_control.views importado")
except Exception as e:
    print(f"❌ Erro ao importar access_control.views: {e}")

print("\n✅ Todos os testes de importação concluídos!")
