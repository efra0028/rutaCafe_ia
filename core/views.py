from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db.models import Avg, Count
from django.conf import settings
import json
import math
import random
import mimetypes
from datetime import datetime
from .models import (
    Cafeteria, Recorrido, RecorridoUsuario, Comentario, 
    MeGusta, PerfilUsuario, TipoCafe, Producto, DuenoCafeteria
)
from .forms import RegistroForm, PerfilForm, LoginForm, DuenoCafeteriaForm


def validar_imagen(archivo):
    """Valida que el archivo sea una imagen válida"""
    if not archivo:
        return True  # Permitir archivos vacíos (opcional)
    
    # Obtener extensión del archivo
    nombre = archivo.name.lower()
    extensiones_permitidas = getattr(settings, 'ALLOWED_IMAGE_EXTENSIONS', [
        'jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'tif',
        'webp', 'avif', 'svg', 'ico', 'heic', 'heif'
    ])
    
    # Validar extensión
    extension = nombre.split('.')[-1] if '.' in nombre else ''
    if extension not in extensiones_permitidas:
        return False
    
    # Validar tipo MIME
    tipo_mime, _ = mimetypes.guess_type(nombre)
    if tipo_mime and not tipo_mime.startswith('image/'):
        return False
    
    # Validar tamaño (10MB máximo)
    if archivo.size > 10 * 1024 * 1024:
        return False
    
    return True


def home(request):
    """Vista principal que muestra el mapa y las cafeterías"""
    cafeterias = Cafeteria.objects.all()
    
    # Obtener todos los recorridos activos
    recorridos_disponibles = list(Recorrido.objects.filter(activo=True))
    
    # Seleccionar 2 recorridos aleatorios que cambien cada semana
    # Usar el número de semana del año como semilla para mantener consistencia
    semana_actual = datetime.now().isocalendar()[1]  # Número de semana del año
    year_actual = datetime.now().year
    semilla = semana_actual + year_actual * 100  # Semilla única por semana y año
    
    # Establecer la semilla para reproducibilidad semanal
    random.seed(semilla)
    
    # Seleccionar hasta 2 recorridos aleatorios
    recorridos = []
    if len(recorridos_disponibles) >= 2:
        recorridos = random.sample(recorridos_disponibles, 2)
    elif len(recorridos_disponibles) == 1:
        recorridos = recorridos_disponibles
    # Si no hay recorridos, la lista queda vacía
    
    # Preparar datos de cafeterías para el mapa JavaScript
    cafeterias_json = []
    for cafeteria in cafeterias:
        cafeterias_json.append({
            'id': cafeteria.id,
            'nombre': cafeteria.nombre,
            'descripcion': cafeteria.descripcion,
            'direccion': cafeteria.direccion,
            'latitud': float(cafeteria.latitud),
            'longitud': float(cafeteria.longitud),
            'telefono': cafeteria.telefono,
            'horario': cafeteria.horario,
            'precio_promedio': float(cafeteria.precio_promedio),
            'wifi': cafeteria.wifi,
            'terraza': cafeteria.terraza,
            'estacionamiento': cafeteria.estacionamiento,
            'zona': cafeteria.zona,
            'calificacion_promedio': float(cafeteria.calificacion_promedio),
            'total_calificaciones': cafeteria.total_calificaciones,
            'total_me_gusta': cafeteria.total_me_gusta,
        })
    
    context = {
        'cafeterias': cafeterias,
        'recorridos': recorridos,
        'cafeterias_json': json.dumps(cafeterias_json),
        'MAPBOX_ACCESS_TOKEN': getattr(settings, 'MAPBOX_ACCESS_TOKEN', ''),
        'semana_actual': semana_actual,  # Para debug si es necesario
    }
    return render(request, 'core/home.html', context)


