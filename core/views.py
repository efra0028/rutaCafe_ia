from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
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
from datetime import datetime
from .models import (
    Cafeteria, Recorrido, RecorridoUsuario, Comentario, 
    MeGusta, PerfilUsuario, TipoCafe
)
from .forms import RegistroForm, PerfilForm


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
        'me_gusta': me_gusta,
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
    
    context = {
        'recorrido_usuario': recorrido_usuario,
        'cafeterias': recorrido_usuario.recorrido.cafeterias.all().order_by('recorridocafeteria__orden'),
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