from django import forms
from cursos.models import Curso


class CourseEnrollForm(forms.Form):
    course = forms.ModelChoiceField(queryset=Curso.objects.all(), widget=forms.HiddenInput)
