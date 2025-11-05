"""
Script para verificar quais views existem no access_control/views.py
"""
import re

views_file = r"D:\Projeto\SupplyConnect\access_control\views.py"
urls_file = r"D:\Projeto\SupplyConnect\access_control\urls.py"

print("=" * 60)
print("VERIFICAÇÃO DE VIEWS")
print("=" * 60)

# Ler views.py e extrair todas as funções
with open(views_file, 'r', encoding='utf-8') as f:
    views_content = f.read()
    views_defined = re.findall(r'^def (\w+)\(', views_content, re.MULTILINE)

print(f"\n✅ VIEWS DEFINIDAS ({len(views_defined)}):")
for view in sorted(views_defined):
    print(f"   - {view}")

# Ler urls.py e extrair todas as views referenciadas
with open(urls_file, 'r', encoding='utf-8') as f:
    urls_content = f.read()
    views_referenced = re.findall(r'views\.(\w+)', urls_content)
    views_referenced = list(set(views_referenced))  # Remove duplicatas

print(f"\n📋 VIEWS REFERENCIADAS NAS URLs ({len(views_referenced)}):")
for view in sorted(views_referenced):
    print(f"   - {view}")

# Verificar quais views estão faltando
missing_views = [v for v in views_referenced if v not in views_defined]

if missing_views:
    print(f"\n❌ VIEWS FALTANDO ({len(missing_views)}):")
    for view in sorted(missing_views):
        print(f"   - {view}")
else:
    print("\n✅ Todas as views referenciadas existem!")

print("\n" + "=" * 60)
