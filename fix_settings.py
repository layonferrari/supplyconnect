"""
Script para corrigir a função user_settings
"""

# Ler o arquivo
with open('accounts/views.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Encontrar a linha da função
start_line = None
for i, line in enumerate(lines):
    if 'def user_settings(request):' in line:
        start_line = i
        break

if start_line is None:
    print("❌ Função não encontrada!")
    exit(1)

print(f"✅ Função encontrada na linha {start_line + 1}")

# Substituir a linha 190 que tem o redirect errado
for i, line in enumerate(lines):
    if i >= start_line and "return redirect('accounts:supplier_dashboard')" in line:
        print(f"✅ Encontrei a linha problemática: {i + 1}")
        
        # Pegar a indentação
        indent = len(line) - len(line.lstrip())
        
        # Substituir por código correto
        lines[i] = ' ' * indent + '# Redirecionar para o dashboard correto baseado no tipo de usuário\n'
        lines.insert(i + 1, ' ' * indent + 'if request.user.is_supplier:\n')
        lines.insert(i + 2, ' ' * (indent + 4) + "return redirect('accounts:supplier_dashboard')\n")
        lines.insert(i + 3, ' ' * indent + 'else:\n')
        lines.insert(i + 4, ' ' * (indent + 4) + "return redirect('accounts:collaborator_dashboard')\n")
        
        print("✅ Código corrigido!")
        break

# Salvar
with open('accounts/views.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("\n✅ Arquivo salvo!")
print("\n📋 Agora a função redireciona corretamente:")
print("   • Fornecedores → supplier_dashboard")
print("   • Colaboradores → collaborator_dashboard")