def registro(request):
    """Vista para el registro de usuarios"""
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Crear perfil de usuario
            perfil = PerfilUsuario.objects.create(
                user=user,
                genero=form.cleaned_data['genero'],
                edad=form.cleaned_data['edad'],
                ciudad=form.cleaned_data['ciudad'],
                pais=form.cleaned_data['pais']
            )
            login(request, user)
            messages.success(request, '¡Registro exitoso! Ya puedes usar el asistente virtual para crear tu ruta de cafeterías.')
            return redirect('home')
    else:
        form = RegistroForm()
    
    return render(request, 'core/registro.html', {'form': form})


@login_required
def perfil(request):
    """Vista para ver y editar el perfil del usuario"""
    try:
        perfil = request.user.perfilusuario
    except PerfilUsuario.DoesNotExist:
        return redirect('completar_perfil')
    
    if request.method == 'POST':
        form = PerfilForm(request.POST, instance=perfil)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil actualizado correctamente')
            return redirect('perfil')
    else:
        form = PerfilForm(instance=perfil)
    
    return render(request, 'core/perfil.html', {'form': form})


@login_required
def completar_perfil(request):
    """Vista para completar el perfil si no existe"""
    if request.method == 'POST':
        form = PerfilForm(request.POST)
        if form.is_valid():
            perfil = form.save(commit=False)
            perfil.user = request.user
            perfil.save()
            messages.success(request, 'Perfil completado correctamente')
            return redirect('home')
    else:
        form = PerfilForm()
    
    return render(request, 'core/completar_perfil.html', {'form': form})


def cafeteria_detail(request, cafeteria_id):
    """Vista detalle de una cafetería"""
    cafeteria = get_object_or_404(Cafeteria, id=cafeteria_id)
    comentarios = Comentario.objects.filter(cafeteria=cafeteria).order_by('-fecha_creacion')
    productos = Producto.objects.filter(cafeteria=cafeteria, disponible=True)[:6]
    
    # Obtener horarios detallados
    horarios_detallados = cafeteria.get_horarios_detallados()
    horario_hoy = cafeteria.get_horario_hoy()
    
    # Verificar si el usuario ya le dio me gusta
    me_gusta = False
    if request.user.is_authenticated:
        me_gusta = MeGusta.objects.filter(
            usuario=request.user, 
            cafeteria=cafeteria
        ).exists()
    
    context = {
        'cafeteria': cafeteria,
        'comentarios': comentarios,
        'productos': productos,
        'me_gusta': me_gusta,
        'horarios_detallados': horarios_detallados,
        'horario_hoy': horario_hoy,
        'MAPBOX_ACCESS_TOKEN': settings.MAPBOX_ACCESS_TOKEN,
    }
    return render(request, 'core/cafeteria_detail.html', context)


@login_required
@require_http_methods(["POST"])
def toggle_me_gusta(request, cafeteria_id):
    """Toggle para me gusta de cafetería"""
    cafeteria = get_object_or_404(Cafeteria, id=cafeteria_id)
    
    me_gusta, created = MeGusta.objects.get_or_create(
        usuario=request.user,
        cafeteria=cafeteria
    )
    
    if not created:
        me_gusta.delete()
        cafeteria.total_me_gusta -= 1
        liked = False
    else:
        cafeteria.total_me_gusta += 1
        liked = True
    
    cafeteria.save()
    
    return JsonResponse({
        'liked': liked,
        'total_likes': cafeteria.total_me_gusta
    })


@login_required
@require_http_methods(["POST"])
def agregar_comentario(request, cafeteria_id):
    """Agregar comentario a una cafetería"""
    cafeteria = get_object_or_404(Cafeteria, id=cafeteria_id)
    
    comentario_texto = request.POST.get('comentario')
    calificacion = int(request.POST.get('calificacion'))
    
    if comentario_texto and calificacion:
        comentario = Comentario.objects.create(
            usuario=request.user,
            cafeteria=cafeteria,
            comentario=comentario_texto,
            calificacion=calificacion
        )
        
        # Actualizar calificación promedio
        promedio = Comentario.objects.filter(cafeteria=cafeteria).aggregate(
            avg=Avg('calificacion')
        )['avg']
        cafeteria.calificacion_promedio = round(promedio, 2)
        cafeteria.total_calificaciones = Comentario.objects.filter(cafeteria=cafeteria).count()
        cafeteria.save()
        
        return JsonResponse({
            'success': True,
            'comentario': comentario.comentario,
            'calificacion': comentario.calificacion,
            'usuario': comentario.usuario.username,
            'fecha': comentario.fecha_creacion.strftime('%d/%m/%Y %H:%M'),
            'promedio': float(cafeteria.calificacion_promedio),
            'total_calificaciones': cafeteria.total_calificaciones
        })
    
    return JsonResponse({'success': False})


