from django.urls import path
from . import views

urlpatterns = [
    # rutas de usuario
    path('', views.inicio, name='inicio'),
    path('cerrarSecion/', views.cerrarSecion, name='cerrarSecion'),

    path('plantilla/', views.plantilla, name='plantilla'),
    path('rutas/', views.rutas, name='rutas'), 
    path('rutas_disponibles/', views.rutas_disponibles, name='rutas_disponibles'),
    path('login/', views.login, name='login'),
    path('compararlogin/', views.compararlogin, name='compararlogin'),
    path('inicio_admin/', views.inicio_admin, name='inicio_admin'),

    ## rutas para el apartado de aministracion

    path('ir_bus/', views.ir_bus, name='ir_bus'),
    path('guardar_bus/', views.guardar_bus, name='guardar_bus'),
    path('ir_conductor/', views.ir_conductor, name='ir_conductor'),
    path('guardar_conductor/', views.guardar_conductor, name='guardar_conductor'),
    path('ir_ruta/', views.ir_ruta, name='ir_ruta'),
    path('gestionar_rutas/', views.gestionar_rutas, name='gestionar_rutas'),
    path('listado_pasajes/', views.listado_pasajes, name='listado_pasajes'),
    path('ir_horario/', views.ir_horario, name='ir_horario'),
    path('guardar_horario/', views.guardar_horario, name='guardar_horario'),

    
    # URL para guadar y generar compra

    path('ir_factura/', views.ir_factura, name='ir_factura'),
    path('comprar_boletos/', views.comprar_boletos, name='comprar_boletos'),
    path('guardar_compra/', views.guardar_compra, name='guardar_compra'),
    path('generar_comprobante/<int:factura_id>/', views.generar_comprobante, name='generar_comprobante'),
    path('listado_facturas/', views.listado_facturas, name='listado_facturas'),

    # url para eliminar
   # URL para eliminar bus
    path('eliminarBus/<int:id_bus>/', views.eliminar_bus, name='eliminar_bus'),
    
    # URL para eliminar conductor
    path('eliminar_conductor/<int:id_conductor>/', views.eliminar_conductor, name='eliminar_conductor'),
    
    # URL para eliminar ruta
    path('eliminar_ruta/<int:id_ruta>/', views.eliminar_ruta, name='eliminar_ruta'),
    
    # URL para eliminar pasaje
    path('eliminar_pasaje/<int:id_pasaje>/', views.eliminar_pasaje, name='eliminar_pasaje'),  # Nueva URL para pasaje y factura
    path('eliminar_factura/<int:id_factura>/', views.eliminar_factura, name='eliminar_factura'),  # Nueva URL para pasaje y factura

    # URL para eliminar horario
    path('eliminar_horario/<int:id_horario>/', views.eliminar_horario, name='eliminar_horario'),

    # URL para mostrar el formulario de edición de un bus
    path('editar_bus/<int:id_bus>/', views.editar_bus, name='editar_bus'),

    # URL para procesar la edición del bus
    path('procesar_edicion_bus/', views.procesar_edicion_bus, name='procesar_edicion_bus'),
# URL para mostrar el formulario de edición de conductor
    path('editar_conductor/<int:id_conductor>/', views.editar_conductor, name='editar_conductor'),

    # URL para procesar la edición del conductor
    path('procesar_edicion_conductor/', views.procesar_edicion_conductor, name='procesar_edicion_conductor'),
    path('editar_horario/<int:id_horario>/', views.editar_horario, name='editar_horario'),
    path('procesar_edicion_horario/', views.procesar_edicion_horario, name='procesar_edicion_horario'),
    path('editar_ruta/<int:id_ruta>/', views.editar_ruta, name='editar_ruta'),
    path('procesar_edicion_ruta/', views.procesar_edicion_ruta, name='procesar_edicion_ruta'),
]



