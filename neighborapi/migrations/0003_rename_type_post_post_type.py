# Generated by Django 4.2.8 on 2023-12-06 09:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('neighborapi', '0002_alter_neighbor_profile_image_alter_post_image'),
    ]

    operations = [
        migrations.RenameField(
            model_name='post',
            old_name='type',
            new_name='post_type',
        ),
    ]