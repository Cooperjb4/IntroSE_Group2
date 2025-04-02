# Generated by Django 5.1.5 on 2025-04-02 15:23

from django.db import migrations

def create_groups(apps, schema_editor):
    # Use apps.get_model to safely load the Group model
    Group = apps.get_model('auth', 'Group')
    Group.objects.get_or_create(name='Admin')
    Group.objects.get_or_create(name='Seller')
    Group.objects.get_or_create(name='User')

class Migration(migrations.Migration):

    dependencies = [ 
        ('auth', '0012_alter_user_first_name_max_length'),  # Ensure the auth app is migrated first
    ]

    operations = [
        migrations.RunPython(create_groups),  # Add the function to the migration
    ]
