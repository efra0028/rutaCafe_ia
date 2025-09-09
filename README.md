# ☕ Cafeterías de Sucre - Aplicación Web

Una aplicación web moderna para descubrir las mejores cafeterías de Sucre, Bolivia, con un chatbot inteligente que te ayuda a encontrar tu café perfecto y crear recorridos personalizados.

## 🚀 Características

- **🗺️ Mapa Interactivo**: Visualiza todas las cafeterías en Google Maps con GPS
- **🤖 Chatbot Inteligente**: Asistente de café con OpenAI que recomienda cafeterías
- **📍 Rutas Personalizadas**: Crea recorridos de 4 cafeterías basados en tu ubicación
- **⭐ Sistema de Calificaciones**: Califica y comenta tus experiencias
- **👥 Sistema de Usuarios**: Registro completo con perfil personalizado
- **📊 Estadísticas**: Dashboard con métricas de la comunidad
- **📱 Diseño Responsivo**: Funciona perfectamente en móvil y escritorio

## 🛠️ Tecnologías Utilizadas

### Backend
- **Django 5.2.4** - Framework web
- **SQLite** - Base de datos
- **OpenAI API** - Chatbot inteligente
- **Mapbox API** - Mapas y rutas

### Frontend
- **Tailwind CSS** - Framework de estilos
- **Alpine.js** - JavaScript reactivo
- **Font Awesome** - Iconos
- **Mapbox GL JS** - Mapas interactivos

## 📋 Requisitos

- Python 3.8+
- pip
- Cuenta de Mapbox API
- Cuenta de OpenAI API (opcional, para el chatbot)

## 🚀 Instalación

1. **Clonar el repositorio**
   ```bash
   git clone <url-del-repositorio>
   cd app
   ```

2. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configurar variables de entorno**
   ```bash
   # Crear archivo .env
   OPENAI_API_KEY=tu_clave_de_openai
   MAPBOX_ACCESS_TOKEN=tu_clave_de_mapbox
   ```

4. **Ejecutar migraciones**
   ```bash
   python manage.py migrate
   ```

5. **Poblar la base de datos**
   ```bash
   python populate_data.py
   ```

6. **Crear superusuario**
   ```bash
   python manage.py createsuperuser
   ```

7. **Ejecutar servidor**
   ```bash
   python manage.py runserver
   ```

8. **Acceder a la aplicación**
   - Aplicación: http://localhost:8000
   - Admin: http://localhost:8000/admin

## 🎯 Funcionalidades Principales

### 🏠 Página Principal
- Vista general de todas las cafeterías
- Mapa interactivo con marcadores
- Estadísticas de la comunidad
- Recorridos disponibles

### 🤖 Chatbot Inteligente
- Conversación natural sobre tipos de café
- Recomendaciones personalizadas
- Creación automática de recorridos
- Integración con OpenAI GPT

### 🗺️ Sistema de Mapas
- Geolocalización del usuario
- Cálculo de cafeterías más cercanas
- Rutas optimizadas por distancia
- Navegación paso a paso

### 👤 Sistema de Usuarios
- Registro con datos completos (nombre, email, género, edad, ciudad, país)
- Perfil personalizado
- Historial de recorridos
- Sistema de calificaciones y comentarios

### 📊 Panel de Administración
- Gestión completa de cafeterías
- Administración de usuarios
- Estadísticas detalladas
- Gestión de comentarios y calificaciones

## 🗃️ Estructura de la Base de Datos

### Modelos Principales
- **Cafeteria**: Información de cafeterías (nombre, dirección, coordenadas, horarios)
- **TipoCafe**: Tipos de café disponibles
- **Recorrido**: Recorridos predefinidos
- **RecorridoUsuario**: Recorridos iniciados por usuarios
- **Comentario**: Reseñas y calificaciones
- **PerfilUsuario**: Información adicional del usuario

## 🔧 Configuración de APIs

### Mapbox API
1. Ir a [Mapbox](https://www.mapbox.com/)
2. Crear una cuenta gratuita
3. Ir a la sección "Access tokens"
4. Copiar tu token de acceso público
5. Configurar restricciones de dominio (opcional)

### OpenAI API
1. Ir a [OpenAI Platform](https://platform.openai.com/)
2. Crear una cuenta y obtener API Key
3. Configurar límites de uso
4. Agregar la clave al archivo .env

## 📱 Uso de la Aplicación

### Para Usuarios
1. **Registrarse**: Crear cuenta con datos personales
2. **Explorar**: Ver cafeterías en el mapa
3. **Chatear**: Hablar con el asistente de café
4. **Recorrer**: Iniciar recorridos personalizados
5. **Calificar**: Dejar reseñas y comentarios

### Para Administradores
1. **Acceder al admin**: http://localhost:8000/admin
2. **Gestionar cafeterías**: Agregar, editar, eliminar
3. **Ver estadísticas**: Métricas de uso
4. **Moderar contenido**: Revisar comentarios

## 🎨 Personalización

### Colores
Los colores principales se pueden modificar en `templates/base.html`:
```javascript
colors: {
    'coffee': {
        50: '#fdf7f0',
        100: '#f9e6d3',
        // ... más tonos
    }
}
```

### Datos de Cafeterías
Modificar `populate_data.py` para agregar más cafeterías o cambiar datos existentes.

## 🐛 Solución de Problemas

### Error de Mapbox
- Verificar que el Access Token sea válido
- Comprobar que el token tenga los permisos necesarios
- Revisar restricciones de dominio

### Error del Chatbot
- Verificar la API Key de OpenAI
- Comprobar límites de uso
- Revisar conexión a internet

### Error de Base de Datos
- Ejecutar migraciones: `python manage.py migrate`
- Verificar permisos de archivo SQLite
- Revisar configuración en settings.py

## 📈 Próximas Mejoras

- [ ] Integración con redes sociales
- [ ] Sistema de notificaciones push
- [ ] Modo offline para mapas
- [ ] Integración con sistemas de pago
- [ ] App móvil nativa
- [ ] Sistema de recompensas
- [ ] Integración con delivery

## 🤝 Contribución

1. Fork el proyecto
2. Crear una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 👥 Autores

- **Desarrollador Principal** - [Tu Nombre]
- **Diseño UI/UX** - [Nombre del Diseñador]

## 📞 Contacto

- **Email**: tu-email@ejemplo.com
- **LinkedIn**: [Tu LinkedIn]
- **GitHub**: [Tu GitHub]

---

¡Disfruta explorando las mejores cafeterías de Sucre! ☕✨
