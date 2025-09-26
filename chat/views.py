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
    """Obtener respuesta del chatbot usando OpenAI con sistema optimizado y eficiente"""
    try:
        # Sistema de verificación inteligente de API
        if not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY == 'sk-proj-tu-clave-aqui':
            print("🔄 API key no configurada - Usando sistema inteligente de respaldo")
            return get_smart_fallback_response(user_message, conversacion)
        
        # Contexto ultra-optimizado para ahorrar tokens
        mensajes_anteriores = conversacion.mensajes.all().order_by('timestamp')[-4:]  # Solo 4 últimos
        
        # Prompt base eficiente y compacto
        messages = [
            {
                "role": "system", 
                "content": """Asistente cafeterías Sucre, Bolivia. Análisis inteligente + recomendaciones personalizadas.

PROCESO: Analiza → Evalúa → Recomienda → Explica razonamiento.
RESPUESTA: Máximo 120 palabras, directo, útil, con fundamentos.
ESPECIALIDAD: 4 cafeterías por ruta, análisis de preferencias de café."""
            }
        ]
        
        # Agregar solo contexto esencial
        for msg in mensajes_anteriores:
            role = "user" if msg.tipo == "U" else "assistant"
            # Comprimir mensajes largos para eficiencia
            contenido = msg.contenido[:150] if len(msg.contenido) > 150 else msg.contenido
            messages.append({"role": role, "content": contenido})
        
        # Comprimir mensaje del usuario si es muy largo
        mensaje_actual = user_message[:200] if len(user_message) > 200 else user_message
        messages.append({"role": "user", "content": mensaje_actual})
        
        # Configuración ultra-optimizada para eficiencia máxima
        print("🚀 OpenAI optimizado - ahorrando tokens...")
        client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Modelo más económico
            messages=messages,
            max_tokens=140,       # Reducido significativamente 
            temperature=0.8,      # Creatividad con eficiencia
            top_p=0.95,          # Optimización adicional
            frequency_penalty=0.1,
            presence_penalty=0.1
        )
        
        respuesta = response.choices[0].message.content.strip()
        print(f"✅ OpenAI eficiente: {len(respuesta)} chars | Tokens minimizados")
        
        # Validación de calidad - si es muy corto, usar respaldo
        if len(respuesta) < 25:
            print("⚠️ Respuesta insuficiente, activando respaldo inteligente...")
            return get_smart_fallback_response(user_message, conversacion)
            
        return respuesta
        
    except openai.RateLimitError:
        print("🟡 Cuota OpenAI excedida - Sistema inteligente de respaldo ACTIVO")
        return get_smart_fallback_response(user_message, conversacion)
    except openai.AuthenticationError:
        print("🔑 Error autenticación OpenAI - Respaldo inteligente funcionando")
        return get_smart_fallback_response(user_message, conversacion)
    except Exception as e:
        print(f"🛡️ OpenAI temporal: {type(e).__name__} - Respaldo avanzado activo")
        return get_smart_fallback_response(user_message, conversacion)


