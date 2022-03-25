import db_script
from django.db import migrations
from django.conf import settings
from django.contrib.auth.models import Group
from employee.models import User


def forwards(apps, schema_editor):
    if schema_editor.connection.alias != 'default':
        return

    if not User.objects.filter(email=settings.ADMIN_EMAIL):
        admin = User.objects.create_superuser(email=settings.ADMIN_EMAIL,
                                              password=settings.ADMIN_PASSWORD)
        admin.is_active = True
        admin.is_admin = True
        admin.save()

    if not Group.objects.filter(name='Have API access Group'):
        group = Group(name='Have API access Group')
        group.save()


class Migration(migrations.Migration):

    dependencies = [
        ('employee', '0003_alter_paylog_amount'),
    ]

    operations = [
        migrations.RunPython(forwards),
    ]
