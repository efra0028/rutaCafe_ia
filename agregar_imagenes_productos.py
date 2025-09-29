#!/usr/bin/env python
"""
Script para agregar imágenes a productos de café que no tienen imagen asignada.
Descarga imágenes gratuitas de Unsplash para productos de café típicos.
"""

import os
import django
import requests
from pathlib import Path

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cafeterias_sucre.settings')
django.setup()

from core.models import Producto

# Diccionario de URLs de imágenes gratuitas de alta calidad para productos de café
IMAGENES_PRODUCTOS = {
    # Bebidas de café
    'americano': 'https://images.unsplash.com/photo-1509042239860-f550ce710b93?w=800&q=80',  # Americano
    'cappuccino': 'https://images.unsplash.com/photo-1534778101976-62847782c213?w=800&q=80',  # Cappuccino con espuma
    'latte': 'https://images.unsplash.com/photo-1561882468-9110e03e0f78?w=800&q=80',  # Latte art
    'espresso': 'https://images.unsplash.com/photo-1510707577719-ae7c14805e3a?w=800&q=80',  # Espresso
    'mocha': 'https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=800&q=80',  # Mocha con chocolate
    'macchiato': 'https://images.unsplash.com/photo-1572286258217-fac0c9c87f51?w=800&q=80',  # Macchiato
    'frappe': 'https://images.unsplash.com/photo-1461023058943-07fcbe16d735?w=800&q=80',  # Frappé helado
    'cortado': 'https://images.unsplash.com/photo-1497636577773-f1231844b336?w=800&q=80',  # Cortado
    'cold_brew': 'https://images.unsplash.com/photo-1544787219-7f47ccb76574?w=800&q=80',  # Cold brew
    'cafe_con_leche': 'https://images.unsplash.com/photo-1509042239860-f550ce710b93?w=800&q=80',  # Café con leche
    
    # Comidas y snacks
    'sandwich': 'https://images.unsplash.com/photo-1565299624946-b28f40a0ca4b?w=800&q=80',  # Sandwich
    'wrap': 'https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=800&q=80',  # Wrap
    'desayuno': 'https://images.unsplash.com/photo-1533089860892-a7c6f0a88666?w=800&q=80',  # Desayuno
    'bowl': 'https://images.unsplash.com/photo-1511690743698-d9d85f2fbf38?w=800&q=80',  # Bowl saludable
    'smoothie': 'https://images.unsplash.com/photo-1553530666-ba11a7da3888?w=800&q=80',  # Smoothie verde
    'jugos': 'https://images.unsplash.com/photo-1622597467836-f3285f2131b8?w=800&q=80',  # Jugos naturales
    'muffin': 'https://images.unsplash.com/photo-1607958996333-41aef7caefaa?w=800&q=80',  # Muffin
    'tostadas': 'https://images.unsplash.com/photo-1484723091739-30a097e8f929?w=800&q=80',  # Tostadas
    'hamburguesa': 'https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=800&q=80',  # Hamburguesa
    
    # Postres
    'torta': 'https://images.unsplash.com/photo-1563729784474-d77dbb933a9e?w=800&q=80',  # Torta de chocolate
    'cheesecake': 'https://images.unsplash.com/photo-1565661531096-8e289cb90e8b?w=800&q=80',  # Cheesecake
    'carrot_cake': 'https://images.unsplash.com/photo-1621303837174-89787a7d4729?w=800&q=80',  # Carrot cake
    'postre': 'https://images.unsplash.com/photo-1551024601-bec78aea704b?w=800&q=80',  # Postre general
    'dulces': 'https://images.unsplash.com/photo-1506224772180-d75b3efbe9be?w=800&q=80',  # Dulces caseros
    
    # Café especializado
    'cafe_especialidad': 'https://images.unsplash.com/photo-1559056199-641a0ac8b55e?w=800&q=80',  # Café de especialidad
    'cafe_altura': 'https://images.unsplash.com/photo-1447933601403-0c6688de566e?w=800&q=80',  # Café de altura
    'single_origin': 'https://images.unsplash.com/photo-1497515114629-f71d768fd07c?w=800&q=80',  # Single origin
    'metodo_v60': 'https://images.unsplash.com/photo-1606312619070-d48b4c652a52?w=800&q=80',  # Método V60
    'chemex': 'https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=800&q=80',  # Chemex
    'aeropress': 'https://images.unsplash.com/photo-1611854779393-1b2da9d400ac?w=800&q=80',  # Aeropress
    
    # Otras bebidas
    'cerveza': 'https://images.unsplash.com/photo-1558618047-3c8c76ca7d13?w=800&q=80',  # Cerveza artesanal
    'cocktail': 'https://images.unsplash.com/photo-1551538827-9c037cb4f32a?w=800&q=80',  # Cocktail
    'infusion': 'https://images.unsplash.com/photo-1556679343-c7306c1976bc?w=800&q=80',  # Infusión
    'vino': 'https://images.unsplash.com/photo-1506377872849-38c1b6445363?w=800&q=80',  # Vino
    
    # Imagen genérica para productos sin categoría específica
    'general': 'https://images.unsplash.com/photo-1559056199-641a0ac8b55e?w=800&q=80'
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

def categorizar_producto(nombre):
    """Categoriza un producto basado en su nombre para asignar la imagen apropiada."""
    nombre_lower = nombre.lower()
    
    # Bebidas de café
    if 'americano' in nombre_lower:
        return 'americano'
    elif 'cappuccino' in nombre_lower:
        return 'cappuccino'
    elif 'latte' in nombre_lower:
        return 'latte'
    elif 'espresso' in nombre_lower:
        return 'espresso'
    elif 'mocha' in nombre_lower:
        return 'mocha'
    elif 'macchiato' in nombre_lower:
        return 'macchiato'
    elif 'frappé' in nombre_lower or 'frappe' in nombre_lower:
        return 'frappe'
    elif 'cortado' in nombre_lower:
        return 'cortado'
    elif 'cold brew' in nombre_lower:
        return 'cold_brew'
    elif 'café con leche' in nombre_lower or 'cafe con leche' in nombre_lower:
        return 'cafe_con_leche'
    
    # Comidas
    elif 'sandwich' in nombre_lower or 'sándwich' in nombre_lower:
        return 'sandwich'
    elif 'wrap' in nombre_lower:
        return 'wrap'
    elif 'desayuno' in nombre_lower:
        return 'desayuno'
    elif 'bowl' in nombre_lower:
        return 'bowl'
    elif 'smoothie' in nombre_lower:
        return 'smoothie'
    elif 'jugo' in nombre_lower or 'jugos' in nombre_lower:
        return 'jugos'
    elif 'muffin' in nombre_lower:
        return 'muffin'
    elif 'tostada' in nombre_lower or 'tostadas' in nombre_lower:
        return 'tostadas'
    elif 'hamburguesa' in nombre_lower:
        return 'hamburguesa'
    
    # Postres
    elif 'torta' in nombre_lower:
        return 'torta'
    elif 'cheesecake' in nombre_lower:
        return 'cheesecake'
    elif 'carrot cake' in nombre_lower:
        return 'carrot_cake'
    elif 'postre' in nombre_lower or 'postres' in nombre_lower:
        return 'postre'
    elif 'dulce' in nombre_lower or 'dulces' in nombre_lower:
        return 'dulces'
    
    # Café especializado
    elif 'single origin' in nombre_lower or 'origin' in nombre_lower:
        return 'single_origin'
    elif 'v60' in nombre_lower:
        return 'metodo_v60'
    elif 'chemex' in nombre_lower:
        return 'chemex'
    elif 'aeropress' in nombre_lower:
        return 'aeropress'
    elif 'especialidad' in nombre_lower or 'specialty' in nombre_lower:
        return 'cafe_especialidad'
    elif 'altura' in nombre_lower:
        return 'cafe_altura'
    
    # Otras bebidas
    elif 'cerveza' in nombre_lower:
        return 'cerveza'
    elif 'cocktail' in nombre_lower:
        return 'cocktail'
    elif 'infusión' in nombre_lower or 'infusion' in nombre_lower:
        return 'infusion'
    elif 'vino' in nombre_lower or 'vinos' in nombre_lower:
        return 'vino'
    
    # Por defecto, si contiene "café" o "cafe"
    elif 'café' in nombre_lower or 'cafe' in nombre_lower or 'coffee' in nombre_lower:
        return 'americano'  # Imagen genérica de café
    
    return 'general'

def main():
    print("🚀 Iniciando proceso de descarga de imágenes para productos...")
    
    # Obtener productos sin imagen
    productos_sin_imagen = []
    for producto in Producto.objects.all():
        if not producto.imagen or producto.imagen == '':
            productos_sin_imagen.append(producto)
    
    print(f"📊 Encontrados {len(productos_sin_imagen)} productos sin imagen")
    
    # Categorizar productos y descargar imágenes únicas
    categorias_usadas = set()
    imagenes_descargadas = {}
    
    for producto in productos_sin_imagen:
        categoria = categorizar_producto(producto.nombre)
        
        # Descargar imagen solo si no la hemos descargado antes
        if categoria not in categorias_usadas:
            url = IMAGENES_PRODUCTOS.get(categoria, IMAGENES_PRODUCTOS['general'])
            nombre_archivo = f"{categoria}.jpg"
            
            ruta_imagen = descargar_imagen(url, nombre_archivo)
            if ruta_imagen:
                imagenes_descargadas[categoria] = ruta_imagen
                categorias_usadas.add(categoria)
    
    print(f"\n📥 Descargadas {len(imagenes_descargadas)} imágenes únicas")
    
    # Asignar imágenes a productos
    productos_actualizados = 0
    for producto in productos_sin_imagen:
        categoria = categorizar_producto(producto.nombre)
        
        if categoria in imagenes_descargadas:
            producto.imagen = imagenes_descargadas[categoria]
            producto.save()
            productos_actualizados += 1
            print(f"✅ Actualizado: {producto.nombre} -> {categoria}.jpg")
    
    print(f"\n🎉 Proceso completado!")
    print(f"📊 Productos actualizados: {productos_actualizados}")
    print(f"🖼️  Imágenes descargadas: {len(imagenes_descargadas)}")

if __name__ == "__main__":
    main()