// Mapa interactivo de cafeterías con Leaflet
let map;
let userLocationMarker;
let cafeteriasMarkers = [];

// Coordenadas de Sucre como centro por defecto
const SUCRE_COORDS = [-19.0478, -65.2595];

// Icono personalizado para cafeterías (taza blanca con fondo café)
const cafeteriaIcon = L.divIcon({
    className: 'custom-cafeteria-icon',
    html: `
        <div style="
            background-color: #8B4513;
            color: white;
            width: 35px;
            height: 35px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 18px;
            box-shadow: 0 3px 6px rgba(0,0,0,0.3);
            border: 3px solid #ffffff;
        ">
            ☕
        </div>
    `,
    iconSize: [35, 35],
    iconAnchor: [17.5, 17.5],
    popupAnchor: [0, -17.5]
});

// Icono personalizado para ubicación actual (exacto como Google Maps)
const userLocationIcon = L.divIcon({
    className: 'user-location-icon-google',
    html: `
        <div class="location-marker">
            <!-- Círculo exterior azul con pulso -->
            <div class="location-pulse"></div>
            <!-- Punto central azul -->
            <div class="location-dot"></div>
        </div>
    `,
    iconSize: [25, 25],
    iconAnchor: [12.5, 12.5]
});

// Inicializar el mapa
function inicializarMapa() {
    try {
        // Crear el mapa centrado en Sucre
        map = L.map('mapa-cafeterias').setView(SUCRE_COORDS, 13);

        // Definir solo 2 capas base: Calles y Satélite
        const capas = {
            // Capa de calles (OpenStreetMap)
            'Calles': L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '© OpenStreetMap contributors',
                maxZoom: 19
            }),
            
            // Capa satelital (Esri World Imagery)
            'Satélite': L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
                attribution: '© Esri, Maxar, GeoEye, Earthstar Geographics, CNES/Airbus DS, USDA, USGS, AeroGRID, IGN, and the GIS User Community',
                maxZoom: 19
            })
        };

        // Agregar la capa por defecto (Calles)
        capas['Calles'].addTo(map);

        // Control de capas EXACTO como Google Maps
        const controlCapas = L.Control.extend({
            onAdd: function(map) {
                const container = L.DomUtil.create('div', 'leaflet-bar leaflet-control google-maps-layer-control');
                
                // Estilos exactos Google Maps
                container.style.cssText = `
                    background: #fff;
                    border: none;
                    border-radius: 2px;
                    box-shadow: 0 2px 6px rgba(0,0,0,.3);
                    padding: 0;
                    font-family: Roboto, Arial, sans-serif;
                    overflow: hidden;
                    min-width: 72px;
                `;
                
                let expanded = false;
                
                container.innerHTML = `
                    <div class="google-layer-control">
                        <button class="google-layer-main-button">
                            <div class="layer-icon-stack">
                                <div class="layer-icon roadmap-icon"></div>
                                <div class="layer-icon satellite-icon"></div>
                            </div>
                            <span class="layer-main-label">Capas</span>
                        </button>
                        <div class="google-layer-options" style="display: none;">
                            <button class="google-layer-option active" data-type="roadmap">
                                <div class="layer-preview roadmap-preview"></div>
                                <span class="layer-label">Mapa</span>
                            </button>
                            <button class="google-layer-option" data-type="satellite">
                                <div class="layer-preview satellite-preview">
                                    <span class="sat-text">SAT</span>
                                </div>
                                <span class="layer-label">Satélite</span>
                            </button>
                        </div>
                    </div>
                `;
                
                const mainButton = container.querySelector('.google-layer-main-button');
                const optionsPanel = container.querySelector('.google-layer-options');
                const options = container.querySelectorAll('.google-layer-option');
                
                // Toggle panel
                mainButton.addEventListener('click', function(e) {
                    e.preventDefault();
                    e.stopPropagation();
                    
                    expanded = !expanded;
                    if (expanded) {
                        optionsPanel.style.display = 'block';
                        container.style.minWidth = '120px';
                    } else {
                        optionsPanel.style.display = 'none';
                        container.style.minWidth = '72px';
                    }
                });
                
                // Option selection
                options.forEach(option => {
                    option.addEventListener('click', function(e) {
                        e.preventDefault();
                        e.stopPropagation();
                        
                        // Skip if already active
                        if (this.classList.contains('active')) {
                            // Hide panel
                            expanded = false;
                            optionsPanel.style.display = 'none';
                            container.style.minWidth = '72px';
                            return;
                        }
                        
                        // Remove active class from all options
                        options.forEach(opt => opt.classList.remove('active'));
                        
                        // Add active class to clicked option
                        this.classList.add('active');
                        
                        const tipo = this.getAttribute('data-type');
                        
                        // Switch layers
                        if (tipo === 'roadmap') {
                            map.eachLayer(layer => {
                                if (layer._url && layer._url.includes('World_Imagery')) {
                                    map.removeLayer(layer);
                                }
                            });
                            let hasStreetLayer = false;
                            map.eachLayer(layer => {
                                if (layer._url && layer._url.includes('openstreetmap')) {
                                    hasStreetLayer = true;
                                }
                            });
                            if (!hasStreetLayer) {
                                capas['Calles'].addTo(map);
                            }
                        } else if (tipo === 'satellite') {
                            map.eachLayer(layer => {
                                if (layer._url && layer._url.includes('openstreetmap')) {
                                    map.removeLayer(layer);
                                }
                            });
                            let hasSatelliteLayer = false;
                            map.eachLayer(layer => {
                                if (layer._url && layer._url.includes('World_Imagery')) {
                                    hasSatelliteLayer = true;
                                }
                            });
                            if (!hasSatelliteLayer) {
                                capas['Satélite'].addTo(map);
                            }
                        }
                        
                        // Hide panel after selection
                        setTimeout(() => {
                            expanded = false;
                            optionsPanel.style.display = 'none';
                            container.style.minWidth = '72px';
                        }, 100);
                    });
                });
                
                // Close panel when clicking outside
                document.addEventListener('click', function(e) {
                    if (!container.contains(e.target) && expanded) {
                        expanded = false;
                        optionsPanel.style.display = 'none';
                        container.style.minWidth = '72px';
                    }
                });
                
                // Prevent click propagation
                L.DomEvent.disableClickPropagation(container);
                
                return container;
            }
        });
        
        // Agregar el control personalizado al mapa
        new controlCapas({ position: 'topright' }).addTo(map);

        // Agregar control de ubicación integrado (estilo Google Maps)
        const controlUbicacion = L.Control.extend({
            onAdd: function(map) {
                const container = L.DomUtil.create('div', 'leaflet-bar leaflet-control');
                
                container.style.backgroundColor = '#fff';
                container.style.border = 'none';
                container.style.borderRadius = '2px';
                container.style.boxShadow = '0 2px 6px rgba(0,0,0,.3)';
                container.style.cursor = 'pointer';
                container.style.width = '40px';
                container.style.height = '40px';
                container.style.display = 'flex';
                container.style.alignItems = 'center';
                container.style.justifyContent = 'center';
                container.style.transition = 'all 0.3s';
                container.title = 'Mostrar tu ubicación';
                
                // Icono de ubicación exacto Google Maps (punto de ubicación)
                container.innerHTML = `
                    <svg width="18" height="18" viewBox="0 0 24 24" style="pointer-events: none;">
                        <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z" fill="#5f6368"/>
                    </svg>
                `;
                
                container.onmouseover = function() {
                    this.style.backgroundColor = '#f5f5f5';
                };
                
                container.onmouseout = function() {
                    this.style.backgroundColor = '#fff';
                };
                
                container.onclick = function() {
                    this.style.backgroundColor = '#e8f0fe';
                    this.innerHTML = `
                        <svg width="18" height="18" viewBox="0 0 24 24" style="pointer-events: none;">
                            <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z" fill="#1a73e8"/>
                        </svg>
                    `;
                    
                    centrarEnUbicacionActual();
                    
                    // Restaurar estilo después de 300ms
                    setTimeout(() => {
                        this.style.backgroundColor = '#fff';
                        this.innerHTML = `
                            <svg width="18" height="18" viewBox="0 0 24 24" style="pointer-events: none;">
                                <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z" fill="#5f6368"/>
                            </svg>
                        `;
                    }, 300);
                };                // Prevenir que el clic se propague al mapa
                L.DomEvent.disableClickPropagation(container);
                
                return container;
            }
        });

        // Agregar el control de ubicación al mapa
        new controlUbicacion({ position: 'topleft' }).addTo(map);

        // Agregar control de escala
        L.control.scale({
            position: 'bottomleft',
            metric: true,
            imperial: false
        }).addTo(map);

        console.log('✅ Mapa inicializado correctamente con 2 capas');
        
        // Obtener ubicación del usuario
        obtenerUbicacionUsuario();
        
        // Cargar cafeterías
        cargarCafeterias();
        
    } catch (error) {
        console.error('❌ Error al inicializar el mapa:', error);
    }
}

