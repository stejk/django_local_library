# Generated by Django 2.0.3 on 2018-03-20 13:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0004_auto_20180319_2016'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='author',
            options={'ordering': ['last_name', 'first_name'], 'permissions': (('can_edit_author', 'Can administer authors'),)},
        ),
    ]
