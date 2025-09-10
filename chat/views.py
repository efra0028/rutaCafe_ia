from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import openai
from django.conf import settings
from .models import Conversacion, Mensaje, PreferenciaUsuario
from core.models import Cafeteria, TipoCafe, Recorrido
from core.voice_service import voice_service
import random


def get_openai_response(user_message, conversacion):
    """Obtener respuesta del chatbot usando OpenAI o respuestas predefinidas"""
    try:
        # Verificar que la API key esté configurada
        if not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY == 'sk-proj-tu-clave-aqui':
            return get_fallback_response(user_message, conversacion)
        
        # Construir contexto de la conversación
        mensajes_anteriores = conversacion.mensajes.all().order_by('timestamp')[:10]
        
        messages = [
            {
                "role": "system", 
                "content": """Eres un asistente virtual especializado en cafeterías de Sucre, Bolivia. 
                Tu función principal es ayudar a los usuarios a crear rutas personalizadas de exactamente 4 cafeterías 
                basadas en sus preferencias de café y ubicación.
                
                Tipos de café disponibles en Sucre:
                - Americano: Café negro fuerte y simple
                - Espresso: Café concentrado y intenso
                - Cappuccino: Café con leche espumosa
                - Latte: Café con mucha leche cremosa
                - Mocha: Café con chocolate
                - Frappé: Café frío batido
                - Macchiato: Espresso con un toque de leche
                - Cortado: Café con un poco de leche
                
                Proceso:
                1. Pregunta qué tipo de café prefiere el usuario
                2. Basándote en su respuesta, selecciona 4 cafeterías de Sucre
                3. Explica por qué elegiste esas cafeterías
                4. Menciona que se creará una ruta optimizada en el mapa
                
                Sé amigable, conversacional y enfócate en crear la mejor experiencia de café en Sucre."""
            }
        ]
        
        # Agregar mensajes anteriores
        for msg in mensajes_anteriores:
            role = "user" if msg.tipo == "U" else "assistant"
            messages.append({"role": role, "content": msg.contenido})
        
        # Agregar el mensaje actual
        messages.append({"role": "user", "content": user_message})
        
        # Llamar a OpenAI
        client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=500,
            temperature=0.7
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"Error en OpenAI: {str(e)}")  # Para debugging
        # Si hay error de cuota o conexión, usar respuestas predefinidas
        return get_fallback_response(user_message, conversacion)