// Obtener la ubicación actual del usuario
function obtenerUbicacionUsuario() {
    if (navigator.geolocation) {
        console.log('🔍 Solicitando ubicación del usuario...');
        
        navigator.geolocation.getCurrentPosition(
            function(position) {
                const lat = position.coords.latitude;
                const lng = position.coords.longitude;
                const precision = position.coords.accuracy;
                
                console.log(`📍 Ubicación obtenida: ${lat}, ${lng} (precisión: ${precision}m)`);
                
                // Agregar marcador de ubicación actual
                if (userLocationMarker) {
                    map.removeLayer(userLocationMarker);
                }
                
                userLocationMarker = L.marker([lat, lng], {
                    icon: userLocationIcon,
                    title: 'Tu ubicación actual'
                }).addTo(map);
                
                // NO mostrar popup automáticamente - solo centrar
                // (Eliminado el bindPopup para que no muestre información)
                
            },
            function(error) {
                console.log('⚠️ Error al obtener ubicación:', error.message);
                switch(error.code) {
                    case error.PERMISSION_DENIED:
                        mostrarNotificacion('Permiso de ubicación denegado. El mapa se centrará en Sucre.', 'warning');
                        break;
                    case error.POSITION_UNAVAILABLE:
                        mostrarNotificacion('Ubicación no disponible. El mapa se centrará en Sucre.', 'warning');
                        break;
                    case error.TIMEOUT:
                        mostrarNotificacion('Tiempo agotado al obtener ubicación. El mapa se centrará en Sucre.', 'warning');
                        break;
                }
            },
            {
                enableHighAccuracy: true,
                timeout: 10000,
                maximumAge: 300000 // 5 minutos
            }
        );
    } else {
        console.log('❌ Geolocalización no soportada por este navegador');
        mostrarNotificacion('Tu navegador no soporta geolocalización.', 'info');
    }
}

