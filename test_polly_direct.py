#!/usr/bin/env python
"""
Script para probar Amazon Polly directamente
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cafeterias_sucre.settings')
django.setup()

from core.voice_service import voice_service
import base64

def test_polly_direct():
    print("🔊 Probando Amazon Polly directamente...")
    print("=" * 50)
    
    # Verificar si Polly está disponible
    if voice_service.is_available():
        print("✅ Amazon Polly está configurado correctamente")
        
        # Probar con texto corto
        test_text = "Hola, soy Amazon Polly."
        print(f"📝 Texto de prueba: {test_text}")
        
        try:
            audio_base64 = voice_service.text_to_speech(test_text, "Lupe")
            if audio_base64:
                print("✅ Audio generado exitosamente")
                print(f"📊 Tamaño del audio: {len(audio_base64)} caracteres (base64)")
                
                # Guardar audio para verificar
                audio_data = base64.b64decode(audio_base64)
                with open('test_polly_audio.mp3', 'wb') as f:
                    f.write(audio_data)
                print("💾 Audio guardado como 'test_polly_audio.mp3'")
                print("🎵 Puedes reproducir este archivo para verificar la calidad")
                
            else:
                print("❌ Error: No se pudo generar el audio")
                
        except Exception as e:
            print(f"❌ Error al generar audio: {str(e)}")
            
    else:
        print("❌ Amazon Polly NO está configurado")
        print("💡 Verifica tus credenciales en el archivo .env")

if __name__ == "__main__":
    test_polly_direct()

