from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.contrib import messages
from django.utils import timezone
from .models import (
    PerfilUsuario, Cafeteria, TipoCafe, CafeteriaTipoCafe,
    Recorrido, RecorridoCafeteria, RecorridoUsuario, 
    Comentario, MeGusta, HorarioCafeteria, DuenoCafeteria
)


@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ['user', 'genero', 'edad', 'ciudad', 'pais', 'fecha_registro']
    list_filter = ['genero', 'ciudad', 'pais']
    search_fields = ['user__first_name', 'user__last_name', 'user__email']


class CafeteriaTipoCafeInline(admin.TabularInline):
    model = CafeteriaTipoCafe
    extra = 1


class HorarioCafeteriaInline(admin.TabularInline):
    model = HorarioCafeteria
    extra = 0
    ordering = ['dia_semana']


@admin.register(Cafeteria)
class CafeteriaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'direccion', 'calificacion_promedio', 'total_calificaciones', 'total_me_gusta']
    list_filter = ['fecha_creacion']
    search_fields = ['nombre', 'direccion']
    inlines = [HorarioCafeteriaInline, CafeteriaTipoCafeInline]


@admin.register(HorarioCafeteria)
class HorarioCafeteriaAdmin(admin.ModelAdmin):
    list_display = ['cafeteria', 'get_dia_semana_display', 'hora_apertura', 'hora_cierre', 'cerrado']
    list_filter = ['dia_semana', 'cerrado', 'cafeteria']
    search_fields = ['cafeteria__nombre']
    ordering = ['cafeteria', 'dia_semana']


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


@admin.register(DuenoCafeteria)
class DuenoCafeteriaAdmin(admin.ModelAdmin):
    list_display = ['user', 'nombre_cafeteria', 'estado', 'fecha_solicitud', 'aprobado_por', 'acciones']
    list_filter = ['estado', 'fecha_solicitud', 'zona']
    search_fields = ['user__first_name', 'user__last_name', 'user__email', 'nombre_cafeteria']
    readonly_fields = ['fecha_solicitud', 'fecha_aprobacion']
    
    fieldsets = (
        ('Información del Usuario', {
            'fields': ('user', 'telefono', 'cedula', 'direccion_personal')
        }),
        ('Información de la Cafetería', {
            'fields': ('nombre_cafeteria', 'descripcion_cafeteria', 'direccion_cafeteria', 
                      'telefono_cafeteria', 'horario_atencion', 'zona')
        }),
        ('Ubicación', {
            'fields': ('latitud', 'longitud'),
            'classes': ('collapse',)
        }),
        ('Características', {
            'fields': ('wifi', 'terraza', 'estacionamiento')
        }),
        ('Estado de Aprobación', {
            'fields': ('estado', 'comentarios_admin', 'aprobado_por', 'fecha_solicitud', 'fecha_aprobacion')
        }),
        ('Cafetería Asociada', {
            'fields': ('cafeteria',),
            'classes': ('collapse',)
        })
    )
    
    def acciones(self, obj):
        if obj.estado == 'pendiente':
            return format_html(
                '<a class="button" href="{}">Aprobar</a> '
                '<a class="button" href="{}">Rechazar</a>',
                reverse('admin:aprobar_dueno', args=[obj.pk]),
                reverse('admin:rechazar_dueno', args=[obj.pk]),
            )
        elif obj.estado == 'aprobado':
            return format_html('<span style="color: green;">✓ Aprobado</span>')
        else:
            return format_html('<span style="color: red;">✗ Rechazado</span>')
    
    acciones.short_description = 'Acciones'
    
    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('aprobar/<int:pk>/', self.admin_site.admin_view(self.aprobar_dueno), name='aprobar_dueno'),
            path('rechazar/<int:pk>/', self.admin_site.admin_view(self.rechazar_dueno), name='rechazar_dueno'),
        ]
        return custom_urls + urls
    
    def aprobar_dueno(self, request, pk):
        dueno = DuenoCafeteria.objects.get(pk=pk)
        
        # Activar el usuario
        dueno.user.is_active = True
        dueno.user.save()
        
        # Crear la cafetería
        cafeteria = Cafeteria.objects.create(
            nombre=dueno.nombre_cafeteria,
            descripcion=dueno.descripcion_cafeteria,
            direccion=dueno.direccion_cafeteria,
            telefono=dueno.telefono_cafeteria,
            horario=dueno.horario_atencion,
            latitud=dueno.latitud or -19.0336,  # Coordenadas por defecto de Sucre
            longitud=dueno.longitud or -65.2631,
            wifi=dueno.wifi,
            terraza=dueno.terraza,
            estacionamiento=dueno.estacionamiento,
            zona=dueno.zona,
        )
        
        # Actualizar el dueño
        dueno.estado = 'aprobado'
        dueno.fecha_aprobacion = timezone.now()
        dueno.aprobado_por = request.user
        dueno.cafeteria = cafeteria
        dueno.save()
        
        # Enviar email de aprobación
        try:
            from django.core.mail import send_mail
            send_mail(
                subject='¡Tu cafetería ha sido aprobada! - RutaCafé',
                message=f'''
¡Hola {dueno.user.get_full_name()}!

¡Excelentes noticias! Tu cafetería "{dueno.nombre_cafeteria}" ha sido aprobada y ya forma parte de RutaCafé.

Ya puedes iniciar sesión en la plataforma con tus credenciales:
- Usuario: {dueno.user.username}
- Contraseña: La que registraste

Próximamente podrás gestionar tus productos y servicios.

¡Bienvenido a RutaCafé!
                ''',
                from_email='admin@rutacafe.com',
                recipient_list=[dueno.user.email],
                fail_silently=True,
            )
        except Exception as e:
            print(f"Error enviando email: {e}")
        
        messages.success(request, f'La cafetería "{dueno.nombre_cafeteria}" ha sido aprobada exitosamente.')
        return self.response_post_save_change(request, dueno)
    
    def rechazar_dueno(self, request, pk):
        dueno = DuenoCafeteria.objects.get(pk=pk)
        dueno.estado = 'rechazado'
        dueno.save()
        
        # Enviar email de rechazo
        try:
            from django.core.mail import send_mail
            send_mail(
                subject='Actualización de tu solicitud - RutaCafé',
                message=f'''
Hola {dueno.user.get_full_name()},

Lamentamos informarte que tu solicitud para registrar la cafetería "{dueno.nombre_cafeteria}" no ha sido aprobada en este momento.

Si tienes preguntas sobre esta decisión, puedes contactarnos respondiendo a este email.

Atentamente,
Equipo RutaCafé
                ''',
                from_email='admin@rutacafe.com',
                recipient_list=[dueno.user.email],
                fail_silently=True,
            )
        except Exception as e:
            print(f"Error enviando email: {e}")
        
        messages.warning(request, f'La solicitud de "{dueno.nombre_cafeteria}" ha sido rechazada.')
        return self.response_post_save_change(request, dueno)