@login_required
def iniciar_recorrido(request, recorrido_id):
    """Iniciar un recorrido"""
    recorrido = get_object_or_404(Recorrido, id=recorrido_id)
    
    # Verificar si ya tiene un recorrido activo
    recorrido_activo = RecorridoUsuario.objects.filter(
        usuario=request.user,
        estado__in=['P', 'E']
    ).first()
    
    if recorrido_activo:
        messages.warning(request, 'Ya tienes un recorrido en progreso')
        return redirect('recorrido_detail', recorrido_id=recorrido_activo.id)
    
    # Crear nuevo recorrido
    recorrido_usuario = RecorridoUsuario.objects.create(
        usuario=request.user,
        recorrido=recorrido,
        estado='P'
    )
    
    return redirect('recorrido_detail', recorrido_id=recorrido_usuario.id)


@login_required
def recorrido_detail(request, recorrido_id):
    """Detalle de un recorrido del usuario"""
    recorrido_usuario = get_object_or_404(RecorridoUsuario, id=recorrido_id, usuario=request.user)
    cafeterias_qs = recorrido_usuario.recorrido.cafeterias.all().order_by('recorridocafeteria__orden')
    visitadas_ids = set(recorrido_usuario.cafeterias_visitadas.values_list('id', flat=True))

    cafeterias_data = []
    for cafe in cafeterias_qs:
        try:
            lat = float(cafe.latitud)
            lng = float(cafe.longitud)
        except (TypeError, ValueError):
            continue

        cafeterias_data.append({
            'id': cafe.id,
            'nombre': cafe.nombre,
            'direccion': cafe.direccion,
            'lat': lat,
            'lng': lng,
            'visitada': cafe.id in visitadas_ids,
        })

    context = {
        'recorrido_usuario': recorrido_usuario,
        'cafeterias': cafeterias_qs,
        'cafeterias_data': cafeterias_data,
        'total_cafeterias': cafeterias_qs.count(),
        'cafeterias_visitadas': recorrido_usuario.cafeterias_visitadas.count(),
        'cafeterias_restantes': cafeterias_qs.count() - recorrido_usuario.cafeterias_visitadas.count(),
        'MAPBOX_ACCESS_TOKEN': settings.MAPBOX_ACCESS_TOKEN,
    }
    return render(request, 'core/recorrido_detail.html', context)


