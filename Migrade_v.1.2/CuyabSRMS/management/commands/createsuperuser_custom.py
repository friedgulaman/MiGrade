from django.contrib.auth.management.commands.createsuperuser import Command as BaseCommand
from django.core.management import CommandError
from django.utils.translation import gettext as _
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password  # Import make_password function to hash the password
import os
from dotenv import load_dotenv
load_dotenv()

class Command(BaseCommand):
    help = 'Create a superuser with additional fields.'

    def add_arguments(self, parser):
        super().add_arguments(parser)
        # Add additional arguments
        parser.add_argument('--user_type', type=int, help='User type')
        parser.add_argument('--password', help='User password')

    def handle(self, *args, **options):
        default = os.getenv("SUPER")
        username = options.get('username')
        email = options.get('email')
        password = options.get('password')
        user_type = options.get('user_type')

        # Validate if all required options are provided
        if not username or not email or user_type is None:
            raise CommandError(_("Required fields missing. Please provide username, email, and user_type."))

        # Set the default password if not provided
        if not password:
            password = default  # Set default password to "super_pass"

        
        CustomUser = get_user_model()
        CustomUser.objects.create_superuser(username=username, email=email, password=password, user_type=user_type)
