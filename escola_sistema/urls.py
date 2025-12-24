from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from core import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('cursos/', views.cursos_lista, name='cursos_lista'),
    path('cursos/novo/', views.curso_create, name='curso_create'),
    path('cursos/<int:curso_id>/editar/', views.curso_edit, name='curso_edit'),
    path('cursos/<int:curso_id>/toggle/', views.curso_toggle, name='curso_toggle'),
    path('admissao/', views.admissao_estudantes, name='admissao_estudantes'),
    path('admissao/inscricao/', views.admissao_inscricao, name='admissao_inscricao'),
    path('inscricao/<int:curso_id>/', views.inscricao_create, name='inscricao_create'),
    path('inscricao/consulta/<str:numero>/', views.inscricao_consulta, name='inscricao_consulta'),
    path('inscricao/buscar/', views.inscricao_buscar, name='inscricao_buscar'),
    path('inscricao/pdf/<str:numero>/', views.gerar_pdf_confirmacao, name='gerar_pdf'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('api/escolas/autocomplete/', views.escolas_autocomplete, name='escolas_autocomplete'),
    path('api/escolas/create/', views.escola_create_ajax, name='escola_create_ajax'),
    path('api/ano-academico/trocar/', views.trocar_ano_academico, name='trocar_ano_academico'),
    path('login/', views.login_view, name='login'),
    path('registro/', views.registro_view, name='registro'),
    path('logout/', views.logout_view, name='logout'),
    path('notificacoes/', views.notificacoes_view, name='notificacoes'),
    path('notificacoes/<int:notificacao_id>/marcar-lida/', views.marcar_notificacao_lida, name='marcar_notificacao_lida'),
    path('api/notificacoes/count/', views.get_notificacoes_count, name='notificacoes_count'),
    path('api/perfis-pendentes/count/', views.get_perfis_pendentes_count, name='perfis_pendentes_count'),
    path('renovar-subscricao/', views.renovar_subscricao_view, name='renovar_subscricao'),
    path('esqueci-senha/', views.esqueci_senha_view, name='esqueci_senha'),
    path('validar-otp/', views.validar_otp_view, name='validar_otp'),
    path('redefinir-senha/<str:token>/', views.redefinir_senha_email_view, name='redefinir_senha_email'),
    path('perfis-pendentes/', views.perfis_pendentes_view, name='perfis_pendentes'),
    path('atribuir-perfil/<int:perfil_id>/', views.atribuir_perfil_view, name='atribuir_perfil'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
