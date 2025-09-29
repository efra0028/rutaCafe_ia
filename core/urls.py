from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('registro/', views.registro, name='registro'),
    path('registro-dueno/', views.registro_dueno, name='registro_dueno'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('perfil/', views.perfil, name='perfil'),
    path('completar-perfil/', views.completar_perfil, name='completar_perfil'),
    
    # URLs para dueños de cafeterías
    path('panel-dueno/', views.panel_dueno, name='panel_dueno'),
    path('productos/', views.gestionar_productos, name='gestionar_productos'),
    path('productos/agregar/', views.agregar_producto, name='agregar_producto'),
    path('productos/editar/<int:producto_id>/', views.editar_producto, name='editar_producto'),
    path('productos/eliminar/<int:producto_id>/', views.eliminar_producto, name='eliminar_producto'),
    path('cafeteria/editar/', views.editar_cafeteria, name='editar_cafeteria'),
    
    # URLs existentes
    path('cafeteria/<int:cafeteria_id>/', views.cafeteria_detail, name='cafeteria_detail'),
    path('cafeteria/<int:cafeteria_id>/me-gusta/', views.toggle_me_gusta, name='toggle_me_gusta'),
    path('cafeteria/<int:cafeteria_id>/comentario/', views.agregar_comentario, name='agregar_comentario'),
    path('recorrido/<int:recorrido_id>/iniciar/', views.iniciar_recorrido, name='iniciar_recorrido'),
    path('mi-recorrido/<int:recorrido_id>/', views.recorrido_detail, name='recorrido_detail'),
    path('mi-recorrido/<int:recorrido_id>/visitar/<int:cafeteria_id>/', 
         views.marcar_cafeteria_visitada, name='marcar_cafeteria_visitada'),
    path('estadisticas/', views.estadisticas, name='estadisticas'),
    path('api/cercanas/', views.cafeterias_cercanas, name='cafeterias_cercanas'),
    path('api/ordenar-ruta/', views.ordenar_ruta_por_cercania, name='ordenar_ruta_por_cercania'),
]
