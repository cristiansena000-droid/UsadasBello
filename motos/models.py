from django.db import models
from django.contrib.auth.models import User

import random

codigo = str(random.randint(100000, 999999))

# Create your models here.
class Moto(models.Model):

    marca = models.CharField(max_length=50)

    linea = models.CharField(
    max_length=100, null=True
    )

    modelo = models.CharField(null=True, max_length=4)

    precio = models.IntegerField()

    cilindraje = models.IntegerField()

    imagen = models.ImageField(upload_to='motos/')

    kilometraje = models.IntegerField(default=0)

    descripcion = models.CharField(
        max_length=500,
        default="Sin descripción"
    )

    placa = models.CharField(
    max_length=10,
    default="Sin placa"
    )


    estado = models.CharField(
        max_length=20,
        default="Pendiente"
    )

    # NUEVOS CAMPOS

    descripcion_larga = models.TextField(
        default="Sin información"
    )

    soat = models.CharField(
        max_length=100,
        default="No especificado"
    )

    tecnomecanica = models.CharField(
        max_length=100,
        default="No especificado"
    )

    transito = models.CharField(
        max_length=100,
        default="No especificado"
    )

    destacado = models.BooleanField(
        default=False
    )

    vistas = models.IntegerField(
    default=0
    )

    def __str__(self):

        return self.marca + " " + self.modelo
    
class ImagenMoto(models.Model):

    moto = models.ForeignKey(
        Moto,
        on_delete=models.CASCADE,
        related_name='imagenes'
    )

    imagen = models.ImageField(
        upload_to='motos/galeria/'
    )

    def __str__(self):

        return self.moto.marca

class Solicitud(models.Model):

    usuario = models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True)

    marca = models.CharField(max_length=50)

    modelo = models.CharField(max_length=50)

    año = models.IntegerField()

    nombre = models.CharField(
        max_length=100,
        default=""
    )

    whatsapp = models.CharField(max_length=30)



    kilometraje = models.IntegerField()

    imagen = models.ImageField(upload_to="solicitudes/")

    fecha = models.DateTimeField(auto_now_add=True)

    

    estado = models.CharField(
        max_length=20,
        default="pendiente"
    )

    

    def __str__(self):

        return self.marca + " " + self.modelo
    

class Favorito(models.Model):

    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    moto = models.ForeignKey(
        Moto,
        on_delete=models.CASCADE
    )

    creado = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        return self.usuario.username
    


class Notificacion(models.Model):

    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    mensaje = models.TextField()

    leida = models.BooleanField(
        default=False
    )

    fecha = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        return self.mensaje
    

class CodigoReset(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    codigo = models.CharField(max_length=6)
    creado = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario.username} - {self.codigo}"
    

class PerfilUsuario(models.Model):

    usuario = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    telefono = models.CharField(
        max_length=20,
        blank=True
    )

    foto = models.ImageField(
        upload_to='perfiles/',
        default='perfiles/default.png'
    )

    def __str__(self):

        return self.usuario.username
    

class Configuracion(models.Model):

    interes_credito = models.FloatField(
        default=18
    )

    def __str__(self):
        return "Configuración"