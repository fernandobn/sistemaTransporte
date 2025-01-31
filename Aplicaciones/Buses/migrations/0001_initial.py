# Generated by Django 5.1.4 on 2025-01-11 17:07

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Administrador",
            fields=[
                (
                    "id_administrador",
                    models.AutoField(primary_key=True, serialize=False),
                ),
                ("nombre", models.CharField(default="administrador", max_length=100)),
                (
                    "contraseña",
                    models.CharField(default="administrador", max_length=128),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Bus",
            fields=[
                ("id_bus", models.AutoField(primary_key=True, serialize=False)),
                ("placa", models.CharField(max_length=10, unique=True)),
                ("capacidad", models.PositiveIntegerField()),
                ("modelo", models.CharField(max_length=50)),
                ("marca", models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name="Cliente",
            fields=[
                ("id_cliente", models.AutoField(primary_key=True, serialize=False)),
                ("nombre", models.CharField(max_length=100)),
                ("apellido", models.CharField(max_length=100)),
                ("telefono", models.CharField(blank=True, max_length=10, null=True)),
            ],
        ),
        migrations.CreateModel(
            name="Horario",
            fields=[
                ("id_horario", models.AutoField(primary_key=True, serialize=False)),
                ("hora_salida", models.TimeField()),
                ("hora_llegada", models.TimeField()),
            ],
        ),
        migrations.CreateModel(
            name="Conductor",
            fields=[
                ("id_conductor", models.AutoField(primary_key=True, serialize=False)),
                ("nombre", models.CharField(max_length=100)),
                ("cedula", models.CharField(max_length=10, unique=True)),
                ("telefono", models.CharField(blank=True, max_length=10, null=True)),
                (
                    "bus_asignado",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE, to="Buses.bus"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Pasaje",
            fields=[
                ("id_pasaje", models.AutoField(primary_key=True, serialize=False)),
                ("numero_asiento", models.PositiveIntegerField()),
                ("costo", models.DecimalField(decimal_places=2, max_digits=8)),
                ("fecha_compra", models.DateTimeField(auto_now_add=True)),
                (
                    "cliente",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="Buses.cliente"
                    ),
                ),
                (
                    "horario",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="Buses.horario"
                    ),
                ),
            ],
            options={
                "unique_together": {("horario", "numero_asiento")},
            },
        ),
        migrations.CreateModel(
            name="Factura",
            fields=[
                ("id_factura", models.AutoField(primary_key=True, serialize=False)),
                ("fecha_emision", models.DateTimeField(auto_now_add=True)),
                ("total", models.DecimalField(decimal_places=2, max_digits=10)),
                (
                    "cliente",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="Buses.cliente"
                    ),
                ),
                ("pasajes", models.ManyToManyField(to="Buses.pasaje")),
            ],
        ),
        migrations.CreateModel(
            name="Ruta",
            fields=[
                ("id_ruta", models.AutoField(primary_key=True, serialize=False)),
                ("origen", models.CharField(max_length=100)),
                ("destino", models.CharField(max_length=100)),
                ("duracion_aproximada", models.DurationField()),
                ("precio", models.DecimalField(decimal_places=2, max_digits=8)),
                (
                    "bus",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="Buses.bus"
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="horario",
            name="ruta",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="Buses.ruta"
            ),
        ),
    ]
