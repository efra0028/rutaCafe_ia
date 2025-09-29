from django.shortcuts import redirect
from django.urls import reverse


class DuenoRedirectMiddleware:
    """Middleware para redirigir automáticamente a los dueños a su panel"""
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Rutas que no necesitan redirección
        exempt_urls = [
            '/login/', '/logout/', '/registro/', '/registro-dueno/', 
            '/panel-dueno/', '/productos/', '/cafeteria/editar/',
            '/admin/', '/static/', '/media/', '/chat/', '/api/'
        ]
        
        # Si el usuario está autenticado
        if request.user.is_authenticated:
            
            # Si es superusuario, permitir acceso normal
            if request.user.is_superuser:
                pass
            
            # Si es dueño de cafetería aprobado
            elif (hasattr(request.user, 'duenocafeteria') and 
                  request.user.duenocafeteria.esta_aprobado):
                
                # Si está en la página principal, redirigir al panel
                if request.path == '/':
                    return redirect('panel_dueno')
                
                # Si está tratando de acceder a rutas no permitidas para dueños
                forbidden_paths = ['/perfil/', '/estadisticas/', '/completar-perfil/']
                if any(request.path.startswith(path) for path in forbidden_paths):
                    return redirect('panel_dueno')
        
        response = self.get_response(request)
        return response