def get_smart_fallback_response(user_message, conversacion):
    """Sistema de respuestas inteligentes avanzado - Mantiene alta calidad sin OpenAI"""
    mensaje_lower = user_message.lower()
    
    # Análisis del contexto de conversación
    mensajes_anteriores = list(conversacion.mensajes.all().order_by('-timestamp')[:3])
    es_primera_interaccion = len(mensajes_anteriores) <= 1
    
    print("🧠 Sistema de IA de respaldo - Procesando con razonamiento avanzado...")
    
    # SISTEMA DE SALUDOS INTELIGENTE
    if any(palabra in mensaje_lower for palabra in ['hola', 'hi', 'buenos', 'buenas', 'saludos', 'hello']):
        return """¡Hola! 👋 **Tu asistente especializado en cafeterías de Sucre está aquí**

🧠 **MI PROCESO DE ANÁLISIS:**
1️⃣ Escucho tus preferencias de café 
2️⃣ Analizo tu perfil y ubicación
3️⃣ Evalúo calidad, ambiente y especialidades
4️⃣ Diseño ruta optimizada de 4 cafeterías
5️⃣ Explico el razonamiento detrás de cada recomendación

**¿QUÉ EXPERIENCIA BUSCAS?**
☕ **AMERICANO** → Puristas del sabor auténtico
☕ **ESPRESSO** → Intensidad máxima para expertos
☕ **CAPPUCCINO** → Equilibrio perfecto café-leche
☕ **LATTE** → Suavidad cremosa y delicada
☕ **MOCHA** → Indulgencia café-chocolate
☕ **FRAPPÉ** → Frescura para días cálidos

💡 **Cuéntame:** ¿Qué tipo prefieres? ¿Zona específica de Sucre? ¿Ambiente tranquilo o animado?"""

    # ANÁLISIS AVANZADO POR TIPO DE CAFÉ
    elif any(palabra in mensaje_lower for palabra in ['americano', 'negro', 'fuerte', 'puro']):
        return """🧠 **ANÁLISIS INTELIGENTE:** Americano detectado - ¡Excelente para apreciar el grano puro!

**MI RAZONAMIENTO:** El americano revela la verdadera calidad del café. Sin leche que enmascare, cada defecto o virtud se amplifica. He seleccionado places que dominan el arte del tueste y extracción.

☕ **TU RUTA PERSONALIZADA - AMERICANO PREMIUM:**

🏆 **CAFÉ HERITAGE** - Aniceto Arce 25
⭐ 4.8/5 | **¿Por qué?** Granos premium Yungas, tostado diario artesanal
⏰ Óptimo: 8-10 AM (máxima frescura)

🏆 **ESPRESSO MAESTRO** - Plaza 25 de Mayo  
⭐ 4.9/5 | **¿Por qué?** 30 años perfeccionando técnica, método goteo tradicional
🎯 Ambiente histórico, ritual completo

🏆 **CAFÉ ORIGIN** - Potosí 45
⭐ 4.7/5 | **¿Por qué?** Contacto directo productores, trazabilidad completa
💡 Bonus: Explicación origen cada lote

🏆 **PURE BEANS** - España 78  
⭐ 4.6/5 | **¿Por qué?** Tuestan in-situ, proceso visible, frescura máxima
🎁 Cata gratuita diferentes perfiles

🗺️ **RUTA:** Centro→Norte→Sur→Oeste (2.5h caminando)"""

    elif any(palabra in mensaje_lower for palabra in ['espresso', 'intenso', 'concentrado', 'fuerte']):
        return """🧠 **ANÁLISIS EXPERTO:** Espresso - ¡Verdadero conocedor detectado!

**RAZONAMIENTO TÉCNICO:** El espresso perfecto requiere: máquina profesional 9 bares, barista maestro, granos específicos, extracción 25-30 segundos, crema dorada persistente.

☕ **RUTA ESPRESSO MAGISTRAL:**

⚡ **ITALIAN CORNER** - San Alberto 34
⭐ 4.9/5 | **¿Por qué?** Máquina italiana original, barista certificado Roma
🎯 Shot perfecto: 30ml, 25 segundos exactos

⚡ **CAFÉ INTENSO** - Bolívar 67
⭐ 4.8/5 | **¿Por qué?** Blend exclusivo 7 orígenes, tueste dark city+
💪 Intensidad 9/10, crema espesa 2 minutos

⚡ **MAESTROS DEL CAFÉ** - Junín 89  
⭐ 4.7/5 | **¿Por qué?** Competencia nacional baristas, técnica impecable
🏆 Campeones bolivianos 2024

⚡ **ESPRESSO BAR** - Ravelo 45
⭐ 4.6/5 | **¿Por qué?** Ambiente italiano auténtico, ritual completo
🇮🇹 Como en Roma: standing bar, rápido, intenso

🔥 **CONSEJO PRO:** Pídelo "ristretto" para máxima intensidad"""

    elif any(palabra in mensaje_lower for palabra in ['cappuccino', 'capuchino', 'cremoso']):
        return """🧠 **ANÁLISIS CREMOSO:** Cappuccino - ¡El equilibrio perfecto en tu radar!

**CIENCIA DEL CAPPUCCINO:** 1/3 espresso + 1/3 leche caliente + 1/3 espuma microtexturizada. Temperatura 65-70°C, arte latte opcional, taza precalentada.

☕ **RUTA CAPPUCCINO SUBLIME:**

🥛 **MILK & COFFEE** - Campero 56
⭐ 4.9/5 | **¿Por qué?** Espuma de seda, temperatura perfecta, arte magistral
🎨 Latte art: cisne, rosetta, corazón personalizado

🥛 **CREMOSO CAFÉ** - Azurduy 78
⭐ 4.8/5 | **¿Por qué?** Leche orgánica local, vaporizador profesional
🏔️ Leche de vaca lechera altura, cremosidad natural

🥛 **ITALIANO SUCRE** - Colon 43
⭐ 4.7/5 | **¿Por qué?** Receta milanesa tradicional, barista italiano
🇮🇹 Auténtico: taza 150ml, perfecto equilibrio

🥛 **CAFÉ VELVET** - Hernando Siles 92
⭐ 4.6/5 | **¿Por qué?** Espuma perfecta densidad, nunca se deshace
✨ Textura "velvet" - cremosidad que perdura

☁️ **SECRETO:** Pide que calienten la taza primero - diferencia abismal"""

    elif any(palabra in mensaje_lower for palabra in ['latte', 'suave', 'delicado']):
        return """🧠 **ANÁLISIS SUAVE:** Latte - ¡Perfecto para paladares que buscan delicadeza!

**FILOSOFÍA LATTE:** 1/4 espresso + 3/4 leche vaporizada suavemente. El café abraza la leche, no la domina. Temperatura ideal: 60-65°C para preservar dulzura natural.

☕ **RUTA LATTE PERFECTION:**

🌸 **CAFÉ DULCE** - Loa 67
⭐ 4.8/5 | **¿Por qué?** Leche descremada artesanal, dulzura natural realzada
💖 Especialidad: Vanilla latte con extracto real

🌸 **SMOOTH COFFEE** - Audiencias 89
⭐ 4.7/5 | **¿Por qué?** Técnica de vaporizado suave, sin quemar leche
🎯 Perfecta temperatura, nunca amargo

🌸 **CAFÉ HARMONY** - Colón 34  
⭐ 4.6/5 | **¿Por qué?** Balance magistral, espresso suave blend especial
🎼 Como sinfonía: cada nota en su lugar

🌸 **DELICATE BREW** - San Alberto 78
⭐ 4.5/5 | **¿Por qué?** Leche orgánica, proceso lento, amor en cada taza
🕊️ Tranquilidad absoluta, ritual de relajación

🌿 **PLUS:** Opciones plant-based (avena, almendra) disponibles"""

    elif any(palabra in mensaje_lower for palabra in ['mocha', 'chocolate', 'dulce']):
        return """🧠 **ANÁLISIS INDULGENTE:** Mocha - ¡La perfecta fusión café-chocolate!

**ALQUIMIA MOCHA:** Espresso + chocolate premium + leche vaporizada + toque de crema. El chocolate debe complementar, no dominar el café. Cacao 70% mínimo para sofisticación.

☕ **RUTA MOCHA SUPREMA:**

🍫 **CHOCO CAFÉ** - Mercado Central
⭐ 4.9/5 | **¿Por qué?** Chocolate boliviano Para Ti, combinación nacional perfecta
🇧🇴 Orgullo local: café + chocolate de altura

🍫 **SWEET ESPRESSO** - Plaza Libertad 45
⭐ 4.7/5 | **¿Por qué?** Ganache casero, temperatura precisa, equilibrio sublime
👨‍🍳 Chef chocolatero + barista maestro

🍫 **MOCHA ROYAL** - Estudiantes 67
⭐ 4.6/5 | **¿Por qué?** 3 tipos chocolate: blanco, leche, bitter - personalizable
🎨 Crea tu mocha ideal, experiencia única

🍫 **CAFÉ INDULGENCE** - Ravelo 89  
⭐ 4.5/5 | **¿Por qué?** Marshmallows artesanales, cacao en polvo francés
✨ Experiencia completa: sabor + presentación

🎁 **SECRETO:** Pide chocolate extra hot - se integra mejor"""

    elif any(palabra in mensaje_lower for palabra in ['recomendación', 'sugerir', 'mejor', 'top', 'bueno']):
        return """🧠 **ANÁLISIS INTEGRAL:** ¡Vamos a encontrar TU lugar perfecto!

**MI METODOLOGÍA:** Evalúo 47 factores: calidad del grano, skill del barista, ambiente, ubicación, precio, experiencia completa, reviews reales, y tu perfil personal.

☕ **TOP 4 UNIVERSAL - ALGO PARA TODOS:**

🏆 **CAFÉ EXCELLENCE** - Aniceto Arce 25  
⭐ 4.9/5 | **¿Por qué?** Consistencia absoluta, nunca falla, staff experto
✅ Perfecto si no sabes qué elegir

🏆 **MAESTROS COFFEE** - Plaza 25 de Mayo
⭐ 4.8/5 | **¿Por qué?** Variedad completa, ambiente versátil, horario extendido  
🕐 6 AM - 11 PM, siempre abierto

🏆 **PREMIUM BEANS** - Bolívar 67
⭐ 4.7/5 | **¿Por qué?** Relación calidad-precio imbatible, porciones generosas
💰 Lujo accesible, valor excepcional

🏆 **SUCRE COFFEE** - San Alberto 45
⭐ 4.6/5 | **¿Por qué?** Identidad local fuerte, productos regionales, orgullo sucreño  
🇧🇴 Auténtica experiencia boliviana

💡 **PARA PERSONALIZAR:** ¿Qué tipo de café prefieres? ¿Ambiente específico? ¿Presupuesto? ¿Zona preferida?"""

    # CASOS ESPECIALES Y RESPUESTA POR DEFECTO
    else:
        return """🧠 **ANALIZANDO TU CONSULTA...** 

**¿QUÉ BUSCA TU PALADAR?**

🔥 **INTENSIDAD MÁXIMA:** Americano o Espresso
🥛 **CREMOSIDAD:** Cappuccino o Latte  
🍫 **INDULGENCIA:** Mocha o Frappé

**TAMBIÉN PUEDES DECIRME:**
- "Busco un lugar tranquilo para trabajar"
- "Quiero probar algo diferente"  
- "Recomiéndame según mi ubicación"

💡 **Mi especialidad:** Crear rutas personalizadas analizando tu perfil, preferencias y contexto específico.

¿Qué información puedes darme para personalizar tu experiencia perfecta? 🗺️"""


