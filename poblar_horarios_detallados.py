#!/usr/bin/env python
import os
import sys
import django
from datetime import time

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cafeterias_sucre.settings')
django.setup()

from core.models import Cafeteria, HorarioCafeteria

def poblar_horarios_mirador_san_miguel():
    """Poblar horarios específicos para Café Mirador San Miguel"""
    try:
        # Buscar la cafetería por nombre (puedes ajustar esto según sea necesario)
        cafeteria = Cafeteria.objects.filter(nombre__icontains="Mirador San Miguel").first()
        
        if not cafeteria:
            print("No se encontró la cafetería 'Mirador San Miguel'")
            # Crear una de ejemplo si no existe
            cafeteria = Cafeteria.objects.create(
                nombre="Café Mirador San Miguel",
                descripcion="Café con vista panorámica de la ciudad de Sucre",
                direccion="Mirador San Miguel, Sucre",
                latitud=-19.0336,
                longitud=-65.2634,
                telefono="",
                zona="Mirador San Miguel",
                precio_promedio=25.00,
                wifi=True,
                terraza=True,
                estacionamiento=False
            )
            print(f"Cafetería creada: {cafeteria.nombre}")
        
        # Eliminar horarios existentes para esta cafetería
        HorarioCafeteria.objects.filter(cafeteria=cafeteria).delete()
        
        # Horarios específicos para Café Mirador San Miguel
        horarios = [
            # Lunes a Sábado: 8 a.m. - 8 p.m.
            (0, time(8, 0), time(20, 0), False),  # Lunes
            (1, time(8, 0), time(20, 0), False),  # Martes
            (2, time(8, 0), time(20, 0), False),  # Miércoles
            (3, time(8, 0), time(20, 0), False),  # Jueves
            (4, time(8, 0), time(20, 0), False),  # Viernes
            (5, time(8, 0), time(20, 0), False),  # Sábado
            (6, None, None, True),                # Domingo - Cerrado
        ]
        
        for dia, apertura, cierre, cerrado in horarios:
            HorarioCafeteria.objects.create(
                cafeteria=cafeteria,
                dia_semana=dia,
                hora_apertura=apertura,
                hora_cierre=cierre,
                cerrado=cerrado
            )
        
        print(f"Horarios actualizados para {cafeteria.nombre}")
        print("Horarios creados:")
        for horario in HorarioCafeteria.objects.filter(cafeteria=cafeteria):
            print(f"  {horario}")
            
    except Exception as e:
        print(f"Error: {e}")

def poblar_horarios_generales():
    """Poblar horarios genéricos para otras cafeterías"""
    cafeterias_sin_horarios = Cafeteria.objects.exclude(
        id__in=HorarioCafeteria.objects.values_list('cafeteria_id', flat=True)
    )
    
    for cafeteria in cafeterias_sin_horarios:
        # Horario genérico: Lunes a Domingo 8:00 - 20:00
        horarios_genericos = [
            (0, time(8, 0), time(20, 0), False),  # Lunes
            (1, time(8, 0), time(20, 0), False),  # Martes
            (2, time(8, 0), time(20, 0), False),  # Miércoles
            (3, time(8, 0), time(20, 0), False),  # Jueves
            (4, time(8, 0), time(20, 0), False),  # Viernes
            (5, time(8, 0), time(20, 0), False),  # Sábado
            (6, time(8, 0), time(20, 0), False),  # Domingo
        ]
        
        for dia, apertura, cierre, cerrado in horarios_genericos:
            HorarioCafeteria.objects.create(
                cafeteria=cafeteria,
                dia_semana=dia,
                hora_apertura=apertura,
                hora_cierre=cierre,
                cerrado=cerrado
            )
        
        print(f"Horarios genéricos creados para: {cafeteria.nombre}")

if __name__ == "__main__":
    print("Poblando horarios detallados...")
    
    # Poblar horarios específicos
    poblar_horarios_mirador_san_miguel()
    
    # Poblar horarios genéricos para el resto
    poblar_horarios_generales()
    
    print("\n¡Horarios poblados exitosamente!")