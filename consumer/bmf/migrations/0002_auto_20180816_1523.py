# Generated by Django 2.1 on 2018-08-16 15:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bmf', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='company',
            old_name='inserted_at',
            new_name='created_at',
        ),
    ]
