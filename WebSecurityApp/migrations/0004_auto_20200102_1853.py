# Generated by Django 2.0 on 2020-01-02 18:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('WebSecurityApp', '0003_auto_20191226_1654'),
    ]

    operations = [
        migrations.RenameField(
            model_name='actividad',
            old_name='fechaCreacion',
            new_name='fecha_creacion',
        ),
        migrations.RenameField(
            model_name='actividad',
            old_name='motivoVeto',
            new_name='motivo_veto',
        ),
        migrations.RenameField(
            model_name='usuario',
            old_name='empresaUEquipo',
            new_name='empresa_u_equipo',
        ),
        migrations.RenameField(
            model_name='usuario',
            old_name='esAdmin',
            new_name='es_admin',
        ),
    ]