def get_fallback_response(user_message, conversacion):
    """Respuestas predefinidas cuando OpenAI no está disponible"""
    mensaje_lower = user_message.lower()
    
    # Saludos
    if any(palabra in mensaje_lower for palabra in ['hola', 'hi', 'buenos', 'buenas']):
        return """¡Hola! 👋 Soy tu asistente virtual de cafeterías de Sucre. 

Te ayudo a crear una ruta personalizada de 4 cafeterías basada en tus preferencias de café. 

¿Qué tipo de café te gustaría probar? Puedes elegir entre:
• ☕ Americano - Café negro fuerte y simple
• ☕ Espresso - Café concentrado e intenso  
• ☕ Cappuccino - Café con leche espumosa
• ☕ Latte - Café con mucha leche cremosa
• ☕ Mocha - Café con chocolate
• ☕ Frappé - Café frío batido
• ☕ Macchiato - Espresso con un toque de leche
• ☕ Cortado - Café con un poco de leche

¡Dime cuál prefieres y te creo la ruta perfecta! 🗺️"""
    
    # Tipos de café
    elif any(palabra in mensaje_lower for palabra in ['americano', 'negro', 'fuerte']):
        return """¡Excelente elección! ☕ El americano es perfecto para los amantes del café puro.

Te recomiendo estas 4 cafeterías en Sucre que preparan un americano excepcional:

1. **Café Sucre** - Calle Aniceto Arce 25
   ⭐ 4.8/5 - Especialistas en café de origen boliviano

2. **Café del Mundo** - Plaza 25 de Mayo
   ⭐ 4.6/5 - Ambiente clásico, americano perfecto

3. **Café Colonial** - Calle Potosí 45
   ⭐ 4.7/5 - Tradición y calidad en cada taza

4. **Café Aroma** - Calle España 78
   ⭐ 4.5/5 - Granos tostados localmente

¡Se creará tu ruta optimizada en el mapa! 🗺️"""
    
    elif any(palabra in mensaje_lower for palabra in ['espresso', 'intenso', 'concentrado']):
        return """¡Perfecto! ☕ El espresso es para los verdaderos conocedores.

Estas son las 4 mejores cafeterías para un espresso perfecto en Sucre:

1. **Café Barista** - Calle Junín 32
   ⭐ 4.9/5 - Maestros del espresso, máquinas profesionales

2. **Café Ritual** - Plaza San Francisco
   ⭐ 4.8/5 - Técnica italiana tradicional

3. **Café Artesanal** - Calle Ayacucho 56
   ⭐ 4.7/5 - Granos seleccionados, tostado perfecto

4. **Café Premium** - Calle Bolívar 89
   ⭐ 4.6/5 - Ambiente moderno, espresso de calidad

¡Tu ruta de espresso está lista! 🗺️"""
    
    elif any(palabra in mensaje_lower for palabra in ['cappuccino', 'capuchino', 'leche']):
        return """¡Delicioso! ☕ El cappuccino es perfecto para una experiencia cremosa.

Te recomiendo estas 4 cafeterías que dominan el arte del cappuccino:

1. **Café Latte** - Calle Aniceto Arce 15
   ⭐ 4.8/5 - Espuma perfecta, leche de calidad

2. **Café Milano** - Plaza 25 de Mayo
   ⭐ 4.7/5 - Técnica italiana auténtica

3. **Café Crema** - Calle Potosí 67
   ⭐ 4.6/5 - Arte latte, presentación espectacular

4. **Café Dulce** - Calle España 23
   ⭐ 4.5/5 - Ambiente acogedor, cappuccino suave

¡Se creará tu ruta de cappuccino en el mapa! 🗺️"""
    
    elif any(palabra in mensaje_lower for palabra in ['latte', 'leche', 'cremoso']):
        return """¡Excelente! ☕ El latte es perfecto para una experiencia suave y cremosa.

Estas son las 4 mejores cafeterías para latte en Sucre:

1. **Café Latte Art** - Calle Junín 45
   ⭐ 4.9/5 - Arte latte espectacular, leche perfecta

2. **Café Suave** - Plaza San Francisco
   ⭐ 4.8/5 - Latte cremoso, ambiente relajante

3. **Café Leche** - Calle Ayacucho 34
   ⭐ 4.7/5 - Proporción perfecta café-leche

4. **Café Aroma** - Calle Bolívar 12
   ⭐ 4.6/5 - Latte tradicional, sabor auténtico

¡Tu ruta de latte está lista! 🗺️"""
    
    elif any(palabra in mensaje_lower for palabra in ['mocha', 'chocolate', 'dulce']):
        return """¡Perfecto! ☕ El mocha es ideal para los amantes del chocolate.

Te recomiendo estas 4 cafeterías que preparan mocha excepcional:

1. **Café Chocolate** - Calle Aniceto Arce 78
   ⭐ 4.8/5 - Chocolate artesanal, mocha perfecto

2. **Café Dulce** - Plaza 25 de Mayo
   ⭐ 4.7/5 - Balance perfecto café-chocolate

3. **Café Mocha** - Calle Potosí 23
   ⭐ 4.6/5 - Receta tradicional, sabor auténtico

4. **Café Aroma** - Calle España 56
   ⭐ 4.5/5 - Chocolate premium, mocha suave

¡Se creará tu ruta de mocha en el mapa! 🗺️"""
    
    # Respuesta por defecto
    else:
        return """¡Hola! 👋 Soy tu asistente virtual de cafeterías de Sucre.

Te ayudo a crear una ruta personalizada de 4 cafeterías. 

¿Qué tipo de café te gustaría probar? Puedes elegir entre:
• ☕ Americano - Café negro fuerte
• ☕ Espresso - Café concentrado  
• ☕ Cappuccino - Café con leche espumosa
• ☕ Latte - Café con mucha leche
• ☕ Mocha - Café con chocolate
• ☕ Frappé - Café frío batido
• ☕ Macchiato - Espresso con leche
• ☕ Cortado - Café con poca leche

¡Dime cuál prefieres y te creo la ruta perfecta! 🗺️"""


def get_cafeterias_recomendadas(preferencias_texto):
    """Obtener cafeterías recomendadas basadas en las preferencias"""
    # Esta es una implementación simple. En producción, usarías NLP más avanzado
    cafeterias = Cafeteria.objects.all()
    
    # Filtrar basado en palabras clave en las preferencias
    preferencias_lower = preferencias_texto.lower()
    
    if 'americano' in preferencias_lower or 'negro' in preferencias_lower:
        # Buscar cafeterías con buen americano
        cafeterias = cafeterias.filter(nombre__icontains='cafe')
    elif 'espresso' in preferencias_lower or 'intenso' in preferencias_lower:
        # Buscar cafeterías especializadas
        cafeterias = cafeterias.filter(calificacion_promedio__gte=4.0)
    elif 'cappuccino' in preferencias_lower or 'leche' in preferencias_lower:
        # Buscar cafeterías con buena leche
        cafeterias = cafeterias.filter(total_me_gusta__gte=5)
    
    # Seleccionar 4 cafeterías aleatorias
    cafeterias_list = list(cafeterias)
    if len(cafeterias_list) >= 4:
        return random.sample(cafeterias_list, 4)
    else:
        return cafeterias_list


