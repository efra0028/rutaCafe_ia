#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para probar el sistema de login y redirección de dueños
"""

import os
import sys
import django

# Configurar Django
if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cafeterias_sucre.settings')
    django.setup()
    
    from django.contrib.auth.models import User
    from core.models import DuenoCafeteria
    from django.contrib.auth import authenticate
    
    def probar_dueños():
        """Probar que todos los dueños estén configurados correctamente"""
        
        print("🧪 PROBANDO SISTEMA DE DUEÑOS DE CAFETERÍAS")
        print("=" * 60)
        
        # Obtener algunos dueños para probar
        duenos = DuenoCafeteria.objects.filter(estado='aprobado')[:5]
        
        for dueno in duenos:
            print(f"\n🏪 Probando: {dueno.nombre_cafeteria}")
            print(f"   Usuario: {dueno.user.username}")
            print(f"   Email: {dueno.user.email}")
            print(f"   Activo: {dueno.user.is_active}")
            print(f"   Estado: {dueno.estado}")
            print(f"   Aprobado: {dueno.esta_aprobado}")
            print(f"   Tiene cafetería: {dueno.cafeteria is not None}")
            
            # Probar autenticación
            auth_user = authenticate(username=dueno.user.username, password='password')
            if auth_user:
                print(f"   ✅ Autenticación: EXITOSA")
                
                # Verificar redirección
                if hasattr(auth_user, 'duenocafeteria') and auth_user.duenocafeteria.esta_aprobado:
                    print(f"   ✅ Redirección: Debe ir a panel_dueno")
                else:
                    print(f"   ❌ Redirección: Problema detectado")
            else:
                print(f"   ❌ Autenticación: FALLIDA")
        
        print("\n" + "=" * 60)
        print("🔐 CREDENCIALES PARA PROBAR:")
        print("=" * 60)
        
        for dueno in duenos:
            print(f"Cafetería: {dueno.nombre_cafeteria}")
            print(f"Usuario: {dueno.user.username}")
            print(f"Contraseña: password")
            print(f"URL: http://127.0.0.1:8000/login/")
            print("-" * 40)
    
    if __name__ == '__main__':
        probar_dueños()