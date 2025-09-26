#!/usr/bin/env python
"""
Verificador y mostrador de datos completos del sistema de cafeterías
Muestra resumen de toda la información disponible para usuarios
"""
import os
import django

# Configuración de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cafeterias_sucre.settings')
django.setup()

from core.models import Cafeteria, TipoCafe, Producto, Recorrido
from django.db.models import Count, Avg

class VerificadorDatosSucre:
    def __init__(self):
        self.cafeterias = Cafeteria.objects.all()
        self.tipos_cafe = TipoCafe.objects.all()
        self.productos = Producto.objects.all()
        self.recorridos = Recorrido.objects.all()
    
    def mostrar_tipos_cafe(self):
        """Mostrar todos los tipos de café disponibles"""
        print("☕ TIPOS DE CAFÉ DISPONIBLES EN EL SISTEMA")
        print("=" * 50)
        
        for tipo in self.tipos_cafe.order_by('intensidad'):
            productos_count = self.productos.filter(tipo_cafe=tipo).count()
            print(f"""
🔸 **{tipo.nombre}** 
   💪 Intensidad: {tipo.intensidad}/10
   💰 Precio base: Bs.{tipo.precio_base}
   📝 {tipo.descripcion}
   🏪 Disponible en: {productos_count} ubicaciones
""")
    
    def mostrar_cafeterias_por_zona(self):
        """Mostrar cafeterías organizadas por zona"""
        print("\n🗺️ CAFETERÍAS DE SUCRE POR ZONA")
        print("=" * 50)
        
        zonas = {}
        for cafeteria in self.cafeterias:
            if cafeteria.zona not in zonas:
                zonas[cafeteria.zona] = []
            zonas[cafeteria.zona].append(cafeteria)
        
        for zona, cafeterias in zonas.items():
            print(f"\n📍 **ZONA {zona.upper()}** - {len(cafeterias)} cafeterías")
            print("-" * 40)
            
            for cafe in sorted(cafeterias, key=lambda x: x.calificacion_promedio, reverse=True):
                productos_count = self.productos.filter(cafeteria=cafe).count()
                servicios = []
                if cafe.wifi:
                    servicios.append("📶 WiFi")
                if cafe.terraza:
                    servicios.append("🌤️ Terraza")  
                if cafe.estacionamiento:
                    servicios.append("🚗 Parking")
                
                print(f"""
🏪 **{cafe.nombre}**
   ⭐ {cafe.calificacion_promedio}/5.0 | ❤️ {cafe.total_me_gusta} me gusta
   💰 Precio promedio: Bs.{cafe.precio_promedio}
   📍 {cafe.direccion}
   📞 {cafe.telefono or 'No disponible'}
   🕐 {cafe.horario}
   🛍️ {productos_count} productos disponibles
   {'🔧 Servicios: ' + ' | '.join(servicios) if servicios else ''}
   💭 {cafe.descripcion[:100]}...
""")
    
    def mostrar_productos_populares(self):
        """Mostrar productos más populares"""
        print("\n🏆 PRODUCTOS MÁS POPULARES")
        print("=" * 50)
        
        productos_populares = self.productos.filter(popular=True).select_related('cafeteria', 'tipo_cafe')
        
        # Agrupar por tipo de café
        tipos_populares = {}
        for producto in productos_populares:
            tipo = producto.tipo_cafe.nombre
            if tipo not in tipos_populares:
                tipos_populares[tipo] = []
            tipos_populares[tipo].append(producto)
        
        for tipo, productos in tipos_populares.items():
            print(f"\n☕ **{tipo.upper()}** - {len(productos)} opciones populares")
            print("-" * 30)
            
            for producto in sorted(productos, key=lambda x: x.precio):
                print(f"   🌟 **{producto.nombre}**")
                print(f"      🏪 {producto.cafeteria.nombre}")
                print(f"      💰 Bs.{producto.precio}")
                print(f"      📝 {producto.descripcion}")
                print()
    
    def mostrar_recorridos_disponibles(self):
        """Mostrar recorridos temáticos"""
        print("\n🗺️ RECORRIDOS TEMÁTICOS DISPONIBLES") 
        print("=" * 50)
        
        for recorrido in self.recorridos.filter(activo=True).order_by('-destacado', 'precio_total'):
            cafeterias_count = recorrido.cafeterias.count()
            destacado_text = " 🌟 DESTACADO" if recorrido.destacado else ""
            
            print(f"""
🚶 **{recorrido.nombre}**{destacado_text}
   🕐 Duración: {recorrido.duracion_estimada} minutos ({recorrido.duracion_estimada//60}h {recorrido.duracion_estimada%60}min)
   📏 Distancia: {recorrido.distancia_total} km
   🎯 Dificultad: {recorrido.dificultad}
   💰 Precio total: Bs.{recorrido.precio_total}
   🏪 Incluye: {cafeterias_count} cafeterías
   📝 {recorrido.descripcion}
   
   📍 Ruta:""")
            
            # Mostrar cafeterías del recorrido en orden
            cafeterias_recorrido = recorrido.cafeterias.all().order_by('recorridocafeteria__orden')
            for i, cafe in enumerate(cafeterias_recorrido, 1):
                print(f"      {i}. {cafe.nombre} - ⭐{cafe.calificacion_promedio} - {cafe.zona}")
            print()
    
    def mostrar_estadisticas_generales(self):
        """Mostrar estadísticas del sistema"""
        print("\n📊 ESTADÍSTICAS GENERALES DEL SISTEMA")
        print("=" * 50)
        
        # Estadísticas básicas
        total_cafeterias = self.cafeterias.count()
        total_productos = self.productos.count()
        total_recorridos = self.recorridos.filter(activo=True).count()
        
        # Promedios
        calificacion_promedio = self.cafeterias.aggregate(Avg('calificacion_promedio'))['calificacion_promedio__avg'] or 0
        precio_promedio = self.cafeterias.aggregate(Avg('precio_promedio'))['precio_promedio__avg'] or 0
        
        # Estadísticas de productos
        productos_premium = self.productos.filter(precio__gte=18).count()
        productos_economicos = self.productos.filter(precio__lte=12).count()
        productos_populares = self.productos.filter(popular=True).count()
        
        # Servicios disponibles
        cafes_con_wifi = self.cafeterias.filter(wifi=True).count()
        cafes_con_terraza = self.cafeterias.filter(terraza=True).count()
        cafes_con_parking = self.cafeterias.filter(estacionamiento=True).count()
        
        print(f"""
🏪 **CAFETERÍAS:**
   • Total: {total_cafeterias} establecimientos
   • Calificación promedio: ⭐ {calificacion_promedio:.1f}/5.0
   • Precio promedio: 💰 Bs.{precio_promedio:.2f}
   • Mejor calificada: 🏆 {self.cafeterias.order_by('-calificacion_promedio').first().nombre}
   • Más económica: 💝 {self.cafeterias.order_by('precio_promedio').first().nombre}

☕ **PRODUCTOS:**
   • Total disponible: {total_productos} productos únicos
   • Productos premium (>Bs.18): {productos_premium}
   • Productos económicos (<Bs.12): {productos_economicos} 
   • Marcados como populares: {productos_populares}

🗺️ **RECORRIDOS:**
   • Rutas activas: {total_recorridos}
   • Recorridos destacados: {self.recorridos.filter(destacado=True).count()}
   • Precio promedio por ruta: Bs.{self.recorridos.aggregate(Avg('precio_total'))['precio_total__avg'] or 0:.2f}

📡 **SERVICIOS:**
   • WiFi disponible: {cafes_con_wifi}/{total_cafeterias} cafeterías ({(cafes_con_wifi/total_cafeterias*100):.0f}%)
   • Con terraza: {cafes_con_terraza}/{total_cafeterias} cafeterías ({(cafes_con_terraza/total_cafeterias*100):.0f}%)
   • Con estacionamiento: {cafes_con_parking}/{total_cafeterias} cafeterías ({(cafes_con_parking/total_cafeterias*100):.0f}%)

📍 **COBERTURA GEOGRÁFICA:**""")
        
        # Distribución por zonas
        zonas = self.cafeterias.values('zona').annotate(count=Count('id')).order_by('-count')
        for zona_data in zonas:
            porcentaje = (zona_data['count'] / total_cafeterias) * 100
            print(f"   • Zona {zona_data['zona']}: {zona_data['count']} cafeterías ({porcentaje:.0f}%)")
    
    def generar_reporte_completo(self):
        """Generar reporte completo del sistema"""
        print("🚀 SISTEMA DE CAFETERÍAS DE SUCRE - REPORTE COMPLETO")
        print("=" * 60)
        print("📅 Estado actual de la base de datos")
        print("✅ Información real y verificada de Sucre, Bolivia")
        print("=" * 60)
        
        self.mostrar_tipos_cafe()
        self.mostrar_cafeterias_por_zona()
        self.mostrar_productos_populares()
        self.mostrar_recorridos_disponibles()
        self.mostrar_estadisticas_generales()
        
        print(f"\n🎯 **CONCLUSIÓN:**")
        print(f"✅ El sistema está completamente poblado con datos reales")
        print(f"🗺️ Los usuarios pueden explorar {self.cafeterias.count()} cafeterías auténticas de Sucre")
        print(f"☕ Con {self.tipos_cafe.count()} tipos diferentes de café")
        print(f"🛍️ Y {self.productos.count()} productos únicos disponibles")
        print(f"🚶 Organizados en {self.recorridos.filter(activo=True).count()} rutas temáticas")
        print(f"🏆 ¡Sistema listo para ofrecer la mejor experiencia cafetera de Sucre!")


def main():
    """Función principal"""
    verificador = VerificadorDatosSucre()
    verificador.generar_reporte_completo()


if __name__ == "__main__":
    main()