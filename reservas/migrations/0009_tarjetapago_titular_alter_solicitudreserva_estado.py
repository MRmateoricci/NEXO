# Generated by Django 5.2.1 on 2025-06-11 19:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reservas', '0008_tarjetapago_alter_solicitudreserva_estado_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='tarjetapago',
            name='titular',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='solicitudreserva',
            name='estado',
            field=models.CharField(choices=[('pendiente', 'Pendiente'), ('pendiente de pago', 'Pendiente de Pago'), ('pagada', 'Pagada'), ('confirmada', 'Confirmada'), ('cancelada', 'Cancelada')], default='pendiente', max_length=50),
        ),
    ]
