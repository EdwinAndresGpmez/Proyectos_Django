# Generated by Django 5.0.7 on 2024-12-09 17:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('administrador', '0007_servicio'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profesional',
            name='email_prof',
            field=models.EmailField(blank=True, max_length=254, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='profesional',
            name='id_prof',
            field=models.AutoField(primary_key=True, serialize=False, unique=True),
        ),
        migrations.AlterField(
            model_name='profesional',
            name='telefono_prof',
            field=models.CharField(blank=True, max_length=15, null=True, unique=True),
        ),
    ]