// Cargar todas las cafeterías
function cargarCafeterias() {
    // Obtener cafeterías desde la variable global (pasada desde Django)
    if (typeof cafeteriasData !== 'undefined' && cafeteriasData.length > 0) {
        console.log(`📍 Cargando ${cafeteriasData.length} cafeterías...`);
        
        // Limpiar marcadores anteriores
        cafeteriasMarkers.forEach(marker => map.removeLayer(marker));
        cafeteriasMarkers = [];
        
        // Agregar marcador para cada cafetería
        cafeteriasData.forEach(cafeteria => {
            try {
                const marker = L.marker(
                    [parseFloat(cafeteria.latitud), parseFloat(cafeteria.longitud)],
                    {
                        icon: cafeteriaIcon,
                        title: cafeteria.nombre
                    }
                ).addTo(map);
                
                // Popup con información de la cafetería
                marker.bindPopup(`
                    <div class="max-w-sm">
                        <h3 class="font-bold text-lg text-coffee-700 mb-2">
                            ☕ ${cafeteria.nombre}
                        </h3>
                        <div class="text-sm text-gray-600 space-y-1">
                            <p><i class="fas fa-map-marker-alt mr-1"></i> ${cafeteria.direccion}</p>
                            <p><i class="fas fa-star mr-1 text-yellow-500"></i> ${cafeteria.calificacion_promedio} 
                               <span class="text-xs">(${cafeteria.total_calificaciones} reseñas)</span></p>
                            <p><i class="fas fa-heart mr-1 text-red-500"></i> ${cafeteria.total_me_gusta} me gusta</p>
                            <p><i class="fas fa-clock mr-1"></i> ${cafeteria.horario}</p>
                            <p><i class="fas fa-phone mr-1"></i> ${cafeteria.telefono || 'No disponible'}</p>
                        </div>
                        <div class="mt-3 flex space-x-2">
                            <button onclick="verDetalleCafeteria(${cafeteria.id})" 
                                    class="bg-coffee-600 hover:bg-coffee-700 text-white px-3 py-1 rounded text-xs transition duration-200">
                                Ver Detalles
                            </button>
                            <button onclick="navegarACafeteria(${cafeteria.latitud}, ${cafeteria.longitud})" 
                                    class="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded text-xs transition duration-200">
                                <i class="fas fa-directions mr-1"></i> Ir
                            </button>
                        </div>
                    </div>
                `);
                
                cafeteriasMarkers.push(marker);
                
            } catch (error) {
                console.error(`❌ Error al crear marcador para ${cafeteria.nombre}:`, error);
            }
        });
        
        console.log(`✅ ${cafeteriasMarkers.length} cafeterías cargadas en el mapa`);
        
    } else {
        console.log('⚠️ No hay datos de cafeterías disponibles');
        mostrarNotificacion('No se pudieron cargar las cafeterías en el mapa.', 'error');
    }
}

