"""
Módulo de criptografia AES para dados sensíveis.
Mantém compatibilidade com o sistema existente (modo ECB).
"""

import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from django.conf import settings

BLOCK_SIZE = 16


class AESCipher:
    """
    Classe para criptografia/descriptografia AES-256.
    Usa modo ECB para compatibilidade com sistema legado.
    """
    
    def __init__(self):
        """Inicializa o cipher com a chave do settings."""
        key = settings.CRYPTO_MASTER_KEY.encode('utf-8')
        self.key = key[:32].ljust(32, b'\0')
    
    def encrypt(self, raw):
        """
        Criptografa um texto usando AES-256 em modo ECB.
        
        Args:
            raw (str): Texto em claro
        
        Returns:
            str: Texto criptografado em base64
        """
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
        """
        Descriptografa um texto criptografado.
        
        Args:
            enc (str): Texto criptografado em base64
        
        Returns:
            str: Texto descriptografado ou string vazia se houver erro
        """
        if not enc:
            return ""
        
        try:
            enc_bytes = base64.b64decode(enc)
            cipher = AES.new(self.key, AES.MODE_ECB)
            decrypted = unpad(cipher.decrypt(enc_bytes), BLOCK_SIZE)
            return decrypted.decode('utf-8')
        except Exception as e:
            # Retorna string vazia ao invés de None
            print(f"⚠️ Erro ao descriptografar: {e}")
            # Se o texto não está criptografado, retorna ele mesmo
            return enc if len(enc) < 100 else ""


# Instância global para uso em modelos legados
aes = AESCipher()


# Funções standalone para novo sistema
def encrypt_text(plain_text):
    """Criptografa texto usando a instância global."""
    return aes.encrypt(plain_text)


def decrypt_text(encrypted_text):
    """Descriptografa texto usando a instância global."""
    result = aes.decrypt(encrypted_text)
    return result if result else ""


def test_encryption():
    """
    Testa se a criptografia está funcionando.
    
    Usage:
        python manage.py shell
        >>> from adminpanel.encryption import test_encryption
        >>> test_encryption()
    """
    print("🔐 Testando criptografia AES-256 (modo ECB)...")
    print(f"🔑 Chave definida: {settings.CRYPTO_MASTER_KEY[:10]}...")
    
    test_password = "@Britswt963*"
    print(f"\n📝 Senha original: {test_password}")
    print(f"   Tamanho: {len(test_password)} caracteres")
    
    # Criptografa
    encrypted = aes.encrypt(test_password)
    print(f"\n🔒 Criptografado:")
    print(f"   {encrypted}")
    print(f"   Tamanho: {len(encrypted)} caracteres")
    
    # Descriptografa
    decrypted = aes.decrypt(encrypted)
    print(f"\n🔓 Descriptografado: {decrypted}")
    print(f"   Tamanho: {len(decrypted)} caracteres")
    
    # Verifica
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