@login_required
@require_http_methods(["POST"])
def marcar_cafeteria_visitada(request, recorrido_id, cafeteria_id):
    """Marcar una cafetería como visitada en el recorrido"""
    recorrido_usuario = get_object_or_404(RecorridoUsuario, id=recorrido_id, usuario=request.user)
    cafeteria = get_object_or_404(Cafeteria, id=cafeteria_id)
    
    recorrido_usuario.cafeterias_visitadas.add(cafeteria)
    
    # Verificar si completó el recorrido
    total_cafeterias = recorrido_usuario.recorrido.cafeterias.count()
    visitadas = recorrido_usuario.cafeterias_visitadas.count()
    
    if visitadas >= total_cafeterias:
        recorrido_usuario.estado = 'C'
        recorrido_usuario.save()
        return JsonResponse({
            'completado': True,
            'mensaje': '¡Felicidades! Has completado el recorrido'
        })
    
    return JsonResponse({
        'completado': False,
        'visitadas': visitadas,
        'total': total_cafeterias
    })


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calcula distancia Haversine en kilómetros entre dos coordenadas."""
    R = 6371.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


@require_http_methods(["GET"])
def cafeterias_cercanas(request):
    """Devuelve las 4 cafeterías más cercanas a una ubicación dada (lat, lng)."""
    try:
        lat = float(request.GET.get('lat'))
        lng = float(request.GET.get('lng'))
    except (TypeError, ValueError):
        return JsonResponse({'success': False, 'error': 'Parámetros lat/lng inválidos'}, status=400)

    tipo = request.GET.get('tipo')  # opcional

    cafeterias_qs = Cafeteria.objects.all()
    if tipo:
        cafeterias_qs = cafeterias_qs.filter(cafeteriatipocafe__tipo_cafe__nombre__iexact=tipo).distinct()

    cafeterias_list = []
    for c in cafeterias_qs:
        try:
            d = _haversine_km(float(c.latitud), float(c.longitud), lat, lng)
        except Exception:
            continue
        cafeterias_list.append((d, c))

    cafeterias_list.sort(key=lambda x: x[0])
    top4 = [c for _, c in cafeterias_list[:4]]

    return JsonResponse({
        'success': True,
        'cafeterias': [
            {
                'id': c.id,
                'nombre': c.nombre,
                'direccion': c.direccion,
                'latitud': float(c.latitud),
                'longitud': float(c.longitud),
                'calificacion': float(c.calificacion_promedio),
                'me_gusta': c.total_me_gusta,
            } for c in top4
        ]
    })


@require_http_methods(["GET"])
def ordenar_ruta_por_cercania(request):
    """Ordena una lista de cafeterías por cercanía incremental desde (lat,lng). Greedy NN."""
    try:
        lat = float(request.GET.get('lat'))
        lng = float(request.GET.get('lng'))
        ids = request.GET.getlist('ids')
        ids = [int(x) for x in ids]
    except Exception:
        return JsonResponse({'success': False, 'error': 'Parámetros inválidos'}, status=400)

    cafes = list(Cafeteria.objects.filter(id__in=ids))
    if not cafes:
        return JsonResponse({'success': False, 'error': 'Sin cafeterías'}, status=400)

    ruta = []
    current_lat, current_lng = lat, lng
    remaining = cafes[:]
    while remaining:
        remaining.sort(key=lambda c: _haversine_km(current_lat, current_lng, float(c.latitud), float(c.longitud)))
        nxt = remaining.pop(0)
        ruta.append(nxt)
        current_lat, current_lng = float(nxt.latitud), float(nxt.longitud)

    return JsonResponse({
        'success': True,
        'orden': [c.id for c in ruta]
    })


def estadisticas(request):
    """Vista de estadísticas generales"""
    total_cafeterias = Cafeteria.objects.count()
    total_recorridos = RecorridoUsuario.objects.count()
    recorridos_completados = RecorridoUsuario.objects.filter(estado='C').count()
    
    # Top 5 cafeterías más populares
    top_cafeterias = Cafeteria.objects.annotate(
        total_me_gusta_count=Count('megusta')
    ).order_by('-total_me_gusta_count')[:5]
    
    context = {
        'total_cafeterias': total_cafeterias,
        'total_recorridos': total_recorridos,
        'recorridos_completados': recorridos_completados,
        'top_cafeterias': top_cafeterias,
    }
    return render(request, 'core/estadisticas.html', context)


def user_login(request):
    """Vista para iniciar sesión del usuario"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'¡Bienvenido {user.first_name or user.username}!')
                
                # Redirigir según el tipo de usuario
                if user.is_superuser:
                    return redirect('/admin/')
                elif hasattr(user, 'duenocafeteria') and user.duenocafeteria.esta_aprobado:
                    return redirect('panel_dueno')
                else:
                    return redirect('home')
            else:
                messages.error(request, 'Nombre de usuario o contraseña incorrectos.')
    else:
        form = LoginForm()
    
    return render(request, 'core/login.html', {'form': form})


def user_logout(request):
    """Vista para cerrar sesión del usuario"""
    logout(request)
    return redirect('home')