// Función para ver detalles de una cafetería
function verDetalleCafeteria(cafeteriaId) {
    window.open(`/cafeteria/${cafeteriaId}/`, '_blank');
}

// Función para navegar a una cafetería
function navegarACafeteria(lat, lng) {
    // Abrir Google Maps con direcciones
    const url = `https://www.google.com/maps/dir/?api=1&destination=${lat},${lng}`;
    window.open(url, '_blank');
}

// Mostrar notificaciones
function mostrarNotificacion(mensaje, tipo = 'info') {
    // Crear elemento de notificación
    const notificacion = document.createElement('div');
    notificacion.className = `
        fixed top-4 right-4 z-50 p-4 rounded-lg shadow-lg max-w-sm transition-all duration-300 transform translate-x-full
        ${tipo === 'error' ? 'bg-red-500 text-white' : 
          tipo === 'warning' ? 'bg-yellow-500 text-white' : 
          tipo === 'success' ? 'bg-green-500 text-white' : 'bg-blue-500 text-white'}
    `;
    notificacion.innerHTML = `
        <div class="flex items-center justify-between">
            <span>${mensaje}</span>
            <button onclick="this.parentElement.parentElement.remove()" class="ml-2 text-white hover:text-gray-200">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `;
    
    document.body.appendChild(notificacion);
    
    // Animar entrada
    setTimeout(() => {
        notificacion.classList.remove('translate-x-full');
    }, 100);
    
    // Auto-remover después de 5 segundos
    setTimeout(() => {
        if (notificacion.parentElement) {
            notificacion.classList.add('translate-x-full');
            setTimeout(() => {
                if (notificacion.parentElement) {
                    notificacion.remove();
                }
            }, 300);
        }
    }, 5000);
}

// Botón para centrar en ubicación actual
function centrarEnUbicacionActual() {
    if (userLocationMarker) {
        map.setView(userLocationMarker.getLatLng(), 16);
        // NO abrir popup - solo centrar en la ubicación
    } else {
        obtenerUbicacionUsuario();
    }
}

// Botón para mostrar todas las cafeterías
function mostrarTodasLasCafeterias() {
    if (cafeteriasMarkers.length > 0) {
        const group = new L.featureGroup(cafeteriasMarkers);
        map.fitBounds(group.getBounds().pad(0.1));
    }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    // Esperar un poco para que el div del mapa esté completamente renderizado
    setTimeout(inicializarMapa, 500);
});