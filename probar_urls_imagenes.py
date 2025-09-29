#!/usr/bin/env python
"""
Script para probar las URLs de imágenes
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cafeterias_sucre.settings')
django.setup()

from core.models import Producto

def main():
    # Probar algunos productos con imágenes
    productos_prueba = Producto.objects.filter(imagen__icontains='americano')[:3]
    
    print("🧪 Probando URLs de imágenes:")
    for producto in productos_prueba:
        print(f"\nProducto: {producto.nombre}")
        print(f"Imagen: {producto.imagen}")
        if producto.imagen:
            print(f"URL imagen: {producto.imagen.url}")
        else:
            print("❌ Sin imagen")
    
    # Estadísticas finales
    total_productos = Producto.objects.count()
    productos_con_imagen = Producto.objects.exclude(imagen='').exclude(imagen__isnull=True).count()
    productos_sin_imagen = total_productos - productos_con_imagen
    
    print(f"\n📊 Estadísticas finales:")
    print(f"Total productos: {total_productos}")
    print(f"Con imagen: {productos_con_imagen}")
    print(f"Sin imagen: {productos_sin_imagen}")
    print(f"Porcentaje con imagen: {(productos_con_imagen/total_productos)*100:.1f}%")

if __name__ == "__main__":
    main()