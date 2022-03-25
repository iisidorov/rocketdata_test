from django.conf import settings
from django.core.management.base import BaseCommand
from employee.models import User


class Command(BaseCommand):
    def handle(self, *args, **options):
        if User.objects.count() == 0:
            admin = User.objects.create_superuser(email=settings.ADMIN_EMAIL,
                                                  password=settings.ADMIN_PASSWORD)
            admin.is_active = True
            admin.is_admin = True
            admin.save()
            print("Admin created successfully")
        else:
            print('Admin account can only be initialized if no Users exist')