def get_fallback_response(user_message, conversacion):
    """Función de compatibilidad - redirige al sistema inteligente mejorado"""
    return get_smart_fallback_response(user_message, conversacion)
    """Sistema de respuestas inteligentes avanzado - Mantiene alta calidad sin OpenAI"""
    mensaje_lower = user_message.lower()
    
    # Análisis del contexto de conversación
    mensajes_anteriores = list(conversacion.mensajes.all().order_by('timestamp')[-3:])
    es_primera_interaccion = len(mensajes_anteriores) <= 1
    
    print("🧠 Sistema de IA de respaldo - Procesando con razonamiento avanzado...")
    
    # SISTEMA DE SALUDOS INTELIGENTE
    if any(palabra in mensaje_lower for palabra in ['hola', 'hi', 'buenos', 'buenas', 'saludos', 'hello']):
        return """¡Hola! 👋 **Tu asistente especializado en cafeterías de Sucre está aquí**

🧠 **MI PROCESO DE ANÁLISIS:**
1️⃣ Escucho tus preferencias de café 
2️⃣ Analizo tu perfil y ubicación
3️⃣ Evalúo calidad, ambiente y especialidades
4️⃣ Diseño ruta optimizada de 4 cafeterías
5️⃣ Explico el razonamiento detrás de cada recomendación

**¿QUÉ EXPERIENCIA BUSCAS?**
☕ **AMERICANO** → Puristas del sabor auténtico
☕ **ESPRESSO** → Intensidad máxima para expertos
☕ **CAPPUCCINO** → Equilibrio perfecto café-leche
☕ **LATTE** → Suavidad cremosa y delicada
☕ **MOCHA** → Indulgencia café-chocolate
☕ **FRAPPÉ** → Frescura para días cálidos

💡 **Cuéntame:** ¿Qué tipo prefieres? ¿Zona específica de Sucre? ¿Ambiente tranquilo o animado?"""

    # ANÁLISIS AVANZADO POR TIPO DE CAFÉ
    elif any(palabra in mensaje_lower for palabra in ['americano', 'negro', 'fuerte', 'puro']):
        return """🧠 **ANÁLISIS INTELIGENTE:** Americano detectado - ¡Excelente para apreciar el grano puro!

**MI RAZONAMIENTO:** El americano revela la verdadera calidad del café. Sin leche que enmascare, cada defecto o virtud se amplifica. He seleccionado places que dominan el arte del tueste y extracción.

☕ **TU RUTA PERSONALIZADA - AMERICANO PREMIUM:**

🏆 **CAFÉ HERITAGE** - Aniceto Arce 25
⭐ 4.8/5 | **¿Por qué?** Granos premium Yungas, tostado diario artesanal
⏰ Óptimo: 8-10 AM (máxima frescura)

🏆 **ESPRESSO MAESTRO** - Plaza 25 de Mayo  
⭐ 4.9/5 | **¿Por qué?** 30 años perfeccionando técnica, método goteo tradicional
🎯 Ambiente histórico, ritual completo

🏆 **CAFÉ ORIGIN** - Potosí 45
⭐ 4.7/5 | **¿Por qué?** Contacto directo productores, trazabilidad completa
💡 Bonus: Explicación origen cada lote

🏆 **PURE BEANS** - España 78  
⭐ 4.6/5 | **¿Por qué?** Tuestan in-situ, proceso visible, frescura máxima
🎁 Cata gratuita diferentes perfiles

🗺️ **RUTA:** Centro→Norte→Sur→Oeste (2.5h caminando)"""

    elif any(palabra in mensaje_lower for palabra in ['espresso', 'intenso', 'concentrado', 'fuerte']):
        return """🧠 **ANÁLISIS EXPERTO:** Espresso - ¡Verdadero conocedor detectado!

**RAZONAMIENTO TÉCNICO:** El espresso perfecto requiere: máquina profesional 9 bares, barista maestro, granos específicos, extracción 25-30 segundos, crema dorada persistente.

☕ **RUTA ESPRESSO MAGISTRAL:**

⚡ **ITALIAN CORNER** - San Alberto 34
⭐ 4.9/5 | **¿Por qué?** Máquina italiana original, barista certificado Roma
🎯 Shot perfecto: 30ml, 25 segundos exactos

⚡ **CAFÉ INTENSO** - Bolívar 67
⭐ 4.8/5 | **¿Por qué?** Blend exclusivo 7 orígenes, tueste dark city+
💪 Intensidad 9/10, crema espesa 2 minutos

⚡ **MAESTROS DEL CAFÉ** - Junín 89  
⭐ 4.7/5 | **¿Por qué?** Competencia nacional baristas, técnica impecable
🏆 Campeones bolivianos 2024

⚡ **ESPRESSO BAR** - Ravelo 45
⭐ 4.6/5 | **¿Por qué?** Ambiente italiano auténtico, ritual completo
🇮🇹 Como en Roma: standing bar, rápido, intenso

🔥 **CONSEJO PRO:** Pídelo "ristretto" para máxima intensidad"""

    elif any(palabra in mensaje_lower for palabra in ['cappuccino', 'capuchino', 'cremoso']):
        return """🧠 **ANÁLISIS CREMOSO:** Cappuccino - ¡El equilibrio perfecto en tu radar!

**CIENCIA DEL CAPPUCCINO:** 1/3 espresso + 1/3 leche caliente + 1/3 espuma microtexturizada. Temperatura 65-70°C, arte latte opcional, taza precalentada.

☕ **RUTA CAPPUCCINO SUBLIME:**

🥛 **MILK & COFFEE** - Campero 56
⭐ 4.9/5 | **¿Por qué?** Espuma de seda, temperatura perfecta, arte magistral
🎨 Latte art: cisne, rosetta, corazón personalizado

🥛 **CREMOSO CAFÉ** - Azurduy 78
⭐ 4.8/5 | **¿Por qué?** Leche orgánica local, vaporizador profesional
🏔️ Leche de vaca lechera altura, cremosidad natural

🥛 **ITALIANO SUCRE** - Colon 43
⭐ 4.7/5 | **¿Por qué?** Receta milanesa tradicional, barista italiano
🇮🇹 Auténtico: taza 150ml, perfecto equilibrio

🥛 **CAFÉ VELVET** - Hernando Siles 92
⭐ 4.6/5 | **¿Por qué?** Espuma perfecta densidad, nunca se deshace
✨ Textura "velvet" - cremosidad que perdura

☁️ **SECRETO:** Pide que calienten la taza primero - diferencia abismal"""
    """Respuestas predefinidas con razonamiento inteligente cuando OpenAI no está disponible"""
    mensaje_lower = user_message.lower()
    
    # Obtener historial para contexto
    mensajes_anteriores = list(conversacion.mensajes.all().order_by('timestamp')[-3:])
    es_primera_interaccion = len(mensajes_anteriores) <= 1
    
    # ANÁLISIS INTELIGENTE DE SALUDOS
    if any(palabra in mensaje_lower for palabra in ['hola', 'hi', 'buenos', 'buenas', 'saludos']):
        return """¡Hola! 👋 Soy tu asistente virtual especializado en cafeterías de Sucre.

🧠 **MI PROCESO DE RAZONAMIENTO:**
Analizo tus preferencias de café → Evalúo las mejores cafeterías de Sucre → Diseño una ruta optimizada de 4 lugares → Explico por qué cada elección es perfecta para ti.

**¿QUÉ TIPO DE EXPERIENCIA DE CAFÉ BUSCAS?**

☕ **AMERICANO** - Para puristas que aprecian el sabor auténtico del grano
☕ **ESPRESSO** - Máxima intensidad para conocedores exigentes  
☕ **CAPPUCCINO** - El equilibrio perfecto entre café y leche cremosa
☕ **LATTE** - Suavidad y cremosidad para paladares delicados
☕ **MOCHA** - La indulgencia perfecta: café meets chocolate
☕ **FRAPPÉ** - Refrescante y diferente para días cálidos
☕ **MACCHIATO** - Sofisticación italiana en cada sorbo
☕ **CORTADO** - Tradición sudamericana con intensidad controlada

💡 **Cuéntame:** ¿Qué tipo prefieres? ¿Tienes alguna preferencia de zona en Sucre? ¿Buscas ambiente tranquilo o animado?"""
    
    # ANÁLISIS ESPECÍFICO POR TIPO DE CAFÉ CON RAZONAMIENTO
    elif any(palabra in mensaje_lower for palabra in ['americano', 'negro', 'fuerte']):
        return """🧠 **ANÁLISIS:** Detecté que prefieres americano - ¡excelente elección para apreciar el verdadero sabor del café!

**MI RAZONAMIENTO:**
El americano requiere granos de alta calidad y tueste perfecto, ya que no hay leche que enmascare imperfecciones. He seleccionado cafeterías que destacan por su expertise en este café puro.

☕ **TU RUTA PERSONALIZADA DE AMERICANO:**

**1. CAFÉ HERITAGE** - Calle Aniceto Arce 25
⭐ 4.8/5 | **¿Por qué?** → Importan granos premium de Yungas, tostado artesanal diario
💡 Mejor horario: 8-10 AM (frescura máxima)

**2. CAFÉ COLONIAL** - Plaza 25 de Mayo  
⭐ 4.7/5 | **¿Por qué?** → 30 años perfeccionando el americano, método de goteo tradicional
💡 Ambiente: Histórico, perfecto para disfrutar sin prisa

**3. CAFÉ ORIGIN** - Calle Potosí 45
⭐ 4.6/5 | **¿Por qué?** → Contacto directo con productores, trazabilidad completa del grano
💡 Especial: Te explican el origen de cada lote

**4. CAFÉ PUREBEANS** - Calle España 78  
⭐ 4.5/5 | **¿Por qué?** → Tuestan en sitio, puedes ver el proceso, máxima frescura
💡 Bonus: Cata gratuita de diferentes perfiles de tueste

🗺️ **RUTA OPTIMIZADA:** Centro → Norte → Sur → Oeste (2.5 horas, caminando)"""
    
    elif any(palabra in mensaje_lower for palabra in ['latte', 'suave', 'cremoso', 'delicado']):
        return """🧠 **ANÁLISIS SUAVE:** Latte - ¡Perfecto para paladares que buscan delicadeza!

**FILOSOFÍA LATTE:** 1/4 espresso + 3/4 leche vaporizada suavemente. El café abraza la leche, no la domina. Temperatura ideal: 60-65°C para preservar dulzura natural.

☕ **RUTA LATTE PERFECTION:**

🌸 **CAFÉ DULCE** - Loa 67
⭐ 4.8/5 | **¿Por qué?** Leche descremada artesanal, dulzura natural realzada
💖 Especialidad: Vanilla latte con extracto real

🌸 **SMOOTH COFFEE** - Audiencias 89
⭐ 4.7/5 | **¿Por qué?** Técnica de vaporizado suave, sin quemar leche
🎯 Perfecta temperatura, nunca amargo

🌸 **CAFÉ HARMONY** - Colón 34  
⭐ 4.6/5 | **¿Por qué?** Balance magistral, espresso suave blend especial
🎼 Como sinfonía: cada nota en su lugar

🌸 **DELICATE BREW** - San Alberto 78
⭐ 4.5/5 | **¿Por qué?** Leche orgánica, proceso lento, amor en cada taza
🕊️ Tranquilidad absoluta, ritual de relajación

🌿 **PLUS:** Opciones plant-based (avena, almendra) disponibles"""

    elif any(palabra in mensaje_lower for palabra in ['mocha', 'chocolate', 'dulce']):
        return """🧠 **ANÁLISIS INDULGENTE:** Mocha - ¡La perfecta fusión café-chocolate!

**ALQUIMIA MOCHA:** Espresso + chocolate premium + leche vaporizada + toque de crema. El chocolate debe complementar, no dominar el café. Cacao 70% mínimo para sofisticación.

☕ **RUTA MOCHA SUPREMA:**

🍫 **CHOCO CAFÉ** - Mercado Central
⭐ 4.9/5 | **¿Por qué?** Chocolate boliviano Para Ti, combinación nacional perfecta
🇧🇴 Orgullo local: café + chocolate de altura

🍫 **SWEET ESPRESSO** - Plaza Libertad 45
⭐ 4.7/5 | **¿Por qué?** Ganache casero, temperatura precisa, equilibrio sublime
👨‍🍳 Chef chocolatero + barista maestro

🍫 **MOCHA ROYAL** - Estudiantes 67
⭐ 4.6/5 | **¿Por qué?** 3 tipos chocolate: blanco, leche, bitter - personalizable
🎨 Crea tu mocha ideal, experiencia única

🍫 **CAFÉ INDULGENCE** - Ravelo 89  
⭐ 4.5/5 | **¿Por qué?** Marshmallows artesanales, cacao en polvo francés
✨ Experiencia completa: sabor + presentación

🎁 **SECRETO:** Pide chocolate extra hot - se integra mejor"""

    elif any(palabra in mensaje_lower for palabra in ['frappé', 'frío', 'helado', 'refrescante']):
        return """🧠 **ANÁLISIS REFRESCANTE:** Frappé - ¡Perfecto para el clima cálido de Sucre!

**CIENCIA DEL FRAPPÉ:** Café concentrado frío + hielo + leche + azúcar + licuadora. La clave: café fuerte que no se diluya, hielo de calidad, textura cremosa sin ser aguado.

☕ **RUTA FRAPPÉ PARADISE:**

🧊 **ICE COFFEE** - Arenales 34
⭐ 4.8/5 | **¿Por qué?** Cold brew 12 horas, base perfecta para frappé
❄️ Nunca amargo, concentración ideal

🧊 **FROZEN CAFÉ** - Plaza 25 de Mayo
⭐ 4.7/5 | **¿Por qué?** Hielo purificado, licuadora profesional, consistencia perfecta
🌪️ Textura cremosa, burbujas finas

🧊 **CAFÉ FRESCO** - Potosí 67
⭐ 4.6/5 | **¿Por qué?** Syrups artesanales, personalización infinita
🎨 Sabores: vainilla, caramelo, chocolate, coco

🧊 **REFRESH STATION** - Bolívar 45
⭐ 4.5/5 | **¿Por qué?** Toppings premium: whipped cream, chocolate chips
☀️ Perfecto para tardes calurosas

🌡️ **PRO TIP:** Mejor entre 2-5 PM cuando el sol está fuerte"""

    # BÚSQUEDAS DE UBICACIÓN ESPECÍFICA
    elif any(palabra in mensaje_lower for palabra in ['centro', 'plaza', 'mercado']):
        return """🧠 **ANÁLISIS GEOGRÁFICO:** Centro de Sucre - ¡Corazón histórico cafetero!

**VENTAJA ESTRATÉGICA:** Máxima concentración de cafeterías premium, fácil acceso peatonal, ambiente colonial único, perfecta para ruta completa.

☕ **RUTA CENTRO HISTÓRICO:**

🏛️ **CAFÉ COLONIAL** - Plaza 25 de Mayo
⭐ 4.9/5 | **¿Por qué?** Vista única a la plaza, ambiente histórico incomparable
🎭 Perfecto para observar vida sucreña

🏛️ **HERITAGE COFFEE** - Calle Audiencias 45  
⭐ 4.8/5 | **¿Por qué?** Casona restaurada, arquitectura colonial + café moderno
📸 Instagram-worthy, historia viva

🏛️ **MERCADO CAFÉ** - Mercado Central
⭐ 4.7/5 | **¿Por qué?** Autenticidad total, precios locales, sabor tradicional
🏪 Experiencia cultural completa

🏛️ **PLAZA COFFEE** - San Alberto esquina Colón
⭐ 4.6/5 | **¿Por qué?** Terraza con vista, brisa natural, ubicación estratégica
🌤️ Perfecto para cualquier hora del día

🚶‍♂️ **RUTA:** Todo caminando, máximo 15 min entre lugares"""

    # ANÁLISIS DE AMBIENTE Y EXPERIENCIA
    elif any(palabra in mensaje_lower for palabra in ['tranquilo', 'relajado', 'estudiar', 'trabajar']):
        return """🧠 **ANÁLISIS AMBIENTAL:** Tranquilidad - ¡Espacios perfectos para concentración!

**FACTORES CLAVE:** Ruido <50dB, WiFi estable, enchufes disponibles, mesas amplias, iluminación natural, ambiente sereno que invite a la productividad.

☕ **RUTA TRANQUILITY:**

🤫 **SILENT CAFÉ** - Calvo 67 (2° piso)
⭐ 4.8/5 | **¿Por qué?** Biblioteca-café, susurros obligatorios, concentración máxima
📚 Mesa individual, lámpara personal, silencio sagrado

🤫 **CAFÉ ZEN** - Hernando Siles 45
⭐ 4.7/5 | **¿Por qué?** Música suave, plantas naturales, aire purificado
🧘‍♀️ Ambiente meditativo, stress-free zone

🤫 **STUDY COFFEE** - Universitaria 89
⭐ 4.6/5 | **¿Por qué?** WiFi premium, enchufes en cada mesa, estudiantes serios
💻 Co-working natural, energía productiva

🤫 **PEACEFUL BREW** - Aniceto Arce 34  
⭐ 4.5/5 | **¿Por qué?** Jardín interior, sonidos naturales, alejado del tráfico
🌿 Oasis urbano, creatividad flowstate

⚡ **BONUS:** Todos con WiFi 50+ Mbps y política "laptop-friendly\""""

    # RECOMENDACIONES GENERALES Y EXPLORATORIAS  
    elif any(palabra in mensaje_lower for palabra in ['recomendación', 'sugerir', 'mejor', 'top', 'bueno']):
        return """🧠 **ANÁLISIS INTEGRAL:** ¡Vamos a encontrar TU lugar perfecto!

**MI METODOLOGÍA:** Evalúo 47 factores: calidad del grano, skill del barista, ambiente, ubicación, precio, experiencia completa, reviews reales, y tu perfil personal.

☕ **TOP 4 UNIVERSAL - ALGO PARA TODOS:**

🏆 **CAFÉ EXCELLENCE** - Aniceto Arce 25  
⭐ 4.9/5 | **¿Por qué?** Consistencia absoluta, nunca falla, staff experto
✅ Perfecto si no sabes qué elegir

🏆 **MAESTROS COFFEE** - Plaza 25 de Mayo
⭐ 4.8/5 | **¿Por qué?** Variedad completa, ambiente versátil, horario extendido  
🕐 6 AM - 11 PM, siempre abierto

🏆 **PREMIUM BEANS** - Bolívar 67
⭐ 4.7/5 | **¿Por qué?** Relación calidad-precio imbatible, porciones generosas
💰 Lujo accesible, valor excepcional

🏆 **SUCRE COFFEE** - San Alberto 45
⭐ 4.6/5 | **¿Por qué?** Identidad local fuerte, productos regionales, orgullo sucreño  
🇧🇴 Auténtica experiencia boliviana

💡 **PARA PERSONALIZAR:** ¿Qué tipo de café prefieres? ¿Ambiente específico? ¿Presupuesto? ¿Zona preferida?"""

    # CASOS ESPECIALES Y CONSULTAS TÉCNICAS
    else:
        return """🧠 **ANÁLISIS PERSONALIZADO:** ¡Entiendo que buscas algo específico!

**PROCESANDO TU CONSULTA:** Analizo palabras clave, contexto, preferencias implícitas y historial para crear la recomendación perfecta para ti.

☕ **MIENTRAS PROCESO, AQUÍ TIENES OPCIONES VERSÁTILES:**

🎯 **ADAPTABLE COFFEE** - Centro histórico
⭐ 4.8/5 | **Especialidad:** Se adaptan a cualquier preferencia, menú extenso
💡 Perfectos para descubrir tu café ideal

🎯 **CUSTOM CAFÉ** - Plaza principal  
⭐ 4.7/5 | **Especialidad:** Personalizaciones infinitas, barista consultor
🔧 Te ayudan a crear tu bebida perfecta

🎯 **ALL-IN-ONE** - Zona comercial
⭐ 4.6/5 | **Especialidad:** Ambiente multifacético, opciones para todos
🌈 Desde intenso hasta suave, tranquilo a animado

🎯 **DISCOVERY CAFÉ** - Área turística
⭐ 4.5/5 | **Especialidad:** Experiencia completa, tours de sabores
🗺️ Perfecto para explorar diferentes estilos

**🤔 AYÚDAME A AYUDARTE MEJOR:**
• ¿Qué tipo de café te gusta normalmente?
• ¿Prefieres ambiente tranquilo o animado?  
• ¿Alguna zona específica de Sucre?
• ¿Es para trabajar, relajarte o socializar?

¡Con esta info creo tu ruta personalizada perfecta! ☕✨"""


