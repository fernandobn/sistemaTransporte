from django.shortcuts import render, get_object_or_404, redirect
from .models import Ruta, Pasaje, Administrador, Factura, Cliente, Horario, Bus, Conductor
from django.contrib import messages
from datetime import timedelta
from django.db import transaction
from decimal import Decimal, InvalidOperation
from django.utils.timezone import now
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from django.views.decorators.csrf import csrf_exempt


# Create your views here.

def inicio(request):
    return render(request, 'inicio.html')

def cerrarSecion(request):
    messages.success(request, "Se cerró sesión correctamente")
    return redirect('inicio')

# Vista para mostrar la plantilla base (opcional)
def plantilla(request):
    return render(request, 'plantilla.html')

# vista rutas


def rutas(request):
    rutas = Ruta.objects.all()
    for ruta in rutas:
        # Convierte duracion_aproximada a formato HH:MM:SS
        if isinstance(ruta.duracion_aproximada, timedelta):
            total_seconds = int(ruta.duracion_aproximada.total_seconds())
            hours, remainder = divmod(total_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            ruta.duracion_aproximada_formateada = f"{hours:02}:{minutes:02}:{seconds:02}"
        else:
            ruta.duracion_aproximada_formateada = "00:00:00"  # Valor por defecto
    return render(request, 'rutas.html', {'rutas': rutas})



def rutas_disponibles(request):
    # Recupera todas las rutas disponibles desde la base de datos
    rutas = Ruta.objects.all()

    # Contexto para enviar al template
    context = {
        'rutas': rutas,
    }

    # Renderiza el template con las rutas
    return render(request, 'rutas_disponibles.html', context)

def comprar_boletos(request):
    """
    Muestra el formulario para la compra de boletos con las rutas y horarios disponibles.
    """
    rutas = Ruta.objects.all()
    horarios = Horario.objects.all()
    return render(request, 'comprar_pasaje.html', {'rutas': rutas, 'horarios': horarios})


def guardar_compra(request):
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            nombre = request.POST.get('nombre')
            apellido = request.POST.get('apellido')
            telefono = request.POST.get('celular')
            ruta_id = request.POST.get('rutas')
            horario_id = request.POST.get('horario')
            cantidad = int(request.POST.get('cantidad'))

            # Validaciones básicas
            if not all([nombre, apellido, telefono, ruta_id, horario_id, cantidad > 0]):
                messages.error(request, "Todos los campos son obligatorios.")
                return redirect('comprar_boletos')

            # Crear cliente
            cliente = Cliente.objects.create(nombre=nombre, apellido=apellido, telefono=telefono)

            # Obtener ruta y horario
            ruta = get_object_or_404(Ruta, id_ruta=ruta_id)
            horario = get_object_or_404(Horario, id_horario=horario_id)

            # Crear pasajes y calcular total
            total = 0
            asiento_disponible = 1  # Comienza a buscar desde el asiento 1

            for i in range(cantidad):
                # Buscar el primer asiento disponible
                while Pasaje.objects.filter(horario=horario, numero_asiento=asiento_disponible).exists():
                    asiento_disponible += 1  # Incrementa hasta encontrar un asiento libre

                # Si ya se alcanzó el límite de asientos
                if asiento_disponible > 50:
                    messages.error(request, "No hay suficientes asientos disponibles para esta compra.")
                    return redirect('comprar_boletos')

                costo = ruta.precio
                total += costo
                Pasaje.objects.create(
                    cliente=cliente,
                    horario=horario,
                    numero_asiento=asiento_disponible,
                    costo=costo
                )

                # Incrementar el número de asiento para el siguiente pasaje
                asiento_disponible += 1

            # Crear la factura
            factura = Factura.objects.create(cliente=cliente, total=total)
            # Asociar los pasajes a la factura
            for pasaje in Pasaje.objects.filter(cliente=cliente, horario=horario):
                factura.pasajes.add(pasaje)

            # Guardar el ID de la factura en la sesión para usarlo después
            request.session['factura_id'] = factura.id_factura

            # Mensaje de éxito con información sobre la factura
            messages.success(request, f"Compra realizada con éxito. Su factura ha sido generada correctamente.")
            
            # Redirigir a la página de confirmación de compra
            return redirect('comprar_boletos')

        except Exception as e:
            # Mensaje de error
            messages.error(request, f"Hubo un error al procesar la compra: {e}")
            return redirect('comprar_boletos')

    return redirect('comprar_boletos')

def generar_comprobante(request, factura_id):
    # Obtener la factura y sus pasajes
    factura = get_object_or_404(Factura, id_factura=factura_id)
    pasajes = factura.pasajes.all()

    # Renderizar el HTML de la factura
    html_string = render_to_string('factura.html', {'factura': factura, 'pasajes': pasajes})

    # Crear un objeto HttpResponse para el PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="factura_{factura_id}.pdf"'

    # Generar el PDF a partir del HTML
    pisa_status = pisa.CreatePDF(html_string, dest=response)

    # Si hubo un error al generar el PDF
    if pisa_status.err:
        return HttpResponse('Error al generar el PDF', status=500)

    return response

def ir_factura(request):
    return render(request,'factura.html')

def listado_facturas(request):
    facturas = Factura.objects.all()
    return render(request, 'lista_facturas.html', {'facturas': facturas})

# Funciones para el admin


def inicio_admin(request):
    return render (request,'inicio_admin.html')

def login (request):
    return render (request,'login.html')

def compararlogin(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        password = request.POST.get('password')

        # Verificar si el nombre y la contraseña son correctos
        if nombre == 'administrador' and password == 'administrador':
            messages.success(request, "Se inició sesión correctamente.")
            return redirect('ir_bus')  # Redirigir a la página principal después de login
        else:
            # Si las credenciales no coinciden
            messages.error(request, "Error: Nombre de usuario o contraseña incorrectos.")
            return redirect('login')  # Redirigir al formulario de login en caso de error
    else:
        return redirect('login')


# Funciones para buses

def ir_bus(request):
    # Listar todos los buses
    buses = Bus.objects.all()
    return render(request, 'guardar_buses.html', {"buses": buses})

def guardar_bus(request):
    if request.method == "POST":
        placa = request.POST.get("placa")
        capacidad = request.POST.get("capacidad")
        modelo = request.POST.get("modelo")
        marca = request.POST.get("marca")

        if not placa or not capacidad or not modelo or not marca:
            messages.error(request, "Todos los campos son obligatorios.")
            return redirect("ir_bus")

        try:
            # Crear un nuevo bus
            Bus.objects.create(
                placa=placa,
                capacidad=capacidad,
                modelo=modelo,
                marca=marca
            )
            messages.success(request, "Bus guardado correctamente.")
        except Exception as e:
            messages.error(request, f"Error al guardar el bus: {str(e)}")

        return redirect("ir_bus")




# Funciones para conductores
def ir_bus(request):
    # Listar todos los buses
    buses = Bus.objects.all()
    return render(request, 'guardar_buses.html', {"buses": buses})

def guardar_bus(request):
    if request.method == "POST":
        placa = request.POST.get("placa")
        capacidad = request.POST.get("capacidad")
        modelo = request.POST.get("modelo")
        marca = request.POST.get("marca")

        if not placa or not capacidad or not modelo or not marca:
            messages.error(request, "Todos los campos son obligatorios.")
            return redirect("ir_bus")

        try:
            # Crear un nuevo bus
            Bus.objects.create(
                placa=placa,
                capacidad=capacidad,
                modelo=modelo,
                marca=marca
            )
            messages.success(request, "Bus guardado correctamente.")
        except Exception as e:
            messages.error(request, f"Error al guardar el bus: {str(e)}")

        return redirect("ir_bus")

def ir_conductor(request):
    # Listar todos los buses y conductores
    buses = Bus.objects.all()
    conductores = Conductor.objects.all()
    return render(request, 'guardar_conductores.html', {"buses": buses, "conductores": conductores})

def guardar_conductor(request):
    if request.method == "POST":
        nombre = request.POST.get("nombre")
        cedula = request.POST.get("cedula")
        telefono = request.POST.get("telefono")
        bus_asignado_id = request.POST.get("bus_asignado")

        if not nombre or not cedula or not bus_asignado_id:
            messages.error(request, "Nombre, cédula y bus asignado son obligatorios.")
            return redirect("ir_conductor")

        try:
            bus_asignado = Bus.objects.get(id_bus=bus_asignado_id)
            Conductor.objects.create(
                nombre=nombre,
                cedula=cedula,
                telefono=telefono,
                bus_asignado=bus_asignado
            )
            messages.success(request, "Conductor guardado correctamente.")
        except Bus.DoesNotExist:
            messages.error(request, "El bus asignado no existe.")
        except Exception as e:
            messages.error(request, f"Error al guardar el conductor: {str(e)}")

        return redirect("ir_conductor")



# Funciones para rutas

# Función para listar rutas
def ir_ruta(request):
    buses = Bus.objects.all()
    rutas = Ruta.objects.select_related('bus').all()
    return render(request, 'guardar_rutas.html', {'buses': buses, 'rutas': rutas})


# Función para gestionar rutas
def gestionar_rutas(request):
    if request.method == 'POST':
        # Obtener datos del formulario
        origen = request.POST.get('origen', '').strip()
        destino = request.POST.get('destino', '').strip()
        duracion_aproximada = request.POST.get('duracion_aproximada', '').strip()  # Formato HH:MM
        precio = request.POST.get('precio', '').strip()
        bus_id = request.POST.get('bus', '').strip()

        # Validar campos obligatorios
        if not origen or not destino or not duracion_aproximada or not precio or not bus_id:
            messages.error(request, "Todos los campos son obligatorios.")
            return redirect('gestionar_rutas')

        try:
            # Validar formato de la duración
            horas, minutos = map(int, duracion_aproximada.split(':'))
            duracion = timedelta(hours=horas, minutes=minutos)

            # Validar que el precio sea un número positivo
            precio = float(precio)
            if precio <= 0:
                raise ValueError("El precio debe ser un número positivo.")

            # Validar que el bus existe
            try:
                bus = Bus.objects.get(id_bus=bus_id)  # Cambiado a id_bus
            except Bus.DoesNotExist:
                raise ValueError("El bus seleccionado no existe.")

            # Guardar la ruta en la base de datos
            ruta = Ruta(
                origen=origen,
                destino=destino,
                duracion_aproximada=duracion,
                precio=precio,
                bus=bus  # Relacionar la ruta con el bus
            )
            ruta.save()
            messages.success(request, "Ruta guardada exitosamente.")
        except ValueError as ve:
            messages.error(request, f"Error en los datos ingresados: {str(ve)}")
        except Exception as e:
            messages.error(request, f"Error al guardar la ruta: {str(e)}")

        return redirect('gestionar_rutas')

    # Método GET: Listar todas las rutas y obtener los buses disponibles
    rutas = Ruta.objects.select_related('bus').all()  # Carga la relación con el modelo Bus
    buses = Bus.objects.all()  # Obtener todos los buses disponibles
    return render(request, 'guardar_rutas.html', {'rutas': rutas, 'buses': buses})








# Funciones para pasajeros

def listado_pasajes(request):
    # Obtener todos los pasajes registrados, con datos relacionados de cliente y horario
    pasajes = Pasaje.objects.select_related('cliente', 'horario__ruta').all()

    # Pasar los pasajes al contexto para renderizar la plantilla
    return render(request, 'listado_pasajes.html', {'pasajes': pasajes})

# Funciones para horarios

def ir_horario(request):
    # Obtener todas las rutas disponibles
    rutas = Ruta.objects.all()

    # Obtener todos los horarios registrados
    horarios = Horario.objects.all()

    # Pasar las rutas y los horarios al contexto para que estén disponibles en la plantilla
    return render(request, 'guardar_horario.html', {'rutas': rutas, 'horarios': horarios})

def guardar_horario(request):
    if request.method == 'POST':
        # Obtenemos los datos del formulario
        ruta_id = request.POST.get('ruta')
        hora_salida = request.POST.get('hora_salida')
        hora_llegada = request.POST.get('hora_llegada')

        # Comprobamos si la ruta existe
        try:
            ruta = Ruta.objects.get(id_ruta=ruta_id)
        except Ruta.DoesNotExist:
            messages.error(request, "La ruta seleccionada no existe.")
            return redirect('ir_horario')

        # Creamos y guardamos el horario
        nuevo_horario = Horario(
            ruta=ruta,
            hora_salida=hora_salida,
            hora_llegada=hora_llegada
        )
        nuevo_horario.save()

        messages.success(request, "Horario guardado exitosamente.")
        return redirect('ir_horario')

    # Si no es un POST, redirigir a la página de guardado de horarios
    return redirect('ir_horario')




# funciones para eliminar


# Eliminar Bus
@csrf_exempt
def eliminar_bus(request, id_bus):
    if request.method == 'POST':
        try:
            bus = Bus.objects.get(id_bus=id_bus)

            # Verificar si el bus está asignado a una ruta
            if Ruta.objects.filter(bus=bus).exists():
                return JsonResponse({'success': False, 'message': f"El bus {bus.placa} está asignado a una ruta y no puede ser eliminado."})
            
            bus.delete()
            return JsonResponse({'success': True, 'message': f"El bus {bus.placa} ha sido eliminado."})
        
        except Bus.DoesNotExist:
            return JsonResponse({'success': False, 'message': "El bus no existe."})

# Eliminar Conductor
@csrf_exempt
def eliminar_conductor(request, id_conductor):
    if request.method == 'POST':
        try:
            conductor = Conductor.objects.get(id_conductor=id_conductor)

            # Verificar si el conductor está asignado a un bus
            if conductor.bus_asignado:
                return JsonResponse({'success': False, 'message': f"El conductor {conductor.nombre} está asignado a un bus y no puede ser eliminado."})
            
            conductor.delete()
            return JsonResponse({'success': True, 'message': f"El conductor {conductor.nombre} ha sido eliminado."})
        
        except Conductor.DoesNotExist:
            return JsonResponse({'success': False, 'message': "El conductor no existe."})

# Eliminar Ruta
@csrf_exempt
def eliminar_ruta(request, id_ruta):
    if request.method == 'POST':
        try:
            ruta = Ruta.objects.get(id_ruta=id_ruta)

            # Verificar si la ruta tiene pasajes o horarios asociados
            if Pasaje.objects.filter(horario__ruta=ruta).exists() or Horario.objects.filter(ruta=ruta).exists():
                return JsonResponse({'success': False, 'message': "La ruta tiene pasajes o horarios asociados y no puede ser eliminada."})
            
            ruta.delete()
            return JsonResponse({'success': True, 'message': "La ruta ha sido eliminada."})
        
        except Ruta.DoesNotExist:
            return JsonResponse({'success': False, 'message': "La ruta no existe."})

#Eliminar pasaje y factura
@csrf_exempt
def eliminar_pasaje(request, id_pasaje):
    if request.method == 'POST':
        try:
            # Obtener el pasaje
            pasaje = Pasaje.objects.get(id_pasaje=id_pasaje)

            # Eliminar el pasaje
            pasaje.delete()

            return JsonResponse({'success': True, 'message': "El pasaje ha sido eliminado."})

        except Pasaje.DoesNotExist:
            return JsonResponse({'success': False, 'message': "El pasaje no existe."})

        except Exception as e:
            # Captura cualquier otro error inesperado
            return JsonResponse({'success': False, 'message': f"Ocurrió un error: {str(e)}"})

@csrf_exempt
def eliminar_factura(request, id_factura):
    if request.method == 'POST':
        try:
            # Obtener la factura
            factura = Factura.objects.get(id_factura=id_factura)

            # Eliminar los pasajes asociados a la factura (si los hay)
            factura.pasajes.all().delete()

            # Eliminar la factura
            factura.delete()

            return JsonResponse({'success': True, 'message': "La factura y los pasajes asociados han sido eliminados."})

        except Factura.DoesNotExist:
            return JsonResponse({'success': False, 'message': "La factura no existe."})

        except Exception as e:
            # Captura cualquier otro error inesperado
            return JsonResponse({'success': False, 'message': f"Ocurrió un error: {str(e)}"})





# Eliminar Horario
@csrf_exempt
def eliminar_horario(request, id_horario):
    if request.method == 'POST':
        try:
            horario = Horario.objects.get(id_horario=id_horario)

            # Verificar si el horario tiene pasajes asociados
            if Pasaje.objects.filter(horario=horario).exists():
                return JsonResponse({'success': False, 'message': "El horario tiene pasajes asociados y no puede ser eliminado."})
            
            horario.delete()
            return JsonResponse({'success': True, 'message': "El horario ha sido eliminado."})
        
        except Horario.DoesNotExist:
            return JsonResponse({'success': False, 'message': "El horario no existe."})

# Funciones para editar
def editar_bus (request, id_bus):
    """
    Muestra el formulario para editar un bus específico.
    """
    try:
        bus = Bus.objects.get(id_bus=id_bus)
    except Bus.DoesNotExist:
        messages.error(request, "El bus no existe.")
        return redirect('ir_bus')  # Cambia esto al nombre de tu vista de lista de buses.

    return render(request, "editar_buses.html", {
        'bus': bus,
    })

def procesar_edicion_bus(request):
    """
    Procesa los datos enviados desde el formulario de edición de buses.
    """
    if request.method == 'POST':
        try:
            bus = Bus.objects.get(id_bus=request.POST['id_bus'])
        except Bus.DoesNotExist:
            messages.error(request, "El bus no existe.")
            return redirect('ir_bus')  # Cambia esto al nombre de tu vista de lista de buses.

        # Actualiza los datos del bus
        bus.placa = request.POST['placa']
        bus.capacidad = request.POST['capacidad']
        bus.modelo = request.POST['modelo']
        bus.marca = request.POST['marca']
        bus.save()

        messages.success(request, "Bus actualizado correctamente.")
        return redirect('ir_bus')  # Cambia esto al nombre de tu vista de lista de buses.

    return redirect('ir_bus')  # Cambia esto al nombre de tu vista de lista de buses.

# Función para mostrar el formulario de edición de conductor
def editar_conductor(request, id_conductor):
    try:
        conductor = Conductor.objects.get(id_conductor=id_conductor)
        buses = Bus.objects.all()  # Obtener todos los buses para mostrarlos en el formulario
    except Conductor.DoesNotExist:
        messages.error(request, "El conductor no existe.")
        return redirect('ir_conductor')  # Cambia esto al nombre de tu vista de lista de conductores

    return render(request, "editar_conductores.html", {
        'conductor': conductor,
        'buses': buses,
    })
# Función para procesar la edición de un conductor
def procesar_edicion_conductor(request):
    if request.method == 'POST':
        try:
            conductor = Conductor.objects.get(id_conductor=request.POST['id_conductor'])
        except Conductor.DoesNotExist:
            messages.error(request, "El conductor no existe.")
            return redirect('ir_conductor')  # Cambia esto al nombre de tu vista de lista de conductores

        # Actualizar los datos del conductor
        conductor.nombre = request.POST['nombre']
        conductor.cedula = request.POST['cedula']
        conductor.telefono = request.POST.get('telefono', None)  # Puede ser nulo
        conductor.bus_asignado = get_object_or_404(Bus, id_bus=request.POST['bus_asignado'])
        conductor.save()

        messages.success(request, "Conductor actualizado correctamente.")
        return redirect('ir_conductor')  # Cambia esto al nombre de tu vista de lista de conductores

    return redirect('ir_conductor')

def editar_horario(request, id_horario):
    # Obtener el horario a editar utilizando el id_horario
    horario = get_object_or_404(Horario, id_horario=id_horario)
    # Obtener todas las rutas disponibles
    rutas = Ruta.objects.all()

    return render(request, "editar_horario.html", {
        'horario': horario,
        'rutas': rutas,  # Pasar las rutas a la plantilla
    })




def procesar_edicion_horario(request):
    if request.method == 'POST':
        id_horario = request.POST['id_horario']
        # Obtener el horario usando el id
        horario = get_object_or_404(Horario, id_horario=id_horario)

        # Actualizar los campos de hora_salida, hora_llegada y ruta
        horario.hora_salida = request.POST['hora_salida']
        horario.hora_llegada = request.POST['hora_llegada']

        # Obtener la nueva ruta seleccionada
        nueva_ruta_id = request.POST['ruta']
        if nueva_ruta_id:
            nueva_ruta = get_object_or_404(Ruta, id_ruta=nueva_ruta_id)
            horario.ruta = nueva_ruta  # Asignar la nueva ruta al horario

        horario.save()  # Guardar los cambios en la base de datos

        messages.success(request, "Horario actualizado correctamente.")
        return redirect('guardar_horario')  # Redirigir a la página de gestión de horarios o alguna otra vista

    return redirect('guardar_horario')  # Redirigir si no es una solicitud POST


def editar_ruta(request, id_ruta):
    # Obtener la ruta a editar utilizando el id_ruta
    ruta = get_object_or_404(Ruta, id_ruta=id_ruta)
    # Obtener todos los buses disponibles
    buses = Bus.objects.all()

    return render(request, "editar_rutas.html", {
        'ruta': ruta,
        'buses': buses,  # Pasar los buses a la plantilla
    })

def procesar_edicion_ruta(request):
    if request.method == 'POST':
        ruta_id = request.POST.get('id_ruta')
        ruta = Ruta.objects.get(id_ruta=ruta_id)

        # Obtener el valor de duración desde el formulario (como string)
        duracion_str = request.POST.get('duracion_aproximada')  # Asegúrate de que el campo esté en el formulario

        # Convertir el valor de duración a un objeto timedelta
        if duracion_str:
            horas, minutos, segundos = map(int, duracion_str.split(":"))
            duracion = timedelta(hours=horas, minutes=minutos, seconds=segundos)
            ruta.duracion_aproximada = duracion

        # Actualizar otros campos según lo necesites
        ruta.origen = request.POST.get('origen')
        ruta.destino = request.POST.get('destino')

        # Obtener y limpiar el valor de precio (reemplazar coma por punto)
        precio_str = request.POST.get('precio')
        if precio_str:
            precio_str = precio_str.replace(',', '.')  # Reemplazar coma por punto
            try:
                ruta.precio = Decimal(precio_str)  # Convertir a Decimal
            except InvalidOperation:
                # Si el valor no es un número decimal válido, agregar mensaje de error
                messages.error(request, "El precio debe ser un número decimal válido.")
                return redirect('editar_ruta', id_ruta=ruta.id_ruta)

        # Obtener el bus seleccionado del formulario y asignarlo a la ruta
        bus_id = request.POST.get('bus')
        if bus_id:
            ruta.bus_id = bus_id  # Asignar el bus seleccionado

        # Guardar el objeto ruta
        ruta.save()

        # Agregar mensaje de éxito
        messages.success(request, "La ruta se ha actualizado correctamente.")

        return redirect('gestionar_rutas')

    # Si el método no es POST, redirigir al listado de rutas
    messages.error(request, "Error al intentar procesar la edición de la ruta.")
    return redirect('gestionar_rutas')



