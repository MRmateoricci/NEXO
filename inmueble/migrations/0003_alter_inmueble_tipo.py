# Generated by Django 5.2.1 on 2025-05-28 14:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inmueble', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inmueble',
            name='tipo',
            field=models.CharField(choices=[('casa', 'Casa'), ('local', 'Local'), ('cochera', 'Cochera'), ('departamento', 'Departamento')], max_length=50),
        ),
    ]
