#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cafeterias_sucre.settings')
django.setup()

from core.models import Cafeteria

print(f"📊 Total de cafeterías: {Cafeteria.objects.count()}")
print("\n🏪 Listado de cafeterías:")
for i, cafeteria in enumerate(Cafeteria.objects.all()[:10], 1):
    print(f"{i:2}. {cafeteria.nombre}")
    print(f"    📍 Ubicación: {cafeteria.latitud}, {cafeteria.longitud}")
    print(f"    📍 Dirección: {cafeteria.direccion}")
    print(f"    ⭐ Calificación: {cafeteria.calificacion_promedio}")
    print()

print(f"\n✅ Revisión completa. Total: {Cafeteria.objects.count()} cafeterías")