def registro_dueno(request):
    """Vista para registro de dueños de cafeterías"""
    if request.method == 'POST':
        form = DuenoCafeteriaForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(
                request, 
                f'¡Registro enviado exitosamente! Tu solicitud ha sido enviada al administrador para revisión. '
                f'Recibirás un email de confirmación cuando sea aprobada.'
            )
            
            # Enviar notificación al administrador
            from django.core.mail import send_mail
            from django.conf import settings
            
            try:
                # Obtener todos los administradores
                admins = User.objects.filter(is_superuser=True)
                admin_emails = [admin.email for admin in admins if admin.email]
                
                if admin_emails:
                    send_mail(
                        subject='Nueva solicitud de registro de cafetería - RutaCafé',
                        message=f'''
Una nueva cafetería solicita registrarse en RutaCafé:

Dueño: {user.get_full_name()}
Email: {user.email}
Cafetería: {form.cleaned_data['nombre_cafeteria']}
Ubicación: {form.cleaned_data['direccion_cafeteria']}

Por favor, revisa la solicitud en el panel de administración.
                        ''',
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=admin_emails,
                        fail_silently=True,
                    )
            except Exception as e:
                print(f"Error enviando email: {e}")
            
            return redirect('home')
    else:
        form = DuenoCafeteriaForm()
    
    return render(request, 'core/registro_dueno.html', {'form': form})


# ==================== VISTAS PARA DUEÑOS DE CAFETERÍAS ====================

def es_dueno_cafeteria(user):
    """Verificar si el usuario es dueño de una cafetería aprobada"""
    return (hasattr(user, 'duenocafeteria') and 
            user.duenocafeteria.esta_aprobado and 
            user.duenocafeteria.cafeteria is not None)


@login_required
def panel_dueno(request):
    """Panel principal para dueños de cafeterías"""
    if not es_dueno_cafeteria(request.user):
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('home')
    
    dueno = request.user.duenocafeteria
    cafeteria = dueno.cafeteria
    
    # Estadísticas de la cafetería
    total_productos = cafeteria.productos.count()
    total_comentarios = cafeteria.comentario_set.count()
    total_me_gusta = cafeteria.megusta_set.count()
    calificacion_promedio = cafeteria.calificacion_promedio
    
    # Comentarios recientes
    comentarios_recientes = cafeteria.comentario_set.order_by('-fecha_creacion')[:5]
    
    # Productos sin imagen
    productos_sin_imagen = cafeteria.productos.filter(imagen__isnull=True).count()
    
    context = {
        'dueno': dueno,
        'cafeteria': cafeteria,
        'total_productos': total_productos,
        'total_comentarios': total_comentarios,
        'total_me_gusta': total_me_gusta,
        'calificacion_promedio': calificacion_promedio,
        'comentarios_recientes': comentarios_recientes,
        'productos_sin_imagen': productos_sin_imagen,
    }
    
    return render(request, 'dueno/panel.html', context)


@login_required
def gestionar_productos(request):
    """Vista para gestionar productos de la cafetería"""
    if not es_dueno_cafeteria(request.user):
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('home')
    
    dueno = request.user.duenocafeteria
    cafeteria = dueno.cafeteria
    productos = cafeteria.productos.all().order_by('nombre')
    
    context = {
        'dueno': dueno,
        'cafeteria': cafeteria,
        'productos': productos,
    }
    
    return render(request, 'dueno/productos.html', context)


