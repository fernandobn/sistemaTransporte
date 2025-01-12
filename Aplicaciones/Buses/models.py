from django.db import models

# Modelo de Administrador
class Administrador(models.Model):
    id_administrador = models.AutoField(primary_key=True)  # Campo id específico
    nombre = models.CharField(max_length=100, default='administrador')  # Nombre predeterminado
    contraseña = models.CharField(max_length=128, default='administrador')  # Contraseña predeterminada

    def __str__(self):
        return self.nombre


# Modelo de Cliente
class Cliente(models.Model):
    id_cliente = models.AutoField(primary_key=True)  # Campo id específico
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    telefono = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return f"{self.nombre} - {self.cedula}"

# Modelo de Bus
class Bus(models.Model):
    id_bus = models.AutoField(primary_key=True)  # Campo id específico
    placa = models.CharField(max_length=10, unique=True)
    capacidad = models.PositiveIntegerField()
    modelo = models.CharField(max_length=50)
    marca = models.CharField(max_length=50)

    def __str__(self):
        return f"Bus {self.placa} - {self.marca} {self.modelo}"

# Modelo de Conductor
class Conductor(models.Model):
    id_conductor = models.AutoField(primary_key=True)  # Campo id específico
    nombre = models.CharField(max_length=100)
    cedula = models.CharField(max_length=10, unique=True)
    telefono = models.CharField(max_length=10, blank=True, null=True)
    bus_asignado = models.OneToOneField(Bus, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.nombre} - Bus {self.bus_asignado.placa}"

# Modelo de Ruta
class Ruta(models.Model):
    id_ruta = models.AutoField(primary_key=True)  # Campo id específico
    origen = models.CharField(max_length=100)
    destino = models.CharField(max_length=100)
    duracion_aproximada = models.DurationField()
    precio = models.DecimalField(max_digits=8, decimal_places=2)
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE)  # Relación con el modelo Bus
  

    def __str__(self):
        return f"{self.origen} -> {self.destino}"

# Modelo de Horario
class Horario(models.Model):
    id_horario = models.AutoField(primary_key=True)  # Campo id específico
    ruta = models.ForeignKey(Ruta, on_delete=models.CASCADE)
    hora_salida = models.TimeField()
    hora_llegada = models.TimeField()

    def __str__(self):
        return f"{self.ruta} - Salida: {self.hora_salida}"

# Modelo de Pasaje
class Pasaje(models.Model):
    id_pasaje = models.AutoField(primary_key=True)  # Campo id específico
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    horario = models.ForeignKey(Horario, on_delete=models.CASCADE)
    numero_asiento = models.PositiveIntegerField()
    costo = models.DecimalField(max_digits=8, decimal_places=2)
    fecha_compra = models.DateTimeField(auto_now_add=True)
    

    def __str__(self):
        return f"Pasaje Cliente: {self.cliente.nombre}, Asiento: {self.numero_asiento}"

    class Meta:
        unique_together = ('horario', 'numero_asiento')

# Modelo de Factura
class Factura(models.Model):
    id_factura = models.AutoField(primary_key=True)  # Campo id específico
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    fecha_emision = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    pasajes = models.ManyToManyField(Pasaje)

    def __str__(self):
        return f"Factura {self.id_factura} - Cliente: {self.cliente.nombre}"
