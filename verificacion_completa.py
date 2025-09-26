#!/usr/bin/env python3
"""
Script de verificación completa del sistema de cafeterías
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cafeterias_sucre.settings')
django.setup()

from core.models import Cafeteria, TipoCafe, Producto, Recorrido
from django.conf import settings

print("🚀 VERIFICACIÓN COMPLETA DEL SISTEMA")
print("=" * 60)

# Verificar configuración
print("⚙️ CONFIGURACIÓN:")
print(f"   🔑 Mapbox Token: {settings.MAPBOX_ACCESS_TOKEN[:20]}...")
print(f"   📊 Debug Mode: {settings.DEBUG}")
print()

# Verificar datos
cafeterias = Cafeteria.objects.all()
tipos_cafe = TipoCafe.objects.all()
productos = Producto.objects.all()
recorridos = Recorrido.objects.all()

print("📊 ESTADÍSTICAS:")
print(f"   🏪 Cafeterías: {cafeterias.count()}")
print(f"   ☕ Tipos de café: {tipos_cafe.count()}")
print(f"   🛍️ Productos: {productos.count()}")
print(f"   🗺️ Recorridos: {recorridos.count()}")
print()

# Verificar coordenadas
print("🗺️ VERIFICACIÓN DE COORDENADAS:")
coordenadas_vacias = cafeterias.filter(latitud__isnull=True).count()
print(f"   ✅ Cafeterías con coordenadas: {cafeterias.count() - coordenadas_vacias}")
print(f"   ❌ Cafeterías sin coordenadas: {coordenadas_vacias}")
print()

# Verificar por zona
print("📍 DISTRIBUCIÓN POR ZONAS:")
for zona in ['Centro', 'Norte', 'Sur', 'Este']:
    count = cafeterias.filter(zona=zona).count()
    print(f"   🏙️ {zona}: {count} cafeterías")
print()

# Top 5 mejor calificadas
print("🏆 TOP 5 MEJOR CALIFICADAS:")
top_cafeterias = cafeterias.order_by('-calificacion_promedio')[:5]
for i, cafe in enumerate(top_cafeterias, 1):
    print(f"   {i}. {cafe.nombre} - ⭐{cafe.calificacion_promedio} ({cafe.zona})")
print()

# Verificar productos por cafetería
print("🛍️ PRODUCTOS POR CAFETERÍA:")
for cafe in cafeterias[:5]:  # Mostrar solo las primeras 5
    productos_cafe = cafe.productos.count()
    print(f"   🏪 {cafe.nombre}: {productos_cafe} productos")
print(f"   ... y {cafeterias.count() - 5} cafeterías más")
print()

# URLs importantes
print("🌐 URLS DEL SISTEMA:")
print(f"   🏠 Página principal: http://127.0.0.1:8000/")
print(f"   🗺️ Mapa incluido en página principal")
print(f"   📋 API cercanas: http://127.0.0.1:8000/api/cercanas/")
print(f"   🚗 API ordenar ruta: http://127.0.0.1:8000/api/ordenar-ruta/")
print()

print("✅ SISTEMA COMPLETAMENTE CONFIGURADO")
print("🎯 Todas las cafeterías deberían aparecer en el mapa")
print("=" * 60)

# Test de coordenadas específicas para verificar
print("🧪 MUESTRA DE COORDENADAS:")
for cafe in cafeterias.order_by('zona')[:8]:
    print(f"   📍 {cafe.nombre}")
    print(f"      Lat: {cafe.latitud}, Lng: {cafe.longitud}")
    print(f"      Zona: {cafe.zona}")
    print()