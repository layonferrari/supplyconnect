"""
Script para limpar cache Python
"""
import os
import shutil
from pathlib import Path

base_dir = Path(__file__).parent

# Limpar __pycache__
pycache_dirs = list(base_dir.rglob('__pycache__'))
print(f"Encontrados {len(pycache_dirs)} diretórios __pycache__")

for pycache_dir in pycache_dirs:
    try:
        shutil.rmtree(pycache_dir)
        print(f"✅ Removido: {pycache_dir}")
    except Exception as e:
        print(f"❌ Erro ao remover {pycache_dir}: {e}")

# Limpar arquivos .pyc
pyc_files = list(base_dir.rglob('*.pyc'))
print(f"\nEncontrados {len(pyc_files)} arquivos .pyc")

for pyc_file in pyc_files:
    try:
        pyc_file.unlink()
        print(f"✅ Removido: {pyc_file}")
    except Exception as e:
        print(f"❌ Erro ao remover {pyc_file}: {e}")

print("\n✅ Limpeza de cache concluída!")
