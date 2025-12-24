from django.contrib import admin
from .models import ConfiguracaoEscola, Curso, Disciplina, Escola, Inscricao, Professor, Turma, Aluno, Pai, AnoAcademico, PerfilUsuario, Notificacao, Subscricao, PagamentoSubscricao, RecuperacaoSenha

@admin.register(AnoAcademico)
class AnoAcademicoAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'ano_inicio', 'ano_fim', 'ativo', 'data_criacao']
    list_filter = ['ativo', 'data_criacao']
    ordering = ['-ano_inicio']
    
    actions = ['marcar_como_ativo']
    
    def marcar_como_ativo(self, request, queryset):
        # Desativar todos
        AnoAcademico.objects.all().update(ativo=False)
        # Ativar o primeiro selecionado
        if queryset.exists():
            ano = queryset.first()
            ano.ativo = True
            ano.save()
            self.message_user(request, f"Ano acadêmico {ano} marcado como ativo!")
    marcar_como_ativo.short_description = "Marcar como ano ativo"

@admin.register(ConfiguracaoEscola)
class ConfiguracaoEscolaAdmin(admin.ModelAdmin):
    list_display = ['nome_escola', 'telefone', 'email']
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome_escola', 'endereco', 'telefone', 'email', 'logo')
        }),
        ('Templates de Documentos', {
            'fields': ('template_confirmacao_inscricao',)
        }),
    )
    
    def has_add_permission(self, request):
        if ConfiguracaoEscola.objects.exists():
            return False
        return super().has_add_permission(request)
    
    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(Curso)
class CursoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'vagas', 'vagas_disponiveis', 'nota_minima', 'ativo', 'total_inscricoes']
    list_filter = ['ativo', 'data_criacao']
    search_fields = ['nome', 'descricao']
    readonly_fields = ['data_criacao']

@admin.register(Disciplina)
class DisciplinaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'curso', 'carga_horaria']
    list_filter = ['curso']
    search_fields = ['nome', 'curso__nome']

@admin.register(Escola)
class EscolaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'municipio', 'provincia', 'tipo', 'data_cadastro']
    list_filter = ['tipo', 'provincia']
    search_fields = ['nome', 'municipio', 'provincia']
    readonly_fields = ['data_cadastro']

@admin.register(Inscricao)
class InscricaoAdmin(admin.ModelAdmin):
    list_display = ['numero_inscricao', 'nome_completo', 'curso', 'nota_teste', 'aprovado', 'data_inscricao']
    list_filter = ['curso', 'aprovado', 'data_inscricao']
    search_fields = ['numero_inscricao', 'nome_completo', 'bilhete_identidade', 'email']
    readonly_fields = ['numero_inscricao', 'data_inscricao', 'data_resultado']
    fieldsets = (
        ('Informações da Inscrição', {
            'fields': ('numero_inscricao', 'curso', 'data_inscricao')
        }),
        ('Dados Pessoais', {
            'fields': ('nome_completo', 'data_nascimento', 'sexo', 'bilhete_identidade')
        }),
        ('Contato', {
            'fields': ('telefone', 'email', 'endereco')
        }),
        ('Avaliação', {
            'fields': ('nota_teste', 'aprovado', 'data_resultado')
        }),
    )
    
    actions = ['processar_aprovacao']
    
    def processar_aprovacao(self, request, queryset):
        from .views import processar_aprovacoes_curso
        cursos = queryset.values_list('curso', flat=True).distinct()
        for curso_id in cursos:
            processar_aprovacoes_curso(curso_id)
        self.message_user(request, "Aprovações processadas com sucesso!")
    processar_aprovacao.short_description = "Processar aprovação automática"

@admin.register(Professor)
class ProfessorAdmin(admin.ModelAdmin):
    list_display = ['nome_completo', 'bilhete_identidade', 'especialidade', 'telefone', 'email']
    search_fields = ['nome_completo', 'bilhete_identidade', 'especialidade']
    list_filter = ['sexo', 'data_contratacao']

@admin.register(Turma)
class TurmaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'curso', 'ano_letivo', 'professor_titular']
    list_filter = ['curso', 'ano_letivo']
    search_fields = ['nome', 'curso__nome']

@admin.register(Aluno)
class AlunoAdmin(admin.ModelAdmin):
    list_display = ['numero_estudante', 'nome_completo', 'turma', 'telefone', 'email']
    list_filter = ['turma', 'sexo', 'data_matricula']
    search_fields = ['numero_estudante', 'nome_completo', 'bilhete_identidade']
    readonly_fields = ['numero_estudante', 'data_matricula']

@admin.register(Pai)
class PaiAdmin(admin.ModelAdmin):
    list_display = ['nome_completo', 'parentesco', 'telefone', 'email']
    search_fields = ['nome_completo', 'bilhete_identidade']
    filter_horizontal = ['alunos']

@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ['user', 'nivel_acesso', 'telefone', 'ativo', 'data_cadastro', 'status_badge']
    list_filter = ['nivel_acesso', 'ativo', 'data_cadastro']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'telefone']
    readonly_fields = ['data_cadastro']
    list_editable = ['nivel_acesso']
    
    def status_badge(self, obj):
        if obj.nivel_acesso == 'pendente':
            return '⏳ Aguardando Atribuição'
        return '✅ Atribuído'
    status_badge.short_description = 'Status'

