#!/usr/bin/env python
"""
Script para completar las imágenes faltantes con URLs alternativas
"""

import os
import django
import requests
from pathlib import Path

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cafeterias_sucre.settings')
django.setup()

from core.models import Producto

# URLs alternativas para las imágenes que fallaron
IMAGENES_ALTERNATIVAS = {
    'macchiato': 'https://images.unsplash.com/photo-1541167760496-1628856ab772?w=800&q=80',  # Macchiato alternativo
    'sandwich': 'https://images.unsplash.com/photo-1567234669013-59a3fa63ad04?w=800&q=80',  # Sandwich alternativo
    'aeropress': 'https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=800&q=80',  # Aeropress alternativo
    'cerveza': 'https://images.unsplash.com/photo-1595981267035-7b04ca84a82d?w=800&q=80',  # Cerveza alternativa
    'vino': 'https://images.unsplash.com/photo-1516594915697-87eb3b1c14ea?w=800&q=80',  # Vino alternativo
}

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
    print("🚀 Completando imágenes faltantes...")
    
    # Descargar imágenes faltantes
    imagenes_descargadas = {}
    for categoria, url in IMAGENES_ALTERNATIVAS.items():
        nombre_archivo = f"{categoria}.jpg"
        ruta_imagen = descargar_imagen(url, nombre_archivo)
        if ruta_imagen:
            imagenes_descargadas[categoria] = ruta_imagen
    
    print(f"\n📥 Descargadas {len(imagenes_descargadas)} imágenes alternativas")
    
    # Obtener productos sin imagen
    productos_sin_imagen = []
    for producto in Producto.objects.all():
        if not producto.imagen or producto.imagen == '':
            productos_sin_imagen.append(producto)
    
    print(f"📊 Productos sin imagen: {len(productos_sin_imagen)}")
    
    # Asignar imágenes específicas
    productos_actualizados = 0
    for producto in productos_sin_imagen:
        nombre_lower = producto.nombre.lower()
        
        if 'macchiato' in nombre_lower and 'macchiato' in imagenes_descargadas:
            producto.imagen = imagenes_descargadas['macchiato']
            producto.save()
            productos_actualizados += 1
            print(f"✅ Actualizado: {producto.nombre} -> macchiato.jpg")
        
        elif 'sandwich' in nombre_lower or 'sándwich' in nombre_lower:
            if 'sandwich' in imagenes_descargadas:
                producto.imagen = imagenes_descargadas['sandwich']
                producto.save()
                productos_actualizados += 1
                print(f"✅ Actualizado: {producto.nombre} -> sandwich.jpg")
        
        elif 'aeropress' in nombre_lower and 'aeropress' in imagenes_descargadas:
            producto.imagen = imagenes_descargadas['aeropress']
            producto.save()
            productos_actualizados += 1
            print(f"✅ Actualizado: {producto.nombre} -> aeropress.jpg")
        
        elif 'cerveza' in nombre_lower and 'cerveza' in imagenes_descargadas:
            producto.imagen = imagenes_descargadas['cerveza']
            producto.save()
            productos_actualizados += 1
            print(f"✅ Actualizado: {producto.nombre} -> cerveza.jpg")
        
        elif 'vino' in nombre_lower and 'vino' in imagenes_descargadas:
            producto.imagen = imagenes_descargadas['vino']
            producto.save()
            productos_actualizados += 1
            print(f"✅ Actualizado: {producto.nombre} -> vino.jpg")
        
        else:
            # Usar imagen general para productos no categorizados
            producto.imagen = "productos/general.jpg"
            producto.save()
            productos_actualizados += 1
            print(f"✅ Actualizado: {producto.nombre} -> general.jpg")
    
    print(f"\n🎉 Proceso completado!")
    print(f"📊 Productos actualizados: {productos_actualizados}")

if __name__ == "__main__":
    main()