#!/usr/bin/env python
import os
import sys
import django
from datetime import time

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cafeterias_sucre.settings')
django.setup()

from core.models import Cafeteria, HorarioCafeteria

def actualizar_horario_especifico(nombre_cafeteria, horarios_personalizados):
    """
    Actualizar horarios específicos para una cafetería
    
    Args:
        nombre_cafeteria: Nombre de la cafetería a buscar
        horarios_personalizados: Lista de tuplas (dia_semana, hora_apertura, hora_cierre, cerrado)
    """
    try:
        cafeteria = Cafeteria.objects.filter(nombre__icontains=nombre_cafeteria).first()
        
        if not cafeteria:
            print(f"No se encontró la cafetería '{nombre_cafeteria}'")
            return
        
        # Eliminar horarios existentes
        HorarioCafeteria.objects.filter(cafeteria=cafeteria).delete()
        
        # Crear nuevos horarios
        for dia, apertura, cierre, cerrado in horarios_personalizados:
            HorarioCafeteria.objects.create(
                cafeteria=cafeteria,
                dia_semana=dia,
                hora_apertura=apertura,
                hora_cierre=cierre,
                cerrado=cerrado
            )
        
        print(f"Horarios actualizados para {cafeteria.nombre}")
        for horario in HorarioCafeteria.objects.filter(cafeteria=cafeteria):
            print(f"  {horario}")
            
    except Exception as e:
        print(f"Error: {e}")

def ejemplos_horarios():
    """Ejemplos de cómo usar el script para diferentes tipos de horarios"""
    
    # Ejemplo 1: Café Mirador San Miguel (ya configurado)
    # L-S: 8:00-20:00, Domingo cerrado
    horarios_mirador = [
        (0, time(8, 0), time(20, 0), False),  # Lunes
        (1, time(8, 0), time(20, 0), False),  # Martes
        (2, time(8, 0), time(20, 0), False),  # Miércoles
        (3, time(8, 0), time(20, 0), False),  # Jueves
        (4, time(8, 0), time(20, 0), False),  # Viernes
        (5, time(8, 0), time(20, 0), False),  # Sábado
        (6, None, None, True),                # Domingo - Cerrado
    ]
    
    # Ejemplo 2: Café con horarios extendidos fin de semana
    horarios_weekend = [
        (0, time(7, 0), time(19, 0), False),  # Lunes
        (1, time(7, 0), time(19, 0), False),  # Martes
        (2, time(7, 0), time(19, 0), False),  # Miércoles
        (3, time(7, 0), time(19, 0), False),  # Jueves
        (4, time(7, 0), time(21, 0), False),  # Viernes
        (5, time(8, 0), time(22, 0), False),  # Sábado
        (6, time(8, 0), time(20, 0), False),  # Domingo
    ]
    
    # Ejemplo 3: Café que cierra miércoles
    horarios_miercoles_cerrado = [
        (0, time(8, 0), time(18, 0), False),  # Lunes
        (1, time(8, 0), time(18, 0), False),  # Martes
        (2, None, None, True),                # Miércoles - Cerrado
        (3, time(8, 0), time(18, 0), False),  # Jueves
        (4, time(8, 0), time(18, 0), False),  # Viernes
        (5, time(8, 0), time(18, 0), False),  # Sábado
        (6, time(8, 0), time(18, 0), False),  # Domingo
    ]
    
    # Puedes usar cualquiera de estos ejemplos:
    # actualizar_horario_especifico("Time & Coffee", horarios_weekend)
    # actualizar_horario_especifico("Metro Café", horarios_miercoles_cerrado)
    
    print("Ejemplos de horarios disponibles:")
    print("1. horarios_mirador - L-S: 8:00-20:00, Domingo cerrado")
    print("2. horarios_weekend - L-J: 7:00-19:00, V: 7:00-21:00, S: 8:00-22:00, D: 8:00-20:00")
    print("3. horarios_miercoles_cerrado - L-M, J-D: 8:00-18:00, Miércoles cerrado")
    print("\nPara usar, descomenta las líneas del ejemplo que desees actualizar.")

if __name__ == "__main__":
    print("Script para actualizar horarios específicos de cafeterías")
    print("=" * 50)
    
    # Aquí puedes agregar actualizaciones específicas
    # Por ejemplo, si quieres actualizar otra cafetería:
    
    # Actualizar "Typica Café Sucre" con horarios especiales de fin de semana
    horarios_typica = [
        (0, time(7, 30), time(19, 0), False),  # Lunes
        (1, time(7, 30), time(19, 0), False),  # Martes
        (2, time(7, 30), time(19, 0), False),  # Miércoles
        (3, time(7, 30), time(19, 0), False),  # Jueves
        (4, time(7, 30), time(21, 0), False),  # Viernes
        (5, time(8, 0), time(22, 0), False),   # Sábado
        (6, time(8, 0), time(20, 0), False),   # Domingo
    ]
    
    # Descomenta la siguiente línea para actualizar Typica Café
    # actualizar_horario_especifico("Typica Café", horarios_typica)
    
    # Mostrar ejemplos
    ejemplos_horarios()
    
    print("\n✅ Script ejecutado exitosamente!")
    print("Revisa la página de detalles de las cafeterías para ver los horarios actualizados.")