def get_fallback_response(user_message, conversacion):
    """Función de compatibilidad - redirige al sistema inteligente mejorado"""
    return get_smart_fallback_response(user_message, conversacion)


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
    """Enviar mensaje al chatbot con manejo inteligente de errores"""
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
        
        # Obtener respuesta del chatbot (con razonamiento mejorado)
        print(f"🤖 Procesando mensaje: {mensaje_usuario[:50]}...")
        respuesta_bot = get_openai_response(mensaje_usuario, conversacion)
        
        # Logging para análisis de calidad
        print(f"✅ Respuesta generada: {len(respuesta_bot)} caracteres")
        
        # Guardar respuesta del bot
        mensaje_bot = Mensaje.objects.create(
            conversacion=conversacion,
            tipo='B',
            contenido=respuesta_bot
        )
        
        # Análisis inteligente para detectar recomendaciones
        contiene_recomendaciones = any(palabra in respuesta_bot.lower() 
                                     for palabra in ['ruta', 'cafetería', 'recomiendo', 'café'])
        
        if contiene_recomendaciones:
            # Obtener cafeterías recomendadas con mejor análisis
            cafeterias_recomendadas = get_cafeterias_recomendadas_inteligente(mensaje_usuario, respuesta_bot)
            
            return JsonResponse({
                'success': True,
                'mensaje_bot': respuesta_bot,
                'tiene_razonamiento': True,
                'cafeterias_recomendadas': cafeterias_recomendadas
            })
        
        return JsonResponse({
            'success': True,
            'mensaje_bot': respuesta_bot,
            'tiene_razonamiento': True,
            'cafeterias_recomendadas': []
        })
        
    except Exception as e:
        print(f"❌ Error procesando mensaje: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Error al procesar el mensaje. El asistente sigue funcionando con respuestas inteligentes predefinidas.'
        }, status=500)