@admin.register(Notificacao)
class NotificacaoAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'tipo', 'global_notificacao', 'ativa', 'data_criacao']
    list_filter = ['tipo', 'global_notificacao', 'ativa', 'data_criacao']
    search_fields = ['titulo', 'mensagem']
    filter_horizontal = ['destinatarios', 'lida_por']
    readonly_fields = ['data_criacao']
    fieldsets = (
        ('Informações da Notificação', {
            'fields': ('titulo', 'mensagem', 'tipo', 'ativa')
        }),
        ('Destinatários', {
            'fields': ('global_notificacao', 'destinatarios', 'lida_por')
        }),
        ('Metadata', {
            'fields': ('data_criacao',)
        }),
    )

@admin.register(Subscricao)
class SubscricaoAdmin(admin.ModelAdmin):
    list_display = ['nome_escola', 'plano', 'estado', 'data_inicio', 'data_expiracao', 'dias_restantes', 'esta_ativo']
    list_filter = ['plano', 'estado', 'data_inicio', 'data_expiracao']
    search_fields = ['nome_escola', 'observacoes']
    readonly_fields = ['data_criacao', 'dias_restantes', 'percentual_usado', 'esta_ativo']
    fieldsets = (
        ('Informações da Escola', {
            'fields': ('nome_escola',)
        }),
        ('Dados da Subscrição', {
            'fields': ('plano', 'estado', 'data_inicio', 'data_expiracao', 'valor_pago')
        }),
        ('Status', {
            'fields': ('dias_restantes', 'percentual_usado', 'esta_ativo')
        }),
        ('Observações', {
            'fields': ('observacoes', 'data_criacao')
        }),
    )

@admin.register(PagamentoSubscricao)
class PagamentoSubscricaoAdmin(admin.ModelAdmin):
    list_display = ['id', 'subscricao', 'plano_escolhido', 'valor', 'data_pagamento', 'status', 'data_submissao']
    list_filter = ['status', 'plano_escolhido', 'data_pagamento', 'data_submissao']
    search_fields = ['subscricao__nome_escola', 'numero_referencia', 'observacoes']
    readonly_fields = ['data_submissao', 'aprovado_por', 'data_aprovacao', 'recibo_pdf']
    
    fieldsets = (
        ('Informações do Pagamento', {
            'fields': ('subscricao', 'plano_escolhido', 'valor', 'data_pagamento', 'numero_referencia')
        }),
        ('Comprovante', {
            'fields': ('comprovante',)
        }),
        ('Status', {
            'fields': ('status', 'observacoes')
        }),
        ('Aprovação', {
            'fields': ('aprovado_por', 'data_aprovacao', 'recibo_pdf', 'data_submissao')
        }),
    )
    
    actions = ['aprovar_pagamentos', 'rejeitar_pagamentos']
    
    def aprovar_pagamentos(self, request, queryset):
        from datetime import datetime, timedelta
        from django.utils import timezone
        from .utils import gerar_recibo_pagamento
        
        count = 0
        for pagamento in queryset.filter(status='pendente'):
            pagamento.status = 'aprovado'
            pagamento.aprovado_por = request.user
            pagamento.data_aprovacao = timezone.now()
            
            subscricao = pagamento.subscricao
            if pagamento.plano_escolhido == 'mensal':
                dias = 30
            elif pagamento.plano_escolhido == 'anual':
                dias = 365
            else:
                dias = 30
            
            if subscricao.esta_ativo():
                subscricao.data_expiracao = subscricao.data_expiracao + timedelta(days=dias)
            else:
                subscricao.data_inicio = datetime.now().date()
                subscricao.data_expiracao = datetime.now().date() + timedelta(days=dias)
            
            subscricao.plano = pagamento.plano_escolhido
            subscricao.estado = 'ativo'
            subscricao.valor_pago = pagamento.valor
            subscricao.save()
            
            recibo_path = gerar_recibo_pagamento(pagamento)
            if recibo_path:
                pagamento.recibo_pdf = recibo_path
            
            pagamento.save()
            count += 1
        
        self.message_user(request, f'{count} pagamento(s) aprovado(s) com sucesso!')
    aprovar_pagamentos.short_description = "Aprovar pagamentos selecionados"
    
    def rejeitar_pagamentos(self, request, queryset):
        from django.utils import timezone
        
        count = queryset.filter(status='pendente').update(
            status='rejeitado',
            aprovado_por=request.user,
            data_aprovacao=timezone.now()
        )
        self.message_user(request, f'{count} pagamento(s) rejeitado(s)!')
    rejeitar_pagamentos.short_description = "Rejeitar pagamentos selecionados"

@admin.register(RecuperacaoSenha)
class RecuperacaoSenhaAdmin(admin.ModelAdmin):
    list_display = ['user', 'tipo', 'usado', 'esta_expirado', 'data_criacao', 'data_expiracao']
    list_filter = ['tipo', 'usado', 'data_criacao']
    search_fields = ['user__username', 'email_enviado', 'telefone_enviado']
    readonly_fields = ['data_criacao']
