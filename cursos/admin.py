from django.contrib import admin
from .models import Tema, Curso, Modulo


@admin.register(Tema)
class TemaAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'slug']
    prepopulated_fields = {'slug': ('titulo', )}


class ModuloInline(admin.StackedInline):
    model = Modulo


@admin.register(Curso)
class CursoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'tema', 'creado', 'actualizado']
    list_filter = ['creado', 'tema']
    search_fields = ['nombre', 'descripcion']
    prepopulated_fields = {'slug': ('nombre',)}
    inlines = [ModuloInline]
