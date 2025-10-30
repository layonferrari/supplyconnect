"""
Comando Django para criar o primeiro Admin Global do sistema.
Uso: python manage.py create_global_admin
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from accounts.models import User
from access_control.models import AdminProfile


class Command(BaseCommand):
    help = 'Cria o primeiro Admin Global do sistema SupplyConnect'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            help='Username do admin (padrão: admin.global)',
        )
        parser.add_argument(
            '--email',
            type=str,
            help='Email do admin (padrão: admin.global@ilpea.com.br)',
        )
        parser.add_argument(
            '--password',
            type=str,
            help='Senha do admin (padrão: Admin@Global2025)',
        )
        parser.add_argument(
            '--first-name',
            type=str,
            help='Primeiro nome (padrão: Administrador)',
        )
        parser.add_argument(
            '--last-name',
            type=str,
            help='Sobrenome (padrão: Global)',
        )

    def handle(self, *args, **options):
        # Valores padrão
        username = options.get('username') or 'admin.global'
        email = options.get('email') or 'admin.global@ilpea.com.br'
        password = options.get('password') or 'Admin@Global2025'
        first_name = options.get('first_name') or 'Administrador'
        last_name = options.get('last_name') or 'Global'

        self.stdout.write("\n" + "="*70)
        self.stdout.write(self.style.SUCCESS("🌍 CRIAÇÃO DO ADMINISTRADOR GLOBAL"))
        self.stdout.write("="*70 + "\n")

        # Verificar se já existe um admin global
        existing_global = AdminProfile.objects.filter(
            access_level='global_admin'
        ).first()

        if existing_global:
            self.stdout.write(
                self.style.WARNING(
                    f"⚠️  Já existe um Admin Global: {existing_global.user.username}"
                )
            )
            self.stdout.write(
                self.style.WARNING(
                    f"   Nome: {existing_global.user.get_full_name()}"
                )
            )
            self.stdout.write(
                self.style.WARNING(
                    f"   Email: {existing_global.user.email}"
                )
            )
            
            response = input("\n❓ Deseja criar outro Admin Global? (s/N): ")
            if response.lower() != 's':
                self.stdout.write(
                    self.style.WARNING("\n❌ Operação cancelada.\n")
                )
                return

        # Verificar se o username já existe
        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.ERROR(
                    f"\n❌ Erro: O username '{username}' já existe!"
                )
            )
            self.stdout.write(
                self.style.ERROR(
                    "   Use --username para especificar outro.\n"
                )
            )
            return

        # Verificar se o email já existe
        if User.objects.filter(email=email).exists():
            self.stdout.write(
                self.style.ERROR(
                    f"\n❌ Erro: O email '{email}' já existe!"
                )
            )
            self.stdout.write(
                self.style.ERROR(
                    "   Use --email para especificar outro.\n"
                )
            )
            return

        # Confirmar dados
        self.stdout.write("\n📋 Dados do novo Admin Global:")
        self.stdout.write(f"   Username: {username}")
        self.stdout.write(f"   Email: {email}")
        self.stdout.write(f"   Nome: {first_name} {last_name}")
        self.stdout.write(f"   Senha: {'*' * len(password)}")

        response = input("\n❓ Confirma a criação? (S/n): ")
        if response.lower() == 'n':
            self.stdout.write(
                self.style.WARNING("\n❌ Operação cancelada.\n")
            )
            return

        # Criar usuário e perfil em uma transação
        try:
            with transaction.atomic():
                # Criar usuário
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    is_staff=True,
                    is_superuser=True,
                    is_active=True,
                    preferred_language='pt-br'
                )

                # Criar perfil de Admin Global
                admin_profile = AdminProfile.objects.create(
                    user=user,
                    access_level='global_admin',
                    country_code=None,  # Global não tem país
                    is_active=True
                )

                self.stdout.write("\n" + "="*70)
                self.stdout.write(
                    self.style.SUCCESS("✅ Admin Global criado com sucesso!")
                )
                self.stdout.write("="*70)
                
                self.stdout.write(
                    self.style.SUCCESS(f"\n👤 Username: {user.username}")
                )
                self.stdout.write(
                    self.style.SUCCESS(f"📧 Email: {user.email}")
                )
                self.stdout.write(
                    self.style.SUCCESS(f"👨‍💼 Nome: {user.get_full_name()}")
                )
                self.stdout.write(
                    self.style.SUCCESS(f"🔑 Senha: {password}")
                )
                self.stdout.write(
                    self.style.SUCCESS(f"🌍 Nível: {admin_profile.get_access_level_display()}")
                )
                
                self.stdout.write("\n" + "="*70)
                self.stdout.write(
                    self.style.SUCCESS("🚀 Você já pode fazer login no sistema!")
                )
                self.stdout.write(
                    self.style.SUCCESS("   URL: http://127.0.0.1:8000/admin/")
                )
                self.stdout.write("="*70 + "\n")

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"\n❌ Erro ao criar Admin Global: {str(e)}\n")
            )
            raise