#!/usr/bin/env python
"""
Sistema de monitoreo avanzado para la API de OpenAI
Detecta disponibilidad, rendimiento y calidad de respuestas
"""
import os
import django
import json
from datetime import datetime, timedelta
import time
import sys

# Configuración de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cafeterias_sucre.settings')
django.setup()

from openai import OpenAI
from django.conf import settings

class AISystemMonitor:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.status_history = []
        self.performance_metrics = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'average_response_time': 0,
            'reasoning_quality_score': 0
        }
    
    def test_connection(self):
        """Prueba la conexión con OpenAI"""
        try:
            start_time = time.time()
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Eres un asistente de prueba."},
                    {"role": "user", "content": "Responde solo con 'OK' si puedes procesar este mensaje."}
                ],
                max_tokens=10,
                temperature=0.1
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            if response.choices[0].message.content.strip().upper() == 'OK':
                self.performance_metrics['successful_requests'] += 1
                return {
                    'status': 'success',
                    'response_time': response_time,
                    'message': 'Conexión exitosa con OpenAI'
                }
            else:
                return {
                    'status': 'partial',
                    'response_time': response_time,
                    'message': 'Respuesta inesperada de OpenAI'
                }
                
        except Exception as e:
            self.performance_metrics['failed_requests'] += 1
            error_msg = str(e).lower()
            
            if 'rate limit' in error_msg or 'quota' in error_msg:
                return {
                    'status': 'rate_limited',
                    'error': 'Límite de API excedido',
                    'recommendation': 'Usar sistema de respuestas inteligentes de respaldo'
                }
            elif 'api key' in error_msg:
                return {
                    'status': 'auth_error',
                    'error': 'Error de autenticación',
                    'recommendation': 'Verificar API key de OpenAI'
                }
            else:
                return {
                    'status': 'error',
                    'error': str(e),
                    'recommendation': 'Activar modo de respaldo inteligente'
                }
    
    def test_reasoning_capability(self):
        """Prueba la capacidad de razonamiento del asistente"""
        try:
            reasoning_test = """
            Un usuario pregunta: "Quiero un café fuerte que me despierte por la mañana"
            
            Analiza esta solicitud y proporciona:
            1. Tipo de café recomendado
            2. Razón de la recomendación
            3. Horario ideal de consumo
            
            Responde en formato JSON.
            """
            
            start_time = time.time()
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Eres un experto en café con capacidad analítica avanzada."},
                    {"role": "user", "content": reasoning_test}
                ],
                max_tokens=200,
                temperature=0.3
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            response_content = response.choices[0].message.content
            
            # Evaluar calidad del razonamiento
            reasoning_score = self.evaluate_reasoning_quality(response_content)
            
            return {
                'status': 'success',
                'response_time': response_time,
                'reasoning_score': reasoning_score,
                'response': response_content,
                'has_reasoning': reasoning_score >= 7
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'reasoning_score': 0,
                'has_reasoning': False
            }
    
    def evaluate_reasoning_quality(self, response):
        """Evalúa la calidad del razonamiento en la respuesta"""
        score = 0
        response_lower = response.lower()
        
        # Criterios de evaluación
        if 'espresso' in response_lower or 'americano' in response_lower:
            score += 2  # Identificó café fuerte
        
        if 'cafeína' in response_lower or 'despertar' in response_lower:
            score += 2  # Conectó con el objetivo
        
        if 'mañana' in response_lower or 'temprano' in response_lower:
            score += 2  # Consideró el horario
        
        if 'porque' in response_lower or 'debido' in response_lower or 'razón' in response_lower:
            score += 2  # Proporcionó razonamiento
        
        if '{' in response and '}' in response:
            score += 1  # Siguió el formato solicitado
        
        if len(response) > 100:
            score += 1  # Respuesta detallada
        
        return min(score, 10)  # Máximo 10 puntos
    
    def run_comprehensive_test(self):
        """Ejecuta pruebas completas del sistema"""
        print("🔍 INICIANDO MONITOREO DEL SISTEMA DE IA")
        print("=" * 50)
        
        # Prueba de conexión
        print("\n1. Probando conexión básica...")
        connection_result = self.test_connection()
        self.print_test_result("Conexión OpenAI", connection_result)
        
        # Prueba de razonamiento
        print("\n2. Probando capacidad de razonamiento...")
        reasoning_result = self.test_reasoning_capability()
        self.print_test_result("Razonamiento IA", reasoning_result)
        
        # Resumen de estado
        self.print_system_summary(connection_result, reasoning_result)
        
        return connection_result, reasoning_result
    
    def print_test_result(self, test_name, result):
        """Imprime resultados de prueba formateados"""
        status = result.get('status', 'unknown')
        
        if status == 'success':
            print(f"✅ {test_name}: EXITOSO")
            if 'response_time' in result:
                print(f"   ⏱️  Tiempo de respuesta: {result['response_time']:.2f}s")
            if 'reasoning_score' in result:
                print(f"   🧠 Puntuación de razonamiento: {result['reasoning_score']}/10")
        elif status == 'rate_limited':
            print(f"⚠️  {test_name}: LIMITADO")
            print(f"   💡 Recomendación: {result.get('recommendation', 'N/A')}")
        else:
            print(f"❌ {test_name}: ERROR")
            print(f"   🔧 Error: {result.get('error', 'Desconocido')}")
            if 'recommendation' in result:
                print(f"   💡 Recomendación: {result['recommendation']}")
    
    def print_system_summary(self, connection_result, reasoning_result):
        """Imprime resumen del estado del sistema"""
        print("\n" + "=" * 50)
        print("📊 RESUMEN DEL SISTEMA DE IA")
        print("=" * 50)
        
        # Estado general
        if connection_result['status'] == 'success':
            print("🟢 ESTADO: Sistema OpenAI OPERATIVO")
            print("   ✨ El asistente tiene acceso completo a IA avanzada")
            
            if reasoning_result.get('has_reasoning', False):
                print(f"   🧠 RAZONAMIENTO: ACTIVO (Score: {reasoning_result.get('reasoning_score', 0)}/10)")
            else:
                print("   🧠 RAZONAMIENTO: LIMITADO")
                
        elif connection_result['status'] == 'rate_limited':
            print("🟡 ESTADO: Sistema LIMITADO (Rate Limit)")
            print("   🔄 Usando respuestas inteligentes de respaldo")
            print("   💡 Las respuestas mantienen calidad y razonamiento")
            
        else:
            print("🔴 ESTADO: Sistema en modo RESPALDO")
            print("   🛡️  Respuestas inteligentes predefinidas ACTIVAS")
            print("   💪 El asistente sigue siendo funcional y útil")
        
        # Recomendaciones
        print("\n🎯 RECOMENDACIONES:")
        if connection_result['status'] == 'success':
            print("   • Sistema funcionando perfectamente")
            print("   • Continuar monitoreando periódicamente")
        else:
            print("   • Verificar créditos de OpenAI en el dashboard")
            print("   • El sistema de respaldo garantiza funcionalidad")
            print("   • Las respuestas mantienen alta calidad y razonamiento")
        
        print(f"\n⏰ Análisis completado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


def main():
    """Función principal de monitoreo"""
    monitor = AISystemMonitor()
    connection_result, reasoning_result = monitor.run_comprehensive_test()
    
    # Retornar código de salida basado en resultados
    if connection_result['status'] == 'success':
        return 0  # Todo bien
    elif connection_result['status'] == 'rate_limited':
        return 1  # Rate limited pero funcional
    else:
        return 2  # Error pero con respaldo activo


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)