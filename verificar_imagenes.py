#!/usr/bin/env python
"""
Script para verificar y contar productos sin imagen
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cafeterias_sucre.settings')
django.setup()

from core.models import Producto

def main():
    # Obtener todos los productos
    productos = Producto.objects.all()
    print(f"Total productos: {productos.count()}")
    
    # Productos sin imagen (campo vacío o None)
    productos_sin_imagen = []
    productos_con_imagen = []
    
    for producto in productos:
        if not producto.imagen or producto.imagen == '':
            productos_sin_imagen.append(producto)
        else:
            productos_con_imagen.append(producto)
    
    print(f"\nProductos SIN imagen: {len(productos_sin_imagen)}")
    print(f"Productos CON imagen: {len(productos_con_imagen)}")
    
    # Mostrar algunos ejemplos
    print(f"\nPrimeros 10 productos SIN imagen:")
    for i, producto in enumerate(productos_sin_imagen[:10]):
        print(f"{i+1}. {producto.nombre} (imagen: '{producto.imagen}')")
    
    print(f"\nPrimeros 5 productos CON imagen:")
    for i, producto in enumerate(productos_con_imagen[:5]):
        print(f"{i+1}. {producto.nombre} (imagen: '{producto.imagen}')")

if __name__ == "__main__":
    main()