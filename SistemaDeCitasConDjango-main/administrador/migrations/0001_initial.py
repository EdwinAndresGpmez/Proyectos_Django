# Generated by Django 5.0.7 on 2024-12-03 18:08

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Auditoria',
            fields=[
                ('id_aut', models.AutoField(primary_key=True, serialize=False)),
                ('descripcion_aut', models.TextField()),
                ('fecha', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Consultorio',
            fields=[
                ('id_con', models.AutoField(primary_key=True, serialize=False)),
                ('peso_con', models.IntegerField()),
                ('altura_con', models.CharField(max_length=100)),
                ('nota_con', models.TextField()),
                ('nacimiento_con', models.DateField(null=True)),
                ('consultorio_estado', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Disponibilidad',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_habilitada', models.DateField()),
                ('estado_disp', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Horas',
            fields=[
                ('id_hora', models.AutoField(primary_key=True, serialize=False)),
                ('inicio_hora', models.TimeField()),
                ('final_hora', models.TimeField()),
                ('horas_estado', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Lugares',
            fields=[
                ('id_lugar', models.AutoField(primary_key=True, serialize=False)),
                ('nombre_lugar', models.CharField(blank=True, max_length=255, null=True)),
                ('ubicacion_lugar', models.CharField(blank=True, max_length=255, null=True)),
                ('lugares_estado', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Pacientes',
            fields=[
                ('id_pac', models.AutoField(primary_key=True, serialize=False)),
                ('nombre_pac', models.CharField(max_length=255, verbose_name='Nombre del Paciente')),
                ('nacimiento_pac', models.DateField(verbose_name='Fecha de Nacimiento')),
                ('genero_pac', models.CharField(choices=[('M', 'Masculino'), ('F', 'Femenino'), ('O', 'Otro')], max_length=20, verbose_name='Género')),
                ('pacientes_estado', models.BooleanField(default=True, verbose_name='Estado Activo')),
            ],
        ),
        migrations.CreateModel(
            name='Profesional',
            fields=[
                ('id_prof', models.AutoField(primary_key=True, serialize=False)),
                ('nombre_prof', models.CharField(max_length=255)),
                ('especialidad_prof', models.CharField(max_length=255)),
                ('telefono_prof', models.CharField(blank=True, max_length=15, null=True)),
                ('email_prof', models.EmailField(blank=True, max_length=254, null=True)),
                ('estado_prof', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Representantes',
            fields=[
                ('id_rep', models.AutoField(primary_key=True, serialize=False)),
                ('nombre_rep', models.CharField(max_length=255, verbose_name='Nombre del Representante')),
                ('telefono_rep', models.CharField(blank=True, max_length=15, null=True, verbose_name='Teléfono')),
                ('email_rep', models.EmailField(blank=True, max_length=254, null=True, verbose_name='Correo Electrónico')),
                ('representante_estado', models.BooleanField(default=True, verbose_name='Estado Activo')),
            ],
        ),
    ]
