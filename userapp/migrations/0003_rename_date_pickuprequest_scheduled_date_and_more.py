# Generated by Django 5.1.3 on 2025-06-24 12:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('userapp', '0002_alter_pickuprequest_user'),
    ]

    operations = [
        migrations.RenameField(
            model_name='pickuprequest',
            old_name='date',
            new_name='scheduled_date',
        ),
        migrations.RenameField(
            model_name='pickuprequest',
            old_name='time',
            new_name='scheduled_time',
        ),
    ]
