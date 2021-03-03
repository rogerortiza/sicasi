from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from ckeditor.fields import RichTextField
from .fields import OrderField


class Tema(models.Model):
    titulo = models.CharField(max_length=240)
    slug = models.SlugField(max_length=200, unique=True)

    class Meta:
        ordering = ['titulo']

    def __str__(self):
        return self.titulo


class Curso(models.Model):
    propietario = models.ForeignKey(User, related_name='cursos_creados',
                                    on_delete=models.CASCADE)
    tema = models.ForeignKey(Tema, related_name='cursos',
                             on_delete=models.CASCADE)
    nombre = models.CharField(max_length=240)
    slug = models.SlugField(max_length=200, unique=True)
    descripcion = RichTextField()
    duracion = models.CharField(max_length=140, blank=True, null=True)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)
    students = models.ManyToManyField(User, related_name='courses_joined', blank=True)

    class Meta:
        ordering = ['-creado']

    def __str__(self):
        return self.nombre


class Modulo(models.Model):
    curso = models.ForeignKey(Curso, related_name='modulos',
                              on_delete=models.CASCADE)
    titulo = models.CharField(max_length=240)
    descripcion = RichTextField()
    orden = OrderField(blank=True, for_fields=['curso'])

    class Meta:
        ordering = ['orden']

    def __str__(self):
        return f'{self.orden}.- {self.titulo}'


class Contenido(models.Model):
    modulo = models.ForeignKey(Modulo, related_name='contenidos', on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE,
                                     limit_choices_to={'model__in': ('texto',
                                                                     'video',
                                                                     'imagen',
                                                                     'archivo',
                                                                     )})
    object_id = models.PositiveIntegerField()
    item = GenericForeignKey('content_type', 'object_id')
    orden = OrderField(blank=True, for_fields=['modulo'])

    class Meta:
        ordering = ['orden']


class ItemBase(models.Model):
    propietario = models.ForeignKey(User, related_name='%(class)s_relacion', on_delete=models.CASCADE)
    nombre = models.CharField(max_length=240)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.nombre


class Texto(ItemBase):
    contenido = RichTextField(blank=True, null=True)


class Archivo(ItemBase):
    archivo = models.FileField(upload_to='files')


class Imagen(ItemBase):
    archivo = models.FileField(upload_to='images')


class Video(ItemBase):
    url = models.URLField()
