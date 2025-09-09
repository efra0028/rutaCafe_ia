from django.contrib import admin
from .models import (
    PerfilUsuario, Cafeteria, TipoCafe, CafeteriaTipoCafe,
    Recorrido, RecorridoCafeteria, RecorridoUsuario, 
    Comentario, MeGusta
)


@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ['user', 'genero', 'edad', 'ciudad', 'pais', 'fecha_registro']
    list_filter = ['genero', 'ciudad', 'pais']
    search_fields = ['user__first_name', 'user__last_name', 'user__email']


class CafeteriaTipoCafeInline(admin.TabularInline):
    model = CafeteriaTipoCafe
    extra = 1


@admin.register(Cafeteria)
class CafeteriaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'direccion', 'calificacion_promedio', 'total_calificaciones', 'total_me_gusta']
    list_filter = ['fecha_creacion']
    search_fields = ['nombre', 'direccion']
    inlines = [CafeteriaTipoCafeInline]


@admin.register(TipoCafe)
class TipoCafeAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'descripcion']
    search_fields = ['nombre']


class RecorridoCafeteriaInline(admin.TabularInline):
    model = RecorridoCafeteria
    extra = 1


@admin.register(Recorrido)
class RecorridoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'duracion_estimada', 'distancia_total', 'activo']
    list_filter = ['activo', 'fecha_creacion']
    inlines = [RecorridoCafeteriaInline]


@admin.register(RecorridoUsuario)
class RecorridoUsuarioAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'recorrido', 'estado', 'fecha_inicio', 'fecha_completado']
    list_filter = ['estado', 'fecha_inicio']
    search_fields = ['usuario__username', 'recorrido__nombre']


@admin.register(Comentario)
class ComentarioAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'cafeteria', 'calificacion', 'fecha_creacion']
    list_filter = ['calificacion', 'fecha_creacion']
    search_fields = ['usuario__username', 'cafeteria__nombre']


@admin.register(MeGusta)
class MeGustaAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'cafeteria', 'fecha_creacion']
    list_filter = ['fecha_creacion']
    search_fields = ['usuario__username', 'cafeteria__nombre']