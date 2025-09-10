"""
Servicio de voz profesional usando Amazon Polly
"""
import boto3
import base64
import io
from django.conf import settings
from django.core.cache import cache
import hashlib


class VoiceService:
    def __init__(self):
        self.polly_client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Inicializar cliente de Amazon Polly"""
        try:
            if settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY:
                self.polly_client = boto3.client(
                    'polly',
                    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                    region_name=settings.AWS_REGION
                )
                print("✅ Amazon Polly configurado correctamente")
            else:
                print("⚠️ Amazon Polly no configurado - usando voz del navegador")
        except Exception as e:
            print(f"❌ Error configurando Amazon Polly: {e}")
            self.polly_client = None
    
    def get_available_voices(self):
        """Obtener voces disponibles en español"""
        if not self.polly_client:
            return []
        
        try:
            response = self.polly_client.describe_voices(LanguageCode='es-ES')
            voices = []
            for voice in response['Voices']:
                voices.append({
                    'id': voice['Id'],
                    'name': voice['Name'],
                    'gender': voice['Gender'],
                    'language': voice['LanguageCode']
                })
            return voices
        except Exception as e:
            print(f"Error obteniendo voces: {e}")
            return []
    
    def text_to_speech(self, text, voice_id=None):
        """
        Convertir texto a audio usando Amazon Polly
        Retorna: base64 del audio o None si hay error
        """
        if not self.polly_client:
            print("❌ Polly client no disponible")
            return None
        
        try:
            # Usar voz por defecto si no se especifica
            if not voice_id:
                voice_id = settings.POLLY_VOICE_ID
            
            print(f"🔊 Generando audio con voz: {voice_id}")
            print(f"📝 Texto: {text[:50]}...")
            
            # Generar audio con Polly (versión optimizada)
            response = self.polly_client.synthesize_speech(
                Text=text,
                OutputFormat='mp3',  # MP3 es más compatible con navegadores
                VoiceId=voice_id,
                Engine='neural'
            )
            
            # Convertir a base64
            audio_data = response['AudioStream'].read()
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')
            
            print(f"✅ Audio generado: {len(audio_base64)} caracteres")
            return audio_base64
            
        except Exception as e:
            print(f"❌ Error en Polly TTS: {e}")
            return None
    
    def _process_text_for_speech(self, text):
        """
        Procesar texto para mejor pronunciación con SSML
        """
        # Convertir a SSML para mejor control
        ssml_text = f"<speak>{text}</speak>"
        
        # Mejorar pronunciación de palabras específicas
        replacements = {
            'cappuccino': 'capuchino',
            'latte': 'laté',
            'espresso': 'espréso',
            'mocha': 'móka',
            'macchiato': 'makiáto',
            'frappé': 'frapé',
            'cortado': 'cortádo',
            'Café': 'Café',
            'Sucre': 'Súcre'
        }
        
        for original, replacement in replacements.items():
            ssml_text = ssml_text.replace(original, replacement)
        
        # Agregar pausas naturales
        ssml_text = ssml_text.replace('. ', '. <break time="0.5s"/>')
        ssml_text = ssml_text.replace(', ', ', <break time="0.3s"/>')
        ssml_text = ssml_text.replace('! ', '! <break time="0.5s"/>')
        ssml_text = ssml_text.replace('? ', '? <break time="0.5s"/>')
        
        # Mejorar pronunciación de números
        ssml_text = ssml_text.replace('4.8', 'cuatro punto ocho')
        ssml_text = ssml_text.replace('4.7', 'cuatro punto siete')
        ssml_text = ssml_text.replace('4.6', 'cuatro punto seis')
        ssml_text = ssml_text.replace('4.5', 'cuatro punto cinco')
        ssml_text = ssml_text.replace('4.9', 'cuatro punto nueve')
        
        return ssml_text
    
    def is_available(self):
        """Verificar si el servicio está disponible"""
        return self.polly_client is not None


# Instancia global del servicio
voice_service = VoiceService()