@login_required
def agregar_producto(request):
    """Vista para agregar un nuevo producto"""
    if not es_dueno_cafeteria(request.user):
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('home')
    
    dueno = request.user.duenocafeteria
    cafeteria = dueno.cafeteria
    
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        precio = request.POST.get('precio')
        imagen = request.FILES.get('imagen')
        
        if nombre and descripcion and precio:
            # Validar imagen si se proporciona
            if imagen and not validar_imagen(imagen):
                messages.error(request, 'Formato de imagen no válido. Formatos permitidos: JPG, PNG, WebP, AVIF, SVG, etc.')
                return render(request, 'dueno/agregar_producto.html', {
                    'dueno': dueno,
                    'cafeteria': cafeteria,
                })
            
            try:
                producto = Producto.objects.create(
                    nombre=nombre,
                    descripcion=descripcion,
                    precio=float(precio),
                    cafeteria=cafeteria,
                    imagen=imagen
                )
                messages.success(request, f'Producto "{nombre}" agregado exitosamente.')
                return redirect('gestionar_productos')
            except ValueError:
                messages.error(request, 'El precio debe ser un número válido.')
        else:
            messages.error(request, 'Todos los campos son obligatorios.')
    
    context = {
        'dueno': dueno,
        'cafeteria': cafeteria,
    }
    
    return render(request, 'dueno/agregar_producto.html', context)


@login_required
def editar_producto(request, producto_id):
    """Vista para editar un producto existente"""
    if not es_dueno_cafeteria(request.user):
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('home')
    
    dueno = request.user.duenocafeteria
    cafeteria = dueno.cafeteria
    
    # Verificar que el producto pertenece a la cafetería del dueño
    try:
        producto = Producto.objects.get(id=producto_id, cafeteria=cafeteria)
    except Producto.DoesNotExist:
        messages.error(request, 'Producto no encontrado.')
        return redirect('gestionar_productos')
    
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        precio = request.POST.get('precio')
        imagen = request.FILES.get('imagen')
        
        if nombre and descripcion and precio:
            # Validar imagen si se proporciona
            if imagen and not validar_imagen(imagen):
                messages.error(request, 'Formato de imagen no válido. Formatos permitidos: JPG, PNG, WebP, AVIF, SVG, etc.')
                return render(request, 'dueno/editar_producto.html', {
                    'dueno': dueno,
                    'cafeteria': cafeteria,
                    'producto': producto,
                })
            
            try:
                producto.nombre = nombre
                producto.descripcion = descripcion
                producto.precio = float(precio)
                
                # Manejar actualización de imagen
                if imagen:
                    # Eliminar la imagen anterior si existe
                    if producto.imagen:
                        import os
                        if os.path.isfile(producto.imagen.path):
                            os.remove(producto.imagen.path)
                    # Asignar la nueva imagen
                    producto.imagen = imagen
                
                producto.save()
                
                messages.success(request, f'Producto "{nombre}" actualizado exitosamente.')
                return redirect('gestionar_productos')
            except ValueError:
                messages.error(request, 'El precio debe ser un número válido.')
        else:
            messages.error(request, 'Todos los campos son obligatorios.')
    
    context = {
        'cafeteria': cafeteria,
        'producto': producto,
    }
    
    return render(request, 'dueno/editar_producto.html', context)


@login_required
def eliminar_producto(request, producto_id):
    """Vista para eliminar un producto"""
    if not es_dueno_cafeteria(request.user):
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('home')
    
    dueno = request.user.duenocafeteria
    cafeteria = dueno.cafeteria
    
    # Verificar que el producto pertenece a la cafetería del dueño
    try:
        producto = Producto.objects.get(id=producto_id, cafeteria=cafeteria)
        nombre_producto = producto.nombre
        producto.delete()
        messages.success(request, f'Producto "{nombre_producto}" eliminado exitosamente.')
    except Producto.DoesNotExist:
        messages.error(request, 'Producto no encontrado.')
    
    return redirect('gestionar_productos')


