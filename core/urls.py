from django.urls import path
from . import views

urlpatterns = [
    path('', views.index_redirect, name='index_redirect'),
    path('painel/', views.index, name='painel_principal'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('inscricao/<int:curso_id>/', views.inscricao_create, name='inscricao_create'),
    path('inscricao/<int:inscricao_id>/pdf/', views.gerar_pdf_inscricao, name='gerar_pdf_inscricao'),
    path('minha-conta/', views.minha_conta, name='minha_conta'),
    path('pagamento/', views.pagamento_subscription, name='pagamento_subscription'),
    path('documentos/', views.gestao_documentos, name='gestao_documentos'),
    path('documentos/novo/', views.documento_criar, name='documento_criar'),
    path('documentos/<int:doc_id>/editar/', views.documento_editar, name='documento_editar'),
    path('documentos/<int:doc_id>/deletar/', views.documento_deletar, name='documento_deletar'),
    path('documentos/<int:doc_id>/visualizar/', views.documento_visualizar, name='documento_visualizar'),
    path('documentos/<int:doc_id>/pdf/', views.gerar_pdf_documento, name='gerar_pdf_documento'),
    
    # URLs para Gestão de Cursos
    path('cursos/', views.listar_cursos, name='listar_cursos'),
    path('cursos/novo/', views.criar_curso, name='criar_curso'),
    path('cursos/<int:curso_id>/', views.detalhe_curso, name='detalhe_curso'),
    path('cursos/<int:curso_id>/editar/', views.editar_curso, name='editar_curso'),
    path('cursos/<int:curso_id>/deletar/', views.deletar_curso, name='deletar_curso'),
]
