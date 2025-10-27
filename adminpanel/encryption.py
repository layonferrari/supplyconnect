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
        raw_bytes = pad(raw.encode('utf-8'), BLOCK_SIZE)
        cipher = AES.new(self.key, AES.MODE_ECB)
        encrypted = cipher.encrypt(raw_bytes)
        return base64.b64encode(encrypted).decode('utf-8')

    def decrypt(self, enc):
        try:
            enc_bytes = base64.b64decode(enc)
            cipher = AES.new(self.key, AES.MODE_ECB)
            decrypted = unpad(cipher.decrypt(enc_bytes), BLOCK_SIZE)
            return decrypted.decode('utf-8')
        except Exception:
            return None
