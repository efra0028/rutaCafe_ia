from django.db import models
from django.contrib.auth.models import User


class Conversacion(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_inicio = models.DateTimeField(auto_now_add=True)
    activa = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Conversación de {self.usuario.username} - {self.fecha_inicio}"


class Mensaje(models.Model):
    TIPO_CHOICES = [
        ('U', 'Usuario'),
        ('B', 'Bot'),
    ]
    
    conversacion = models.ForeignKey(Conversacion, on_delete=models.CASCADE, related_name='mensajes')
    tipo = models.CharField(max_length=1, choices=TIPO_CHOICES)
    contenido = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['timestamp']
    
    def __str__(self):
        return f"{self.get_tipo_display()}: {self.contenido[:50]}..."


class PreferenciaUsuario(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    tipo_cafe_preferido = models.CharField(max_length=100, blank=True, null=True)
    ambiente_preferido = models.CharField(max_length=100, blank=True, null=True)
    presupuesto_maximo = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Preferencias de {self.usuario.username}"