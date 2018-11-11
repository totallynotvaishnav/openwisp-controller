from django.db import migrations
from django.contrib.auth.models import Permission
from django.contrib.auth.management import create_permissions


def create_default_permissions(apps, schema_editor):
    for app_config in apps.get_app_configs():
        app_config.models_module = True
        create_permissions(app_config, apps=apps, verbosity=0)
        app_config.models_module = None


def assign_permissions_to_groups(apps, schema_editor):
    Group = apps.get_model('openwisp_users', 'Group')
    admin = Group.objects.get(name='Administrator')
    operator = Group.objects.get(name='Operator')
    operators_and_admins_can_change = ['device', 'config', 'template']
    operators_read_only_admins_manage = ['vpn']
    manage_operations = ['add', 'change', 'delete']

    for model_name in operators_and_admins_can_change:
        for operation in manage_operations:
            permission = Permission.objects.get(
                codename='{}_{}'.format(operation, model_name)
            )
            admin.permissions.add(permission.pk)
            operator.permissions.add(permission.pk)
            
    for model_name in operators_read_only_admins_manage:
        try:
            permission = Permission.objects.get(
                codename="view_{}".format(model_name)
            )
            operator.permissions.add(permission.pk)
        except Permission.DoesNotExist:
            pass

        for operation in manage_operations:
            admin.permissions.add(
                Permission.objects.get(codename="{}_{}".format(operation, model_name)).pk
            )


class Migration(migrations.Migration):
    dependencies = [
        ('openwisp_users', '0004_default_groups'),
        ('pki', '__first__'),
        ('geo', '__first__'),
        ('config', '0014_device_hardware_id'),
    ]

    operations = [
        migrations.RunPython(
            create_default_permissions,
            reverse_code=migrations.RunPython.noop
        ),
        migrations.RunPython(
            assign_permissions_to_groups,
            reverse_code=migrations.RunPython.noop
        ),
    ]
