#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para crear usuarios dueños para todas las cafeterías existentes
"""

import os
import sys
import django

# Configurar Django
if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cafeterias_sucre.settings')
    django.setup()
    
    from django.contrib.auth.models import User
    from core.models import Cafeteria, DuenoCafeteria
    from django.utils import timezone
    
    def crear_usuarios_cafeterias():
        """Crear usuarios para todas las cafeterías existentes"""
        
        cafeterias = Cafeteria.objects.all()
        print(f"🏪 Encontradas {cafeterias.count()} cafeterías")
        print("=" * 50)
        
        usuarios_creados = 0
        usuarios_existentes = 0
        
        for i, cafeteria in enumerate(cafeterias, 1):
            print(f"\n{i}. Procesando: {cafeteria.nombre}")
            
            # Crear username basado en el nombre de la cafetería
            username_base = cafeteria.nombre.lower()
            username_base = username_base.replace(' ', '_')
            username_base = username_base.replace('&', 'y')
            username_base = username_base.replace('-', '_')
            username_base = username_base.replace('café', 'cafe')
            
            # Limpiar caracteres especiales
            import re
            username = re.sub(r'[^a-z0-9_]', '', username_base)
            username = username[:30]  # Límite de Django
            
            # Verificar si ya existe un usuario para esta cafetería
            if DuenoCafeteria.objects.filter(cafeteria=cafeteria).exists():
                print(f"   ⚠️  Ya existe un dueño para esta cafetería")
                usuarios_existentes += 1
                continue
            
            # Verificar si el username ya existe
            counter = 1
            original_username = username
            while User.objects.filter(username=username).exists():
                username = f"{original_username}_{counter}"
                counter += 1
            
            # Crear el usuario
            try:
                user = User.objects.create_user(
                    username=username,
                    email=f"{username}@cafeteria.com",
                    password="password",  # Contraseña temporal
                    first_name=f"Dueño de {cafeteria.nombre}",
                    last_name="",
                    is_active=True
                )
                
                # Crear el perfil de dueño
                dueno = DuenoCafeteria.objects.create(
                    user=user,
                    telefono="70000000",  # Teléfono temporal
                    cedula=f"CI{i:06d}",  # CI temporal
                    direccion_personal="Sucre, Bolivia",
                    nombre_cafeteria=cafeteria.nombre,
                    descripcion_cafeteria=cafeteria.descripcion,
                    direccion_cafeteria=cafeteria.direccion,
                    telefono_cafeteria=cafeteria.telefono or "70000000",
                    horario_atencion=cafeteria.horario,
                    latitud=cafeteria.latitud,
                    longitud=cafeteria.longitud,
                    wifi=cafeteria.wifi,
                    terraza=cafeteria.terraza,
                    estacionamiento=cafeteria.estacionamiento,
                    zona=cafeteria.zona,
                    estado='aprobado',  # Ya aprobado automáticamente
                    fecha_aprobacion=timezone.now(),
                    cafeteria=cafeteria
                )
                
                print(f"   ✅ Usuario creado: {username}")
                print(f"   📧 Email: {user.email}")
                print(f"   🔑 Contraseña: password")
                usuarios_creados += 1
                
            except Exception as e:
                print(f"   ❌ Error creando usuario: {e}")
        
        print("\n" + "=" * 50)
        print("📊 RESUMEN:")
        print(f"✅ Usuarios creados: {usuarios_creados}")
        print(f"⚠️  Ya existían: {usuarios_existentes}")
        print(f"🏪 Total cafeterías: {cafeterias.count()}")
        
        print("\n🔐 CREDENCIALES GENERADAS:")
        print("=" * 50)
        duenos = DuenoCafeteria.objects.filter(estado='aprobado')
        for dueno in duenos:
            print(f"Cafetería: {dueno.nombre_cafeteria}")
            print(f"Usuario: {dueno.user.username}")
            print(f"Email: {dueno.user.email}")
            print(f"Contraseña: password")
            print("-" * 30)
    
    if __name__ == '__main__':
        print("🚀 Iniciando creación de usuarios para cafeterías existentes...")
        crear_usuarios_cafeterias()
        print("\n✅ ¡Script completado exitosamente!")