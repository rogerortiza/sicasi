from django import forms
from django.forms.models import inlineformset_factory
from .models import Curso, Modulo


ModuloFormSet = inlineformset_factory(Curso, Modulo,
                                      fields=['titulo', 'descripcion'], extra=2,
                                      can_delete=True)
