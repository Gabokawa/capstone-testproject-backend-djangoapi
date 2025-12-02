from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Creates a superuser'

    def handle(self, *args, **options):
        User = get_user_model()
        username = 'CapstoneSuperUser'
        email = 'CapstoneSuperUser'
        password = 'CapstoneSuperUser'  # Change this!
        
        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(username, email, password)
            self.stdout.write(self.style.SUCCESS('Superuser created successfully'))
        else:
            self.stdout.write(self.style.WARNING('Superuser already exists'))