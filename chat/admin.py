from django.contrib import admin
from .models import Conversacion, Mensaje, PreferenciaUsuario


class MensajeInline(admin.TabularInline):
    model = Mensaje
    extra = 0
    readonly_fields = ['timestamp']


@admin.register(Conversacion)
class ConversacionAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'fecha_inicio', 'activa']
    list_filter = ['activa', 'fecha_inicio']
    search_fields = ['usuario__username']
    inlines = [MensajeInline]


@admin.register(Mensaje)
class MensajeAdmin(admin.ModelAdmin):
    list_display = ['conversacion', 'tipo', 'contenido_short', 'timestamp']
    list_filter = ['tipo', 'timestamp']
    search_fields = ['contenido', 'conversacion__usuario__username']
    
    def contenido_short(self, obj):
        return obj.contenido[:50] + "..." if len(obj.contenido) > 50 else obj.contenido
    contenido_short.short_description = 'Contenido'


@admin.register(PreferenciaUsuario)
class PreferenciaUsuarioAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'tipo_cafe_preferido', 'ambiente_preferido', 'presupuesto_maximo']
    search_fields = ['usuario__username']