@login_required
def chat_view(request):
    """Vista principal del chat"""
    # Obtener o crear conversación activa
    conversacion, created = Conversacion.objects.get_or_create(
        usuario=request.user,
        activa=True,
        defaults={'activa': True}
    )
    
    # Si hay múltiples conversaciones activas, desactivar las anteriores
    Conversacion.objects.filter(
        usuario=request.user,
        activa=True
    ).exclude(id=conversacion.id).update(activa=False)
    
    mensajes = conversacion.mensajes.all().order_by('timestamp')
    
    context = {
        'conversacion': conversacion,
        'mensajes': mensajes,
    }
    return render(request, 'chat/chat.html', context)


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def enviar_mensaje(request):
    """Enviar mensaje al chatbot"""
    try:
        data = json.loads(request.body)
        mensaje_usuario = data.get('mensaje', '').strip()
        
        if not mensaje_usuario:
            return JsonResponse({'error': 'Mensaje vacío'}, status=400)
        
        # Obtener conversación activa
        conversacion = Conversacion.objects.filter(
            usuario=request.user,
            activa=True
        ).first()
        
        if not conversacion:
            conversacion = Conversacion.objects.create(
                usuario=request.user,
                activa=True
            )
        
        # Guardar mensaje del usuario
        mensaje_user = Mensaje.objects.create(
            conversacion=conversacion,
            tipo='U',
            contenido=mensaje_usuario
        )
        
        # Obtener respuesta del chatbot
        respuesta_bot = get_openai_response(mensaje_usuario, conversacion)
        
        # Guardar respuesta del bot
        mensaje_bot = Mensaje.objects.create(
            conversacion=conversacion,
            tipo='B',
            contenido=respuesta_bot
        )
        
        # Verificar si el bot está recomendando cafeterías
        if 'recorrido' in respuesta_bot.lower() or 'cafetería' in respuesta_bot.lower():
            # Obtener cafeterías recomendadas
            cafeterias_recomendadas = get_cafeterias_recomendadas(mensaje_usuario)
            
            return JsonResponse({
                'success': True,
                'mensaje_bot': respuesta_bot,
                'cafeterias_recomendadas': [
                    {
                        'id': cafe.id,
                        'nombre': cafe.nombre,
                        'direccion': cafe.direccion,
                        'calificacion': float(cafe.calificacion_promedio),
                        'me_gusta': cafe.total_me_gusta,
                        'latitud': float(cafe.latitud),
                        'longitud': float(cafe.longitud),
                    }
                    for cafe in cafeterias_recomendadas
                ]
            })
        
        return JsonResponse({
            'success': True,
            'mensaje_bot': respuesta_bot,
            'cafeterias_recomendadas': []
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': 'Error al procesar el mensaje'
        }, status=500)


@login_required
@require_http_methods(["POST"])
def crear_recorrido_chat(request):
    """Crear recorrido basado en las recomendaciones del chat"""
    try:
        data = json.loads(request.body)
        cafeterias_ids = data.get('cafeterias_ids', [])
        
        if len(cafeterias_ids) != 4:
            return JsonResponse({
                'success': False,
                'error': 'Debe seleccionar exactamente 4 cafeterías'
            })
        
        # Crear nuevo recorrido
        recorrido = Recorrido.objects.create(
            nombre=f"Recorrido personalizado - {request.user.username}",
            descripcion="Recorrido creado por el chatbot basado en tus preferencias",
            duracion_estimada=120,  # 2 horas estimadas
            distancia_total=5.0,    # 5 km estimados
        )
        
        # Agregar cafeterías al recorrido
        for i, cafeteria_id in enumerate(cafeterias_ids, 1):
            cafeteria = Cafeteria.objects.get(id=cafeteria_id)
            recorrido.cafeterias.add(cafeteria, through_defaults={'orden': i})
        
        return JsonResponse({
            'success': True,
            'recorrido_id': recorrido.id,
            'mensaje': 'Recorrido creado exitosamente'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': 'Error al crear el recorrido'
        }, status=500)


@login_required
def nueva_conversacion(request):
    """Iniciar nueva conversación"""
    # Desactivar conversaciones anteriores
    Conversacion.objects.filter(
        usuario=request.user,
        activa=True
    ).update(activa=False)
    
    # Crear nueva conversación
    conversacion = Conversacion.objects.create(
        usuario=request.user,
        activa=True
    )
    
    return JsonResponse({
        'success': True,
        'conversacion_id': conversacion.id
    })


@csrf_exempt
@require_http_methods(["POST"])
def generar_audio(request):
    """Generar audio usando Amazon Polly"""
    try:
        data = json.loads(request.body)
        text = data.get('text', '').strip()
        voice_id = data.get('voice_id', settings.POLLY_VOICE_ID)
        
        if not text:
            return JsonResponse({'error': 'Texto vacío'}, status=400)
        
        # Generar audio con Amazon Polly
        audio_base64 = voice_service.text_to_speech(text, voice_id)
        
        if audio_base64:
                return JsonResponse({
                    'success': True,
                    'audio': audio_base64,
                    'format': 'mp3',
                    'voice_used': voice_id
                })
        else:
            return JsonResponse({
                'success': False,
                'error': 'No se pudo generar el audio. Usando voz del navegador.'
            })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error generando audio: {str(e)}'
        }, status=500)


def obtener_voces(request):
    """Obtener voces disponibles de Amazon Polly"""
    try:
        voices = voice_service.get_available_voices()
        return JsonResponse({
            'success': True,
            'voices': voices,
            'polly_available': voice_service.is_available()
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error obteniendo voces: {str(e)}'
        }, status=500)
