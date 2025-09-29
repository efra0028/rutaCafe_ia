#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cafeterias_sucre.settings')
django.setup()

from django.conf import settings

def verificar_configuracion_mapbox():
    """Verificar que la configuración de Mapbox esté correcta"""
    print("Verificando configuración de Mapbox...")
    print(f"Token de Mapbox: {settings.MAPBOX_ACCESS_TOKEN[:20]}...")
    
    if not settings.MAPBOX_ACCESS_TOKEN or settings.MAPBOX_ACCESS_TOKEN == 'pk.tu-token-aqui':
        print("❌ Token de Mapbox no configurado")
        return False
    
    print("✅ Token de Mapbox configurado")
    return True

def verificar_cafeteria_coordenadas():
    """Verificar que las cafeterías tengan coordenadas válidas"""
    from core.models import Cafeteria
    
    cafeterias = Cafeteria.objects.all()
    print(f"\nVerificando coordenadas de {cafeterias.count()} cafeterías...")
    
    for cafe in cafeterias[:3]:  # Solo las primeras 3 para prueba
        print(f"- {cafe.nombre}: Lat {cafe.latitud}, Lng {cafe.longitud}")
        
        # Verificar que las coordenadas estén en el rango válido para Sucre
        lat = float(cafe.latitud)
        lng = float(cafe.longitud)
        
        if not (-19.1 <= lat <= -18.9):
            print(f"  ⚠️ Latitud fuera de rango para Sucre: {lat}")
        if not (-65.4 <= lng <= -65.1):
            print(f"  ⚠️ Longitud fuera de rango para Sucre: {lng}")
    
    return True

if __name__ == "__main__":
    print("=== Diagnóstico del Mapa ===")
    
    # Verificar configuración
    mapbox_ok = verificar_configuracion_mapbox()
    
    # Verificar coordenadas
    coords_ok = verificar_cafeteria_coordenadas()
    
    print("\n=== Resumen ===")
    print(f"Token Mapbox: {'✅' if mapbox_ok else '❌'}")
    print(f"Coordenadas: {'✅' if coords_ok else '❌'}")
    
    if mapbox_ok and coords_ok:
        print("\n✅ Configuración del mapa parece correcta")
        print("Si el mapa no funciona, puede ser un problema de red o JavaScript")
    else:
        print("\n❌ Hay problemas en la configuración")