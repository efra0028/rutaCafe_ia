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
    horario = models.CharField(max_length=100, default="L-D: 8:00-20:00")
    imagen = models.ImageField(upload_to='cafeterias/', blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    # Campos adicionales para la población de datos
    precio_promedio = models.DecimalField(max_digits=8, decimal_places=2, default=15.00)
    wifi = models.BooleanField(default=True)
    terraza = models.BooleanField(default=False)
    estacionamiento = models.BooleanField(default=False)
    zona = models.CharField(max_length=50, default="Centro")
    
    # Métricas
    calificacion_promedio = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    total_calificaciones = models.PositiveIntegerField(default=0)
    total_me_gusta = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return self.nombre
    
    @property
    def estrellas(self):
        return round(self.calificacion_promedio)

    def get_horarios_detallados(self):
        """Retorna los horarios detallados por día de la semana"""
        horarios = HorarioCafeteria.objects.filter(cafeteria=self).order_by('dia_semana')
        return horarios

    def get_horario_hoy(self):
        """Retorna el horario para el día actual"""
        import datetime
        dia_actual = datetime.datetime.now().weekday()  # 0=Lunes, 6=Domingo
        try:
            horario_hoy = HorarioCafeteria.objects.get(cafeteria=self, dia_semana=dia_actual)
            return horario_hoy
        except HorarioCafeteria.DoesNotExist:
            return None


class HorarioCafeteria(models.Model):
    DIAS_SEMANA = [
        (0, 'Lunes'),
        (1, 'Martes'),
        (2, 'Miércoles'),
        (3, 'Jueves'),
        (4, 'Viernes'),
        (5, 'Sábado'),
        (6, 'Domingo'),
    ]
    
    cafeteria = models.ForeignKey(Cafeteria, on_delete=models.CASCADE, related_name='horarios_detallados')
    dia_semana = models.IntegerField(choices=DIAS_SEMANA)
    hora_apertura = models.TimeField(null=True, blank=True)
    hora_cierre = models.TimeField(null=True, blank=True)
    cerrado = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ['cafeteria', 'dia_semana']
        ordering = ['dia_semana']
    
    def __str__(self):
        if self.cerrado:
            return f"{self.cafeteria.nombre} - {self.get_dia_semana_display()}: Cerrado"
        return f"{self.cafeteria.nombre} - {self.get_dia_semana_display()}: {self.hora_apertura}-{self.hora_cierre}"
    
    def get_horario_display(self):
        if self.cerrado:
            return "Cerrado"
        return f"{self.hora_apertura.strftime('%I %p').lower()}-{self.hora_cierre.strftime('%I %p').lower()}"


class TipoCafe(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    intensidad = models.PositiveIntegerField(default=5, validators=[MinValueValidator(1), MaxValueValidator(10)])
    precio_base = models.DecimalField(max_digits=8, decimal_places=2, default=15.00)
    
    def __str__(self):
        return self.nombre


class Producto(models.Model):
    cafeteria = models.ForeignKey(Cafeteria, on_delete=models.CASCADE, related_name='productos')
    tipo_cafe = models.ForeignKey(TipoCafe, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=8, decimal_places=2)
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True)
    disponible = models.BooleanField(default=True)
    popular = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['cafeteria', 'nombre']
    
    def __str__(self):
        return f"{self.nombre} - {self.cafeteria.nombre}"


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
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recorridos_creados', null=True, blank=True)
    duracion_estimada = models.PositiveIntegerField(help_text="Duración en minutos")
    distancia_total = models.DecimalField(max_digits=8, decimal_places=2, help_text="Distancia en kilómetros")
    dificultad = models.CharField(max_length=50, default="Fácil")
    precio_total = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)
    destacado = models.BooleanField(default=False)
    
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


class DuenoCafeteria(models.Model):
    """Modelo para dueños de cafeterías"""
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente de aprobación'),
        ('aprobado', 'Aprobado'),
        ('rechazado', 'Rechazado'),
    ]
    
    # Datos del usuario
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    # Datos básicos del dueño
    telefono = models.CharField(max_length=20)
    cedula = models.CharField(max_length=20, unique=True)
    direccion_personal = models.CharField(max_length=300)
    
    # Datos de la cafetería
    nombre_cafeteria = models.CharField(max_length=200)
    descripcion_cafeteria = models.TextField()
    direccion_cafeteria = models.CharField(max_length=300)
    telefono_cafeteria = models.CharField(max_length=20)
    horario_atencion = models.CharField(max_length=100, default="L-D: 8:00-20:00")
    
    # Coordenadas (se pueden agregar después)
    latitud = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitud = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    
    # Características
    wifi = models.BooleanField(default=True)
    terraza = models.BooleanField(default=False)
    estacionamiento = models.BooleanField(default=False)
    zona = models.CharField(max_length=50, default="Centro")
    
    # Sistema de aprobación
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    fecha_aprobacion = models.DateTimeField(null=True, blank=True)
    aprobado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='aprobaciones_realizadas')
    
    # Relación con cafetería (se crea después de la aprobación)
    cafeteria = models.OneToOneField(Cafeteria, on_delete=models.CASCADE, null=True, blank=True)
    
    # Comentarios del administrador
    comentarios_admin = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.nombre_cafeteria} ({self.estado})"
    
    @property
    def esta_aprobado(self):
        return self.estado == 'aprobado'
    
    @property
    def esta_pendiente(self):
        return self.estado == 'pendiente'