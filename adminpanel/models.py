from django.db import models

# Create your models here.
from django.db import models
from adminpanel.encryption import AESCipher

aes = AESCipher()

class LdapConfig(models.Model):
    host = models.CharField(max_length=255)
    base_dn = models.CharField(max_length=255)
    bind_user = models.CharField(max_length=255)
    bind_password_encrypted = models.TextField()
    group_search = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def set_password(self, password):
        self.bind_password_encrypted = aes.encrypt(password)

    def get_password(self):
        return aes.decrypt(self.bind_password_encrypted or '')

    def __str__(self):
        return f"LDAP Config ({self.host})"


class SmtpConfig(models.Model):
    host = models.CharField(max_length=255)
    port = models.IntegerField(default=465)
    username = models.CharField(max_length=255)
    password_encrypted = models.TextField()
    use_ssl = models.BooleanField(default=True)
    use_tls = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def set_password(self, password):
        self.password_encrypted = aes.encrypt(password)

    def get_password(self):
        return aes.decrypt(self.password_encrypted or '')

    def __str__(self):
        return f"SMTP Config ({self.host})"


class SslConfig(models.Model):
    cert_file = models.FileField(upload_to='ssl_certs/')
    key_file = models.FileField(upload_to='ssl_keys/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"SSL Cert ({self.cert_file.name})"