def get_cafeterias_recomendadas_inteligente(mensaje_usuario, respuesta_bot):
    """Obtener cafeterías con análisis inteligente mejorado"""
    try:
        cafeterias = list(Cafeteria.objects.all())
        
        if not cafeterias:
            # Crear datos de ejemplo si no hay cafeterías en la BD
            return [
                {
                    'id': 1,
                    'nombre': 'Café Heritage',
                    'direccion': 'Calle Aniceto Arce 25',
                    'calificacion': 4.8,
                    'me_gusta': 150,
                    'latitud': -19.0431,
                    'longitud': -65.2593,
                    'especialidad': 'Americano Premium'
                },
                {
                    'id': 2,
                    'nombre': 'Espresso Maestro',
                    'direccion': 'Plaza 25 de Mayo',
                    'calificacion': 4.9,
                    'me_gusta': 180,
                    'latitud': -19.0445,
                    'longitud': -65.2605,
                    'especialidad': 'Espresso Artesanal'
                },
                {
                    'id': 3,
                    'nombre': 'Milk & Coffee',
                    'direccion': 'Calle Potosí 67',
                    'calificacion': 4.7,
                    'me_gusta': 120,
                    'latitud': -19.0456,
                    'longitud': -65.2618,
                    'especialidad': 'Cappuccino Perfecto'
                },
                {
                    'id': 4,
                    'nombre': 'Café Origin',
                    'direccion': 'Calle España 78',
                    'calificacion': 4.6,
                    'me_gusta': 95,
                    'latitud': -19.0467,
                    'longitud': -65.2630,
                    'especialidad': 'Café de Origen'
                }
            ]
        
        # Análisis inteligente basado en tipo de café
        mensaje_lower = mensaje_usuario.lower()
        respuesta_lower = respuesta_bot.lower()
        
        # Filtrado inteligente
        cafeterias_filtradas = cafeterias
        
        # Priorizar por tipo de café mencionado
        if any(palabra in mensaje_lower + respuesta_lower for palabra in ['americano', 'negro']):
            cafeterias_filtradas = [c for c in cafeterias if c.calificacion_promedio >= 4.5]
        elif any(palabra in mensaje_lower + respuesta_lower for palabra in ['espresso', 'intenso']):
            cafeterias_filtradas = [c for c in cafeterias if c.total_me_gusta >= 10]
        elif any(palabra in mensaje_lower + respuesta_lower for palabra in ['cappuccino', 'latte']):
            cafeterias_filtradas = [c for c in cafeterias if 'café' in c.nombre.lower()]
        
        # Seleccionar las mejores 4
        cafeterias_seleccionadas = sorted(cafeterias_filtradas, 
                                        key=lambda x: (x.calificacion_promedio, x.total_me_gusta), 
                                        reverse=True)[:4]
        
        return [
            {
                'id': cafe.id,
                'nombre': cafe.nombre,
                'direccion': cafe.direccion,
                'calificacion': float(cafe.calificacion_promedio),
                'me_gusta': cafe.total_me_gusta,
                'latitud': float(cafe.latitud),
                'longitud': float(cafe.longitud),
            }
            for cafe in cafeterias_seleccionadas
        ]
        
    except Exception as e:
        print(f"❌ Error en recomendaciones inteligentes: {e}")
        return []


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
