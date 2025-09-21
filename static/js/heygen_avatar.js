// HeyGen Avatar System
let heygenAvatar = null;
let avatarSessionId = null;
let isAvatarSpeaking = false;
let avatarConnected = false;

// Inicializar avatar HeyGen
async function initHeyGenAvatar() {
    console.log('🎭 Inicializando avatar HeyGen...');
    
    try {
        // Crear sesión de streaming
        const response = await fetch('/chat/avatar/crear-sesion/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || ''
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            avatarSessionId = data.session_data.session_id;
            console.log('✅ Sesión HeyGen creada:', avatarSessionId);
            
            // Inicializar avatar con HeyGen Web SDK
            heygenAvatar = new HeyGenWebSDK.Avatar({
                sessionId: avatarSessionId,
                token: data.session_data.token,
                container: document.getElementById('avatar-container'),
                avatarName: data.session_data.avatar_id,
                voice: {
                    voiceId: data.session_data.voice_id,
                    speed: 1.0,
                    emotion: 'friendly'
                }
            });
            
            // Configurar eventos del avatar
            heygenAvatar.on('avatar_ready', () => {
                console.log('✅ Avatar HeyGen listo');
                avatarConnected = true;
                updateAvatarStatus('Avatar conectado');
            });
            
            heygenAvatar.on('avatar_speaking_start', () => {
                console.log('🗣️ Avatar empezando a hablar');
                isAvatarSpeaking = true;
                updateAvatarStatus('Avatar hablando...');
            });
            
            heygenAvatar.on('avatar_speaking_end', () => {
                console.log('🔇 Avatar terminó de hablar');
                isAvatarSpeaking = false;
                updateAvatarStatus('Avatar listo');
            });
            
            heygenAvatar.on('error', (error) => {
                console.error('❌ Error en avatar HeyGen:', error);
                updateAvatarStatus('Error en avatar');
                avatarConnected = false;
            });
            
            // Conectar avatar
            await heygenAvatar.connect();
            
        } else {
            console.error('❌ Error creando sesión HeyGen:', data.error);
            updateAvatarStatus('Error creando avatar');
        }
        
    } catch (error) {
        console.error('❌ Error inicializando HeyGen:', error);
        updateAvatarStatus('Error inicializando avatar');
    }
}

// Enviar texto al avatar HeyGen
async function speakWithHeyGen(text) {
    if (!avatarConnected || !avatarSessionId) {
        console.error('❌ Avatar no conectado');
        return false;
    }
    
    try {
        console.log('🗣️ Enviando texto al avatar:', text.substring(0, 50));
        
        const response = await fetch('/chat/avatar/enviar-texto/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || ''
            },
            body: JSON.stringify({
                session_id: avatarSessionId,
                text: text
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            console.log('✅ Texto enviado al avatar exitosamente');
            return true;
        } else {
            console.error('❌ Error enviando texto al avatar:', data.error);
            return false;
        }
        
    } catch (error) {
        console.error('❌ Error en speakWithHeyGen:', error);
        return false;
    }
}

// Detener avatar HeyGen
async function stopHeyGenAvatar() {
    if (!avatarSessionId) {
        return;
    }
    
    try {
        const response = await fetch('/chat/avatar/detener/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || ''
            },
            body: JSON.stringify({
                session_id: avatarSessionId
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            console.log('✅ Avatar detenido');
            avatarConnected = false;
            avatarSessionId = null;
            heygenAvatar = null;
        } else {
            console.error('❌ Error deteniendo avatar:', data.error);
        }
        
    } catch (error) {
        console.error('❌ Error en stopHeyGenAvatar:', error);
    }
}

// Actualizar estado del avatar
function updateAvatarStatus(status) {
    const statusElement = document.getElementById('avatar-status');
    if (statusElement) {
        statusElement.textContent = status;
    }
    console.log('🎭 Estado del avatar:', status);
}

// Función principal para hablar con el avatar
async function speakText(text) {
    console.log('🔊 speakText llamado con:', text.substring(0, 50));
    
    // Activar expresión de habla en el avatar
    syncAvatarWithVoice(true);
    
    // Intentar HeyGen primero, fallback a navegador
    if (avatarConnected) {
        console.log('🎭 Intentando HeyGen Avatar...');
        const success = await speakWithHeyGen(text);
        if (success) {
            return;
        }
    }
    
    // Fallback a voz del navegador
    console.log('🌐 HeyGen no disponible, usando voz del navegador');
    speakWithBrowser(text);
}

// Sincronizar avatar con voz (simplificado para HeyGen)
function syncAvatarWithVoice(speaking) {
    if (speaking) {
        console.log('🗣️ Avatar sincronizado con voz - hablando');
        // HeyGen maneja automáticamente las expresiones
    } else {
        console.log('🔇 Avatar sincronizado con voz - silencio');
        // HeyGen maneja automáticamente las expresiones
    }
}

// Usar voz del navegador (fallback)
function speakWithBrowser(text) {
    console.log('🌐 Iniciando voz del navegador...');
    
    if (!('speechSynthesis' in window)) {
        console.error('❌ Speech Synthesis no disponible en este navegador');
        updateVoiceStatus('Voz no disponible');
        return;
    }
    
    // Cancelar cualquier síntesis anterior
    speechSynthesis.cancel();
    
    // Crear utterance
    const utterance = new SpeechSynthesisUtterance(text);
    
    // Configurar voz en español
    const voices = speechSynthesis.getVoices();
    const spanishVoice = voices.find(voice => 
        voice.lang.startsWith('es') && voice.name.includes('Spanish')
    ) || voices.find(voice => voice.lang.startsWith('es'));
    
    if (spanishVoice) {
        utterance.voice = spanishVoice;
        console.log('🌐 Usando voz:', spanishVoice.name);
    }
    
    // Configurar parámetros
    utterance.rate = 0.9;
    utterance.pitch = 1.0;
    utterance.volume = 1.0;
    
    // Eventos
    utterance.onstart = () => {
        console.log('🌐 Voz del navegador iniciada');
        updateVoiceStatus('Reproduciendo...');
        syncAvatarWithVoice(true);
    };
    
    utterance.onend = () => {
        console.log('🌐 Voz del navegador terminada');
        updateVoiceStatus('Voz del navegador activada');
        syncAvatarWithVoice(false);
    };
    
    utterance.onerror = (event) => {
        console.error('❌ Error en voz del navegador:', event.error);
        updateVoiceStatus('Error en voz');
        syncAvatarWithVoice(false);
    };
    
    // Reproducir
    speechSynthesis.speak(utterance);
}

// Actualizar estado de voz
function updateVoiceStatus(status) {
    const voiceStatus = document.getElementById('voice-status');
    if (voiceStatus) {
        voiceStatus.textContent = status;
    }
    console.log('🔊 Estado de voz:', status);
}
