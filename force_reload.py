"""
Script para limpar completamente o cache e verificar funções
"""
import os
import sys
import shutil
from pathlib import Path

# Mudar para o diretório do projeto
os.chdir(r'D:\Projeto\SupplyConnect')

# 1. Limpar todos os __pycache__
print("=" * 60)
print("LIMPANDO CACHE DO PYTHON")
print("=" * 60)

base_dir = Path('.')
pycache_count = 0
pyc_count = 0

for pycache_dir in base_dir.rglob('__pycache__'):
    try:
        shutil.rmtree(pycache_dir)
        pycache_count += 1
        print(f"✅ Removido: {pycache_dir}")
    except Exception as e:
        print(f"❌ Erro: {e}")

for pyc_file in base_dir.rglob('*.pyc'):
    try:
        pyc_file.unlink()
        pyc_count += 1
    except Exception as e:
        print(f"❌ Erro ao remover {pyc_file}: {e}")

print(f"\n✅ Removidos: {pycache_count} diretórios __pycache__ e {pyc_count} arquivos .pyc")

# 2. Verificar se as funções existem no arquivo
print("\n" + "=" * 60)
print("VERIFICANDO FUNÇÕES NO ARQUIVO")
print("=" * 60)

views_file = Path('access_control/views.py')
if views_file.exists():
    content = views_file.read_text(encoding='utf-8')
    
    funcs_to_check = [
        'country_toggle_group_permission',
        'country_toggle_user_permission',
        'country_ad_sync_users'
    ]
    
    for func in funcs_to_check:
        if f'def {func}(' in content:
            print(f"✅ Função '{func}' ENCONTRADA no arquivo")
        else:
            print(f"❌ Função '{func}' NÃO ENCONTRADA no arquivo")
else:
    print("❌ Arquivo views.py não encontrado!")

# 3. Tentar importar o módulo
print("\n" + "=" * 60)
print("TENTANDO IMPORTAR MÓDULO (forçando recarga)")
print("=" * 60)

# Remover módulos já importados do cache
modules_to_remove = [k for k in sys.modules.keys() if 'access_control' in k]
for mod in modules_to_remove:
    del sys.modules[mod]
    print(f"🗑️  Removido do cache: {mod}")

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'supplyconnect.settings')
import django
django.setup()

# Importar views
try:
    from access_control import views
    print("✅ Módulo access_control.views importado com sucesso!")
    
    # Verificar atributos
    print("\n" + "=" * 60)
    print("VERIFICANDO ATRIBUTOS DO MÓDULO")
    print("=" * 60)
    
    for func in funcs_to_check:
        has_attr = hasattr(views, func)
        print(f"{'✅' if has_attr else '❌'} views.{func}: {has_attr}")
    
    if all(hasattr(views, f) for f in funcs_to_check):
        print("\n🎉 TODAS AS FUNÇÕES ESTÃO DISPONÍVEIS!")
    else:
        print("\n❌ ALGUMAS FUNÇÕES AINDA ESTÃO FALTANDO!")
        print("\n📋 Funções disponíveis no módulo:")
        all_funcs = [attr for attr in dir(views) if not attr.startswith('_') and callable(getattr(views, attr))]
        for func in sorted(all_funcs):
            print(f"   - {func}")
        
except Exception as e:
    print(f"❌ Erro ao importar: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
