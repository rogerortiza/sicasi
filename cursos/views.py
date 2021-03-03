from braces.views import CsrfExemptMixin, JsonRequestResponseMixin
from django.apps import apps
from django.db.models import Count
from django.shortcuts import redirect, get_object_or_404
from django.forms.models import modelform_factory
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic.base import TemplateResponseMixin, View
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from .forms import ModuloFormSet
from .models import Curso, Modulo, Contenido, Tema
from students.forms import CourseEnrollForm


class OwnerMixin(object):
    def get_queryset(self):
        qs = super(OwnerMixin, self).get_queryset()
        return qs.filter(propietario=self.request.user)


class OwnerEditMixin(object):
    def form_valid(self, form):
        form.instance.propietario = self.request.user
        return super(OwnerEditMixin, self).form_valid(form)


class OwnerCourseMixin(OwnerMixin, LoginRequiredMixin, PermissionRequiredMixin):
    model = Curso
    fields = ['tema', 'nombre', 'slug', 'descripcion']
    success_url = reverse_lazy('manage_curso_list')


class OwnerCourseEditMixin(OwnerCourseMixin, OwnerEditMixin):
    template_name = 'cursos/manage/curso/form.html'


class ManageCourseListView(OwnerCourseMixin, ListView):
    template_name = 'cursos/manage/curso/list.html'
    permission_required = 'cursos.view_curso'


class CourseCreateView(OwnerCourseEditMixin, CreateView):
    permission_required = 'cursos.add_curso'


class CourseUpdateView(OwnerCourseEditMixin, UpdateView):
    permission_required = 'cursos.change_curso'


class CourseDeleteView(OwnerCourseMixin, DeleteView):
    template_name = 'cursos/manage/curso/delete.html'
    permission_required = 'cursos.delete_curso'


class CourseModuleUpdateView(TemplateResponseMixin, View):
    template_name = 'cursos/manage/modulo/formset.html'
    curso = None

    def get_formset(self, data=None):
        return ModuloFormSet(instance=self.curso, data=data)

    def dispatch(self, request, pk):
        self.curso = get_object_or_404(Curso, id=pk, propietario=request.user)
        return super(CourseModuleUpdateView, self).dispatch(request, pk)

    def get(self, request, *args, **kwargs):
        formset = self.get_formset()
        context = {'curso': self.curso, 'formset': formset}
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        formset = self.get_formset(data=request.POST)

        if formset.is_valid():
            formset.save()
            return redirect('manage_curso_list')

        context = {'curso': self.curso, 'formset': formset}
        return self.render_to_response(context)


class ContentCreateUpdateView(TemplateResponseMixin, View):
    modulo = None
    model = None
    obj = None
    template_name = 'cursos/manage/contenido/form.html'

    def get_model(self, model_name):
        print('--  get model --')
        if model_name in ['texto', 'video', 'imagen', 'archivo']:
            return apps.get_model(app_label='cursos', model_name=model_name)
        return None

    def get_form(self, model, *args, **kwargs):
        print('--- get from ---')
        Form = modelform_factory(model, exclude=['propietario', 'orden',
                                                 'creado', 'actualizado'])
        return Form(*args, **kwargs)

    def dispatch(self, request, modulo_id, model_name, id=None):
        self.modulo = get_object_or_404(Modulo, id=modulo_id,
                                        curso__propietario=request.user)
        self.model = self.get_model(model_name)
        print('-- model --')
        print(self.model)

        if id:
            self.obj = get_object_or_404(self.model, id=id, propietario=request.user)

        return super().dispatch(request, modulo_id, model_name, id)

    def get(self, request, modulo_id, model_name, id=None):
        print('--- get ---')
        form = self.get_form(self.model, instance=self.obj)
        return self.render_to_response({'form': form, 'object': self.obj, 'modulo_id': modulo_id})

    def post(self, request, modulo_id, model_name, id=None):
        form = self.get_form(self.model, instance=self.obj, data=request.POST, files=request.FILES)

        if form.is_valid():
            obj = form.save(commit=False)
            obj.propietario = request.user
            obj.save()

            if not id:
                Contenido.objects.create(modulo=self.modulo, item=obj)
            return redirect('modulo_contenido_list', self.modulo.id)

        return self.render_to_response({'form': form, 'object': self.obj})


class ContentDeleteView(View):
    def post(self, request, id):
        content = get_object_or_404(Contenido, id=id, modulo__curso__propietario=request.user)
        module = content.modulo
        content.item.delete()
        content.delete()
        return redirect('modulo_contenido_list', module.id)


class ModuleContentListView(TemplateResponseMixin, View):
    template_name = 'cursos/manage/modulo/contenido_list.html'

    def get(self, request, modulo_id):
        modulo = get_object_or_404(Modulo, id=modulo_id, curso__propietario=request.user)
        return self.render_to_response({'modulo': modulo})


class ModuleOrderView(CsrfExemptMixin, JsonRequestResponseMixin, View):
    def post(self, request):
        for id, order in self.request_json.items():
            Modulo.objects.filter(id=id, curso__propietario=request.user).update(orden=order)
            return self.render_json_response({'saved': 'ok'})


class ContentOrderView(CsrfExemptMixin, JsonRequestResponseMixin, View):
    def post(self, request):
        for id, order in self.request_json.items():
            Contenido.objects.filter(id=id, modulo__curso__propietario=request.user).update(orden=order)
        return self.render_json_response({'saved': 'ok'})


class CourseListView(TemplateResponseMixin, View):
    model = Curso
    context = {}
    template_name = 'cursos/curso/list.html'

    def get(self, request, subject=None):
        subjects = Tema.objects.annotate(total_cursos=Count('cursos'))
        courses = Curso.objects.annotate(total_modules=Count('modulos'))

        print('--- annotate ---')
        print(subjects)

        if subject:
            subject = get_object_or_404(Tema, slug=subject)
            courses = courses.filter(tema=subject)

        self.context.update({'subjects': subjects, 'courses': courses, 'subject': subject})
        return self.render_to_response(self.context)


class CourseDetailView(DetailView):
    model = Curso
    template_name = 'cursos/curso/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['enroll_form'] = CourseEnrollForm(initial={'course': self.object})
        return context
