from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class PerfilUsuario(models.Model):
    GENERO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
        ('O', 'Otro'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    genero = models.CharField(max_length=1, choices=GENERO_CHOICES)
    edad = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(120)])
    ciudad = models.CharField(max_length=100)
    pais = models.CharField(max_length=100)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"


class Cafeteria(models.Model):
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()
    direccion = models.CharField(max_length=300)
    latitud = models.DecimalField(max_digits=10, decimal_places=7)
    longitud = models.DecimalField(max_digits=10, decimal_places=7)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    horario_apertura = models.TimeField()
    horario_cierre = models.TimeField()
    dias_apertura = models.CharField(max_length=100, default="Lunes a Domingo")
    imagen = models.ImageField(upload_to='cafeterias/', blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    # Métricas
    calificacion_promedio = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    total_calificaciones = models.PositiveIntegerField(default=0)
    total_me_gusta = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return self.nombre
    
    @property
    def estrellas(self):
        return round(self.calificacion_promedio)


class TipoCafe(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    
    def __str__(self):
        return self.nombre


class CafeteriaTipoCafe(models.Model):
    cafeteria = models.ForeignKey(Cafeteria, on_delete=models.CASCADE)
    tipo_cafe = models.ForeignKey(TipoCafe, on_delete=models.CASCADE)
    precio = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    disponible = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['cafeteria', 'tipo_cafe']


class Recorrido(models.Model):
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()
    cafeterias = models.ManyToManyField(Cafeteria, through='RecorridoCafeteria')
    duracion_estimada = models.PositiveIntegerField(help_text="Duración en minutos")
    distancia_total = models.DecimalField(max_digits=8, decimal_places=2, help_text="Distancia en kilómetros")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)
    
    def __str__(self):
        return self.nombre


class RecorridoCafeteria(models.Model):
    recorrido = models.ForeignKey(Recorrido, on_delete=models.CASCADE)
    cafeteria = models.ForeignKey(Cafeteria, on_delete=models.CASCADE)
    orden = models.PositiveIntegerField()
    
    class Meta:
        unique_together = ['recorrido', 'cafeteria']
        ordering = ['orden']


class RecorridoUsuario(models.Model):
    ESTADO_CHOICES = [
        ('P', 'Pendiente'),
        ('E', 'En Progreso'),
        ('C', 'Completado'),
        ('A', 'Abandonado'),
    ]
    
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    recorrido = models.ForeignKey(Recorrido, on_delete=models.CASCADE)
    estado = models.CharField(max_length=1, choices=ESTADO_CHOICES, default='P')
    fecha_inicio = models.DateTimeField(auto_now_add=True)
    fecha_completado = models.DateTimeField(blank=True, null=True)
    cafeterias_visitadas = models.ManyToManyField(Cafeteria, blank=True)
    
    def __str__(self):
        return f"{self.usuario.username} - {self.recorrido.nombre}"


class Comentario(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    cafeteria = models.ForeignKey(Cafeteria, on_delete=models.CASCADE)
    comentario = models.TextField()
    calificacion = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.usuario.username} - {self.cafeteria.nombre}"


class MeGusta(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    cafeteria = models.ForeignKey(Cafeteria, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['usuario', 'cafeteria']
    
    def __str__(self):
        return f"{self.usuario.username} le gusta {self.cafeteria.nombre}"