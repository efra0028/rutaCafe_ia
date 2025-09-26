#!/usr/bin/env python3
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cafeterias_sucre.settings')
django.setup()

from core.models import Cafeteria

print("🗺️ VERIFICANDO COORDENADAS DE CAFETERÍAS")
print("=" * 50)

cafeterias = Cafeteria.objects.all()
print(f"Total de cafeterías: {cafeterias.count()}")
print()

for cafe in cafeterias:
    print(f"🏪 {cafe.nombre}")
    print(f"   📍 Latitud: {cafe.latitud}")
    print(f"   📍 Longitud: {cafe.longitud}")
    print(f"   🗺️ Zona: {cafe.zona}")
    print()

print("✅ Verificación completa")