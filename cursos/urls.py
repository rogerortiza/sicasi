from django.urls import path
from .views import *


urlpatterns = [
    path('mine/', ManageCourseListView.as_view(), name='manage_curso_list'),
    path('create/', CourseCreateView.as_view(), name='curso_create'),
    path('<pk>/edit/', CourseUpdateView.as_view(), name='curso_edit'),
    path('<pk>/delete/', CourseDeleteView.as_view(), name='curso_delete'),
    path('<pk>/modulo/', CourseModuleUpdateView.as_view(), name='curso_modulo_update'),
    path('modulo/<int:modulo_id>/contenido/<model_name>/create/',
         ContentCreateUpdateView.as_view(), name='modulo_contenido_create'),
    path('modulo/<int:modulo_id>/contenido/<model_name>/<id>/',
         ContentCreateUpdateView.as_view(), name='modulo_contenido_update'),
    path('contenido/<int:id>/delete/', ContentDeleteView.as_view(), name='modulo_contenido_delete'),
    path('modulo/<int:modulo_id>/', ModuleContentListView.as_view(), name='modulo_contenido_list'),
    path('module/order/', ModuleOrderView.as_view(), name='module_order'),
    path('content/order/' ,ContentOrderView.as_view(), name='content_order'),
    path('subject/<slug:subject>/', CourseListView.as_view(), name='course_list_subject'),
    path('<slug:slug>/', CourseDetailView.as_view(), name='course_detail'),
]