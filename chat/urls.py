from django.urls import path
from . import views

urlpatterns = [
    path('', views.chat_view, name='chat'),
    path('enviar-mensaje/', views.enviar_mensaje, name='enviar_mensaje'),
    path('crear-recorrido/', views.crear_recorrido_chat, name='crear_recorrido_chat'),
    path('nueva-conversacion/', views.nueva_conversacion, name='nueva_conversacion'),
    path('generar-audio/', views.generar_audio, name='generar_audio'),
    path('obtener-voces/', views.obtener_voces, name='obtener_voces'),
]
