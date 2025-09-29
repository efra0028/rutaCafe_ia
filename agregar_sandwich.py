#!/usr/bin/env python
"""
Script para completar el sandwich que faltó
"""

import os
import django
import requests
from pathlib import Path

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cafeterias_sucre.settings')
django.setup()

from core.models import Producto

def descargar_imagen(url, nombre_archivo):
    """Descarga una imagen desde una URL y la guarda localmente."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        # Crear directorio si no existe
        media_path = Path('media/productos')
        media_path.mkdir(parents=True, exist_ok=True)
        
        # Guardar archivo
        file_path = media_path / nombre_archivo
        with open(file_path, 'wb') as f:
            f.write(response.content)
        
        print(f"✅ Descargada: {nombre_archivo}")
        return f"productos/{nombre_archivo}"
    except Exception as e:
        print(f"❌ Error descargando {nombre_archivo}: {e}")
        return None

def main():
    print("🚀 Agregando imagen de sandwich...")
    
    # URL alternativa para sandwich
    url_sandwich = 'https://images.unsplash.com/photo-1528736235302-52922df5c122?w=800&q=80'
    
    ruta_imagen = descargar_imagen(url_sandwich, 'sandwich.jpg')
    
    if ruta_imagen:
        # Buscar productos de sandwich sin imagen
        productos_sandwich = []
        for producto in Producto.objects.all():
            if not producto.imagen or producto.imagen == '':
                nombre_lower = producto.nombre.lower()
                if 'sandwich' in nombre_lower or 'sándwich' in nombre_lower:
                    productos_sandwich.append(producto)
        
        print(f"📊 Productos de sandwich sin imagen: {len(productos_sandwich)}")
        
        # Actualizar productos
        for producto in productos_sandwich:
            producto.imagen = ruta_imagen
            producto.save()
            print(f"✅ Actualizado: {producto.nombre} -> sandwich.jpg")
        
        print(f"\n🎉 Proceso completado!")

if __name__ == "__main__":
    main()