@login_required
def editar_cafeteria(request):
    """Vista para editar información de la cafetería"""
    if not es_dueno_cafeteria(request.user):
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('home')
    
    dueno = request.user.duenocafeteria
    cafeteria = dueno.cafeteria
    
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        direccion = request.POST.get('direccion')
        telefono = request.POST.get('telefono')
        latitud = request.POST.get('latitud')
        longitud = request.POST.get('longitud')
        wifi = request.POST.get('wifi') == 'on'
        terraza = request.POST.get('terraza') == 'on'
        estacionamiento = request.POST.get('estacionamiento') == 'on'
        zona = request.POST.get('zona')
        imagen = request.FILES.get('imagen')
        
        if nombre and descripcion and direccion:
            # Validar imagen si se proporciona
            if imagen and not validar_imagen(imagen):
                messages.error(request, 'Formato de imagen no válido. Formatos permitidos: JPG, PNG, WebP, AVIF, SVG, etc.')
                return render(request, 'dueno/editar_cafeteria.html', {
                    'dueno': dueno,
                    'cafeteria': cafeteria,
                })
            
            # Actualizar información básica
            cafeteria.nombre = nombre
            cafeteria.descripcion = descripcion
            cafeteria.direccion = direccion
            cafeteria.telefono = telefono or ''
            cafeteria.wifi = wifi
            cafeteria.terraza = terraza
            cafeteria.estacionamiento = estacionamiento
            cafeteria.zona = zona or 'Centro'
            
            # Actualizar coordenadas si se proporcionan
            if latitud and longitud:
                try:
                    cafeteria.latitud = float(latitud)
                    cafeteria.longitud = float(longitud)
                    dueno.latitud = float(latitud)
                    dueno.longitud = float(longitud)
                except ValueError:
                    messages.error(request, 'Las coordenadas deben ser números válidos.')
                    return render(request, 'dueno/editar_cafeteria.html', {
                        'dueno': dueno,
                        'cafeteria': cafeteria,
                    })
            
            # Manejar actualización de imagen
            if imagen:
                # Eliminar la imagen anterior si existe
                if cafeteria.imagen:
                    import os
                    if os.path.isfile(cafeteria.imagen.path):
                        os.remove(cafeteria.imagen.path)
                # Asignar la nueva imagen
                cafeteria.imagen = imagen
            
            cafeteria.save()
            
            # Actualizar horarios detallados por día
            from .models import HorarioCafeteria
            for dia in range(7):  # 0=Lunes, 6=Domingo
                cerrado = request.POST.get(f'cerrado_{dia}') == 'on'
                hora_apertura = request.POST.get(f'hora_apertura_{dia}')
                hora_cierre = request.POST.get(f'hora_cierre_{dia}')
                
                # Obtener o crear el horario para este día
                horario, created = HorarioCafeteria.objects.get_or_create(
                    cafeteria=cafeteria,
                    dia_semana=dia
                )
                
                horario.cerrado = cerrado
                if not cerrado and hora_apertura and hora_cierre:
                    horario.hora_apertura = hora_apertura
                    horario.hora_cierre = hora_cierre
                elif cerrado:
                    horario.hora_apertura = None
                    horario.hora_cierre = None
                
                horario.save()
            
            # También actualizar en el perfil del dueño
            dueno.nombre_cafeteria = nombre
            dueno.descripcion_cafeteria = descripcion
            dueno.direccion_cafeteria = direccion
            dueno.telefono_cafeteria = telefono or ''
            dueno.save()
            
            messages.success(request, 'Información de la cafetería actualizada exitosamente.')
            return redirect('panel_dueno')
        else:
            messages.error(request, 'Los campos nombre, descripción y dirección son obligatorios.')
    
    # Obtener horarios existentes
    from .models import HorarioCafeteria
    horarios_dict = {}
    for horario in HorarioCafeteria.objects.filter(cafeteria=cafeteria):
        horarios_dict[horario.dia_semana] = horario
    
    # Lista de días de la semana
    dias_semana = [
        (0, 'Lunes'),
        (1, 'Martes'),
        (2, 'Miércoles'),
        (3, 'Jueves'),
        (4, 'Viernes'),
        (5, 'Sábado'),
        (6, 'Domingo'),
    ]
    
    context = {
        'dueno': dueno,
        'cafeteria': cafeteria,
        'horarios_dict': horarios_dict,
        'dias_semana': dias_semana,
        'MAPBOX_ACCESS_TOKEN': getattr(settings, 'MAPBOX_ACCESS_TOKEN', ''),
    }
    
    return render(request, 'dueno/editar_cafeteria.html', context)