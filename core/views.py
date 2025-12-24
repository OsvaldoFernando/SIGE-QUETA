from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from .models import Curso, Inscricao, ConfiguracaoEscola, Escola, AnoAcademico, Notificacao, PerfilUsuario, Subscricao, PagamentoSubscricao, RecuperacaoSenha
from django.views.decorators.http import require_http_methods
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.db import IntegrityError
import json
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from io import BytesIO
from datetime import datetime
from django.conf import settings
import os

def processar_aprovacoes_curso(curso_id):
    curso = Curso.objects.get(id=curso_id)
    inscricoes_com_nota = curso.inscricoes.filter(nota_teste__isnull=False, nota_teste__gte=curso.nota_minima).order_by('-nota_teste')
    
    for inscricao in curso.inscricoes.all():
        inscricao.aprovado = False
        inscricao.save()
    
    vagas_disponiveis = curso.vagas
    for i, inscricao in enumerate(inscricoes_com_nota):
        if i < vagas_disponiveis:
            inscricao.aprovado = True
            inscricao.data_resultado = timezone.now()
            inscricao.save()

@login_required
def index(request):
    cursos = Curso.objects.filter(ativo=True)
    config = ConfiguracaoEscola.objects.first()
    anos_academicos = AnoAcademico.objects.all()
    ano_atual = AnoAcademico.objects.filter(ativo=True).first()
    
    # Se não houver ano ativo, pegar o mais recente
    if not ano_atual and anos_academicos.exists():
        ano_atual = anos_academicos.first()
    
    return render(request, 'core/index.html', {
        'cursos': cursos,
        'config': config,
        'anos_academicos': anos_academicos,
        'ano_atual': ano_atual
    })

def inscricao_create(request, curso_id):
    curso = get_object_or_404(Curso, id=curso_id, ativo=True)
    
    if request.method == 'POST':
        # Validar BI único
        bilhete_identidade = request.POST.get('bilhete_identidade')
        if bilhete_identidade and Inscricao.objects.filter(bilhete_identidade=bilhete_identidade).exists():
            messages.error(request, 'Este Bilhete de Identidade já está registrado no sistema!')
            return render(request, 'core/inscricao_form.html', {'curso': curso})
        
        # Validar email único em inscrições
        email = request.POST.get('email')
        if email and Inscricao.objects.filter(email=email).exists():
            messages.error(request, 'Este email já está sendo usado em outra inscrição!')
            return render(request, 'core/inscricao_form.html', {'curso': curso})
        
        # Validar telefone único em inscrições
        telefone = request.POST.get('telefone')
        if telefone and Inscricao.objects.filter(telefone=telefone).exists():
            messages.error(request, 'Este telefone já está sendo usado em outra inscrição!')
            return render(request, 'core/inscricao_form.html', {'curso': curso})
        
        # Obter escola
        escola_id = request.POST.get('escola_id')
        escola = None
        if escola_id:
            try:
                escola = Escola.objects.get(id=escola_id)
            except Escola.DoesNotExist:
                pass
        
        inscricao = Inscricao(
            curso=curso,
            # 1. Informações Pessoais
            nome_completo=request.POST['nome_completo'],
            data_nascimento=request.POST['data_nascimento'],
            local_nascimento=request.POST['local_nascimento'],
            nacionalidade=request.POST['nacionalidade'],
            bilhete_identidade=request.POST['bilhete_identidade'],
            data_validade_bi=request.POST.get('data_validade_bi') or None,
            sexo=request.POST['sexo'],
            estado_civil=request.POST.get('estado_civil', 'S'),
            endereco=request.POST['endereco'],
            telefone=request.POST['telefone'],
            email=request.POST['email'],
            # 2. Informações Académicas
            escola=escola,
            ano_conclusao=request.POST['ano_conclusao'],
            certificados_obtidos=request.POST.get('certificados_obtidos', ''),
            historico_escolar=request.POST.get('historico_escolar', ''),
            turno_preferencial=request.POST.get('turno_preferencial', 'M'),
            # 3. Informações Financeiras
            numero_comprovante=request.POST.get('numero_comprovante', ''),
            responsavel_financeiro_nome=request.POST.get('responsavel_financeiro_nome', ''),
            responsavel_financeiro_telefone=request.POST.get('responsavel_financeiro_telefone', ''),
            responsavel_financeiro_relacao=request.POST.get('responsavel_financeiro_relacao', ''),
            # 4. Encarregado de Educação
            encarregado_nome=request.POST.get('encarregado_nome', ''),
            encarregado_parentesco=request.POST.get('encarregado_parentesco', ''),
            encarregado_telefone=request.POST.get('encarregado_telefone', ''),
            encarregado_email=request.POST.get('encarregado_email', ''),
            encarregado_profissao=request.POST.get('encarregado_profissao', ''),
            encarregado_local_trabalho=request.POST.get('encarregado_local_trabalho', ''),
        )
        
        inscricao.save()
        messages.success(request, f'Inscrição realizada com sucesso! Seu número de inscrição é: {inscricao.numero_inscricao}')
        return redirect('inscricao_consulta', numero=inscricao.numero_inscricao)
    
    return render(request, 'core/inscricao_form.html', {'curso': curso})

def inscricao_consulta(request, numero):
    inscricao = get_object_or_404(Inscricao, numero_inscricao=numero)
    return render(request, 'core/inscricao_consulta.html', {'inscricao': inscricao})

def inscricao_buscar(request):
    if request.method == 'POST':
        numero = request.POST.get('numero_inscricao', '').strip()
        if numero:
            try:
                inscricao = Inscricao.objects.get(numero_inscricao=numero)
                return redirect('inscricao_consulta', numero=numero)
            except Inscricao.DoesNotExist:
                messages.error(request, 'Número de inscrição não encontrado!')
    
    return render(request, 'core/inscricao_buscar.html')

def gerar_pdf_confirmacao(request, numero):
    inscricao = get_object_or_404(Inscricao, numero_inscricao=numero)
    config = ConfiguracaoEscola.objects.first()
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=2*cm, bottomMargin=2*cm)
    story = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor='#1a1a1a',
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor='#333333',
        spaceAfter=12,
        alignment=TA_LEFT
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=11,
        textColor='#000000',
        spaceAfter=8,
        alignment=TA_LEFT
    )
    
    logo_path = os.path.join(settings.BASE_DIR, 'core', 'static', 'core', 'images', 'siga-logo.png')
    if os.path.exists(logo_path):
        try:
            img = Image(logo_path, width=4*cm, height=1.5*cm)
            img.hAlign = 'CENTER'
            story.append(img)
            story.append(Spacer(1, 0.5*cm))
        except:
            pass
    
    escola_nome = config.nome_escola if config else "Sistema Escolar"
    story.append(Paragraph(escola_nome, title_style))
    story.append(Paragraph("CONFIRMAÇÃO DE INSCRIÇÃO", heading_style))
    story.append(Spacer(1, 0.5*cm))
    
    if config and config.template_confirmacao_inscricao:
        template = config.template_confirmacao_inscricao
    else:
        template = "CONFIRMAÇÃO DE INSCRIÇÃO\n\nNome: {nome}\nCurso: {curso}\nNúmero de Inscrição: {numero}\nData: {data}"
    
    conteudo = template.format(
        nome=inscricao.nome_completo,
        curso=inscricao.curso.nome,
        numero=inscricao.numero_inscricao,
        data=inscricao.data_inscricao.strftime('%d/%m/%Y')
    )
    
    for linha in conteudo.split('\n'):
        if linha.strip():
            story.append(Paragraph(linha, normal_style))
    
    story.append(Spacer(1, 1*cm))
    story.append(Paragraph(f"Data de Nascimento: {inscricao.data_nascimento.strftime('%d/%m/%Y')}", normal_style))
    story.append(Paragraph(f"Bilhete de Identidade: {inscricao.bilhete_identidade}", normal_style))
    story.append(Paragraph(f"Telefone: {inscricao.telefone}", normal_style))
    story.append(Paragraph(f"Email: {inscricao.email}", normal_style))
    
    if inscricao.nota_teste is not None:
        story.append(Spacer(1, 0.5*cm))
        story.append(Paragraph(f"Nota do Teste: {inscricao.nota_teste}", normal_style))
        status = "APROVADO" if inscricao.aprovado else "NÃO APROVADO"
        story.append(Paragraph(f"Status: {status}", normal_style))
    
    doc.build(story)
    
    buffer.seek(0)
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="confirmacao_{inscricao.numero_inscricao}.pdf"'
    
    return response

@login_required
def admissao_estudantes(request):
    cursos = Curso.objects.filter(ativo=True)
    config = ConfiguracaoEscola.objects.first()
    return render(request, 'core/admissao.html', {
        'cursos': cursos,
        'config': config
    })

@login_required
def admissao_inscricao(request):
    cursos = Curso.objects.filter(ativo=True)
    config = ConfiguracaoEscola.objects.first()
    
    if request.method == 'POST':
        curso_id = request.POST.get('curso_id')
        if curso_id:
            return redirect('inscricao_create', curso_id=curso_id)
    
    return render(request, 'core/admissao_inscricao.html', {
        'cursos': cursos,
        'config': config
    })

@login_required
def cursos_lista(request):
    cursos = Curso.objects.all().order_by('-ativo', 'nome')
    return render(request, 'core/cursos_lista.html', {'cursos': cursos})

@login_required
def curso_create(request):
    if request.method == 'POST':
        curso = Curso(
            nome=request.POST['nome'],
            descricao=request.POST['descricao'],
            vagas=request.POST['vagas'],
            nota_minima=request.POST['nota_minima'],
            ativo='ativo' in request.POST
        )
        curso.save()
        messages.success(request, f'Curso "{curso.nome}" cadastrado com sucesso!')
        return redirect('cursos_lista')
    
    return render(request, 'core/curso_form.html')

@login_required
def curso_edit(request, curso_id):
    curso = get_object_or_404(Curso, id=curso_id)
    
    if request.method == 'POST':
        curso.nome = request.POST['nome']
        curso.descricao = request.POST['descricao']
        curso.vagas = request.POST['vagas']
        curso.nota_minima = request.POST['nota_minima']
        curso.ativo = 'ativo' in request.POST
        curso.save()
        messages.success(request, f'Curso "{curso.nome}" atualizado com sucesso!')
        return redirect('cursos_lista')
    
    return render(request, 'core/curso_form.html', {'curso': curso})

@login_required
def curso_toggle(request, curso_id):
    curso = get_object_or_404(Curso, id=curso_id)
    curso.ativo = not curso.ativo
    curso.save()
    
    status = "ativado" if curso.ativo else "desativado"
    messages.success(request, f'Curso "{curso.nome}" {status} com sucesso!')
    return redirect('cursos_lista')

@login_required
def dashboard(request):
    cursos = Curso.objects.all()
    total_inscricoes = Inscricao.objects.count()
    total_aprovados = Inscricao.objects.filter(aprovado=True).count()
    total_reprovados = Inscricao.objects.filter(aprovado=False, nota_teste__isnull=False).count()
    aguardando_nota = Inscricao.objects.filter(nota_teste__isnull=True).count()
    
    return render(request, 'core/dashboard.html', {
        'cursos': cursos,
        'total_inscricoes': total_inscricoes,
        'total_aprovados': total_aprovados,
        'total_reprovados': total_reprovados,
        'aguardando_nota': aguardando_nota
    })

@require_http_methods(["GET"])
def escolas_autocomplete(request):
    """Retorna escolas para autocomplete"""
    query = request.GET.get('q', '')
    escolas = Escola.objects.filter(nome__icontains=query)[:10]
    
    resultados = [
        {
            'id': escola.id,
            'nome': escola.nome,
            'municipio': escola.municipio,
            'provincia': escola.provincia
        }
        for escola in escolas
    ]
    
    return JsonResponse({'escolas': resultados})

@require_http_methods(["POST"])
def escola_create_ajax(request):
    """Cria uma escola via AJAX"""
    try:
        data = json.loads(request.body)
        nome = data.get('nome', '').strip()
        municipio = data.get('municipio', '').strip()
        provincia = data.get('provincia', '').strip()
        tipo = data.get('tipo', 'Pública')
        
        if not nome:
            return JsonResponse({'success': False, 'error': 'Nome da escola é obrigatório'}, status=400)
        
        escola = Escola.objects.create(
            nome=nome,
            municipio=municipio,
            provincia=provincia,
            tipo=tipo
        )
        
        return JsonResponse({
            'success': True,
            'escola': {
                'id': escola.id,
                'nome': escola.nome,
                'municipio': escola.municipio,
                'provincia': escola.provincia
            }
        })
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

@require_http_methods(["POST"])
def trocar_ano_academico(request):
    """Trocar ano acadêmico ativo"""
    try:
        ano_id = request.POST.get('ano_id')
        if not ano_id:
            return JsonResponse({'success': False, 'error': 'ID do ano não fornecido'}, status=400)
        
        ano = get_object_or_404(AnoAcademico, id=ano_id)
        
        # Desativar todos os anos
        AnoAcademico.objects.all().update(ativo=False)
        
        # Ativar o ano selecionado
        ano.ativo = True
        ano.save()
        
        return JsonResponse({
            'success': True,
            'ano': str(ano)
        })
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

def login_view(request):
    """View de login personalizada"""
    from .models import Subscricao
    
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if hasattr(user, 'perfil') and user.perfil.nivel_acesso == 'pendente':
                messages.warning(request, 'Sua conta está aguardando aprovação do administrador. Você receberá acesso assim que seu perfil for atribuído.')
                return render(request, 'core/login.html')
            
            subscricao = Subscricao.objects.filter(estado__in=['ativo', 'teste']).first()
            
            if subscricao and not subscricao.esta_ativo():
                messages.error(request, 'Subscrição vencida! Por favor, renove a subscrição para continuar usando o sistema.')
                return redirect('renovar_subscricao')
            elif not subscricao:
                messages.error(request, 'Nenhuma subscrição encontrada! Por favor, configure a subscrição para usar o sistema.')
                return render(request, 'core/login.html')
            
            auth_login(request, user)
            messages.success(request, f'Bem-vindo, {user.get_full_name() or user.username}!')
            next_url = request.GET.get('next', 'dashboard')
            return redirect(next_url)
        else:
            messages.error(request, 'Usuário ou senha inválidos!')
    
    return render(request, 'core/login.html')

def registro_view(request):
    """View de registro de usuário"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        telefone = request.POST.get('telefone')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        
        if password1 != password2:
            messages.error(request, 'As senhas não coincidem!')
            return render(request, 'core/registro.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Nome de usuário já existe!')
            return render(request, 'core/registro.html')
        
        if email and User.objects.filter(email=email).exists():
            messages.error(request, 'Este email já está sendo usado por outro usuário!')
            return render(request, 'core/registro.html')
        
        if telefone and PerfilUsuario.objects.filter(telefone=telefone).exists():
            messages.error(request, 'Este telefone já está sendo usado por outro usuário!')
            return render(request, 'core/registro.html')
        
        for user in User.objects.all():
            if user.check_password(password1):
                messages.error(request, 'Esta senha já está sendo usada por outro usuário. Por favor, escolha uma senha diferente.')
                return render(request, 'core/registro.html')
        
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1,
                first_name=first_name,
                last_name=last_name
            )
            
            if hasattr(user, 'perfil'):
                user.perfil.telefone = telefone
                user.perfil.save()
                messages.success(request, 'Registro realizado com sucesso! Aguarde a aprovação do administrador para acessar o sistema.')
                return redirect('login')
            else:
                messages.error(request, 'Erro: Perfil de usuário já existe. Entre em contato com o administrador.')
                user.delete()
                return render(request, 'core/registro.html')
                
        except IntegrityError:
            messages.error(request, 'Erro: Perfil de usuário já existe para este usuário. Entre em contato com o administrador.')
            return render(request, 'core/registro.html')
        except Exception as e:
            messages.error(request, f'Erro ao criar conta. Por favor, tente novamente.')
            return render(request, 'core/registro.html')
    
    return render(request, 'core/registro.html')

def logout_view(request):
    """View de logout"""
    auth_logout(request)
    messages.success(request, 'Você saiu do sistema com sucesso!')
    return redirect('login')

@login_required
def notificacoes_view(request):
    """View para listar notificações do usuário"""
    notificacoes = Notificacao.objects.filter(
        Q(global_notificacao=True) | Q(destinatarios=request.user),
        ativa=True
    ).distinct().order_by('-data_criacao')
    
    nao_lidas = notificacoes.exclude(lida_por=request.user)
    
    context = {
        'notificacoes': notificacoes,
        'nao_lidas_count': nao_lidas.count()
    }
    return render(request, 'core/notificacoes.html', context)

@login_required
@require_http_methods(["POST"])
def marcar_notificacao_lida(request, notificacao_id):
    """Marcar notificação como lida"""
    notificacao = get_object_or_404(Notificacao, id=notificacao_id)
    notificacao.marcar_como_lida(request.user)
    return JsonResponse({'success': True})

@login_required
def get_notificacoes_count(request):
    """Retorna contagem de notificações não lidas"""
    count = Notificacao.objects.filter(
        Q(global_notificacao=True) | Q(destinatarios=request.user),
        ativa=True
    ).exclude(lida_por=request.user).distinct().count()
    
    return JsonResponse({'count': count})

def pagamento_subscricao_view(request):
    """View para efetuar pagamento de subscrição"""
    from datetime import datetime
    
    subscricao = Subscricao.objects.filter(estado__in=['ativo', 'teste']).first()
    
    if not subscricao:
        messages.error(request, 'Nenhuma subscrição encontrada no sistema!')
        return redirect('login')
    
    if request.method == 'POST':
        plano = request.POST.get('plano')
        valor = request.POST.get('valor')
        data_pagamento = request.POST.get('data_pagamento')
        numero_referencia = request.POST.get('numero_referencia', '')
        comprovante = request.FILES.get('comprovante')
        observacoes = request.POST.get('observacoes', '')
        
        if not all([plano, valor, data_pagamento, comprovante]):
            messages.error(request, 'Por favor, preencha todos os campos obrigatórios!')
            return render(request, 'core/pagamento_subscricao.html', {'subscricao': subscricao})
        
        pagamento = PagamentoSubscricao.objects.create(
            subscricao=subscricao,
            plano_escolhido=plano,
            valor=valor,
            data_pagamento=datetime.strptime(data_pagamento, '%Y-%m-%d').date(),
            numero_referencia=numero_referencia,
            comprovante=comprovante,
            observacoes=observacoes,
            status='pendente'
        )
        
        messages.success(request, f'Pagamento registrado com sucesso! Número de referência: {pagamento.id:06d}. Aguarde a aprovação do administrador.')
        return redirect('login')
    
    return render(request, 'core/pagamento_subscricao.html', {'subscricao': subscricao})

def renovar_subscricao_view(request):
    """View pública para renovação de subscrição"""
    from datetime import datetime
    
    subscricao = Subscricao.objects.filter(estado__in=['ativo', 'teste']).first()
    
    if not subscricao:
        messages.error(request, 'Nenhuma subscrição encontrada no sistema!')
        return redirect('login')
    
    if request.method == 'POST':
        plano = request.POST.get('plano')
        valor = request.POST.get('valor')
        data_pagamento = request.POST.get('data_pagamento')
        numero_referencia = request.POST.get('numero_referencia', '')
        comprovante = request.FILES.get('comprovante')
        observacoes = request.POST.get('observacoes', '')
        
        if not all([plano, valor, data_pagamento, comprovante]):
            messages.error(request, 'Por favor, preencha todos os campos obrigatórios!')
            return render(request, 'core/renovar_subscricao.html', {'subscricao': subscricao})
        
        pagamento = PagamentoSubscricao.objects.create(
            subscricao=subscricao,
            plano_escolhido=plano,
            valor=valor,
            data_pagamento=datetime.strptime(data_pagamento, '%Y-%m-%d').date(),
            numero_referencia=numero_referencia,
            comprovante=comprovante,
            observacoes=observacoes,
            status='pendente'
        )
        
        messages.success(request, f'Pagamento registrado com sucesso! Número de referência: {pagamento.id:06d}. Aguarde a aprovação do administrador.')
        return redirect('login')
    
    return render(request, 'core/renovar_subscricao.html', {'subscricao': subscricao})

def esqueci_senha_view(request):
    """View para escolher método de recuperação de senha"""
    if request.method == 'POST':
        identificador = request.POST.get('identificador')
        metodo = request.POST.get('metodo')
        
        try:
            user = User.objects.filter(Q(username=identificador) | Q(email=identificador)).first()
            
            if not user:
                messages.error(request, 'Usuário não encontrado!')
                return render(request, 'core/esqueci_senha.html')
            
            perfil = PerfilUsuario.objects.filter(user=user).first()
            
            if metodo == 'telefone':
                if not perfil or not perfil.telefone:
                    messages.error(request, 'Este usuário não possui telefone cadastrado!')
                    return render(request, 'core/esqueci_senha.html')
                
                import random
                from datetime import timedelta
                from django.utils import timezone
                
                codigo_otp = str(random.randint(100000, 999999))
                
                recuperacao = RecuperacaoSenha.objects.create(
                    user=user,
                    tipo='telefone',
                    codigo_otp=codigo_otp,
                    telefone_enviado=perfil.telefone,
                    data_expiracao=timezone.now() + timedelta(minutes=10)
                )
                
                request.session['recuperacao_id'] = recuperacao.id
                messages.info(request, f'Código OTP enviado para o telefone {perfil.telefone}')
                return redirect('validar_otp')
                
            elif metodo == 'email':
                if not user.email:
                    messages.error(request, 'Este usuário não possui email cadastrado!')
                    return render(request, 'core/esqueci_senha.html')
                
                import secrets
                from datetime import timedelta
                from django.utils import timezone
                
                token = secrets.token_urlsafe(32)
                
                recuperacao = RecuperacaoSenha.objects.create(
                    user=user,
                    tipo='email',
                    token=token,
                    email_enviado=user.email,
                    data_expiracao=timezone.now() + timedelta(hours=1)
                )
                
                messages.info(request, f'Link de recuperação enviado para {user.email}')
                return redirect('login')
        
        except Exception as e:
            messages.error(request, f'Erro ao processar recuperação: {str(e)}')
    
    return render(request, 'core/esqueci_senha.html')

def validar_otp_view(request):
    """View para validar código OTP e redefinir senha"""
    recuperacao_id = request.session.get('recuperacao_id')
    
    if not recuperacao_id:
        messages.error(request, 'Sessão expirada! Solicite nova recuperação.')
        return redirect('esqueci_senha')
    
    try:
        recuperacao = RecuperacaoSenha.objects.get(id=recuperacao_id, tipo='telefone', usado=False)
        
        if recuperacao.esta_expirado():
            messages.error(request, 'Código OTP expirado! Solicite nova recuperação.')
            return redirect('esqueci_senha')
        
        if request.method == 'POST':
            codigo = request.POST.get('codigo_otp')
            nova_senha = request.POST.get('nova_senha')
            confirmar_senha = request.POST.get('confirmar_senha')
            
            if codigo != recuperacao.codigo_otp:
                messages.error(request, 'Código OTP inválido!')
                return render(request, 'core/validar_otp.html', {'recuperacao': recuperacao})
            
            if nova_senha != confirmar_senha:
                messages.error(request, 'As senhas não coincidem!')
                return render(request, 'core/validar_otp.html', {'recuperacao': recuperacao})
            
            if len(nova_senha) < 6:
                messages.error(request, 'A senha deve ter no mínimo 6 caracteres!')
                return render(request, 'core/validar_otp.html', {'recuperacao': recuperacao})
            
            for user_check in User.objects.exclude(id=recuperacao.user.id):
                if user_check.check_password(nova_senha):
                    messages.error(request, 'Esta senha já está sendo usada por outro usuário. Por favor, escolha uma senha diferente.')
                    return render(request, 'core/validar_otp.html', {'recuperacao': recuperacao})
            
            user = recuperacao.user
            user.set_password(nova_senha)
            user.save()
            
            recuperacao.marcar_como_usado()
            del request.session['recuperacao_id']
            
            messages.success(request, 'Senha redefinida com sucesso! Faça login com sua nova senha.')
            return redirect('login')
        
        return render(request, 'core/validar_otp.html', {'recuperacao': recuperacao})
    
    except RecuperacaoSenha.DoesNotExist:
        messages.error(request, 'Recuperação inválida!')
        return redirect('esqueci_senha')

def redefinir_senha_email_view(request, token):
    """View para redefinir senha via link de email"""
    try:
        recuperacao = RecuperacaoSenha.objects.get(token=token, tipo='email', usado=False)
        
        if recuperacao.esta_expirado():
            messages.error(request, 'Link expirado! Solicite nova recuperação.')
            return redirect('esqueci_senha')
        
        if request.method == 'POST':
            nova_senha = request.POST.get('nova_senha')
            confirmar_senha = request.POST.get('confirmar_senha')
            
            if nova_senha != confirmar_senha:
                messages.error(request, 'As senhas não coincidem!')
                return render(request, 'core/redefinir_senha_email.html', {'token': token})
            
            if len(nova_senha) < 6:
                messages.error(request, 'A senha deve ter no mínimo 6 caracteres!')
                return render(request, 'core/redefinir_senha_email.html', {'token': token})
            
            for user_check in User.objects.exclude(id=recuperacao.user.id):
                if user_check.check_password(nova_senha):
                    messages.error(request, 'Esta senha já está sendo usada por outro usuário. Por favor, escolha uma senha diferente.')
                    return render(request, 'core/redefinir_senha_email.html', {'token': token})
            
            user = recuperacao.user
            user.set_password(nova_senha)
            user.save()
            
            recuperacao.marcar_como_usado()
            
            messages.success(request, 'Senha redefinida com sucesso! Faça login com sua nova senha.')
            return redirect('login')
        
        return render(request, 'core/redefinir_senha_email.html', {'token': token})
    
    except RecuperacaoSenha.DoesNotExist:
        messages.error(request, 'Link inválido ou já utilizado!')
        return redirect('esqueci_senha')

@login_required
def perfis_pendentes_view(request):
    """View para administradores gerenciarem perfis pendentes"""
    if not request.user.is_staff:
        messages.error(request, 'Acesso negado! Apenas administradores podem acessar esta área.')
        return redirect('dashboard')
    
    perfis_pendentes = PerfilUsuario.objects.filter(nivel_acesso='pendente').order_by('-data_cadastro')
    
    return render(request, 'core/perfis_pendentes.html', {
        'perfis_pendentes': perfis_pendentes
    })

@login_required
def atribuir_perfil_view(request, perfil_id):
    """View para atribuir perfil a um usuário"""
    if not request.user.is_staff:
        messages.error(request, 'Acesso negado!')
        return redirect('dashboard')
    
    perfil = get_object_or_404(PerfilUsuario, id=perfil_id)
    
    if request.method == 'POST':
        nivel_acesso = request.POST.get('nivel_acesso')
        
        if nivel_acesso in ['admin', 'secretaria', 'professor', 'coordenador', 'aluno']:
            perfil.nivel_acesso = nivel_acesso
            perfil.save()
            
            Notificacao.objects.create(
                titulo='Perfil Atribuído',
                mensagem=f'Seu perfil foi atribuído como {perfil.get_nivel_acesso_display()}. Agora você pode acessar o sistema.',
                tipo='sucesso'
            ).destinatarios.add(perfil.user)
            
            messages.success(request, f'Perfil "{perfil.get_nivel_acesso_display()}" atribuído com sucesso para {perfil.user.get_full_name() or perfil.user.username}!')
        else:
            messages.error(request, 'Nível de acesso inválido!')
        
        return redirect('perfis_pendentes')
    
    return redirect('perfis_pendentes')

@login_required
def get_perfis_pendentes_count(request):
    """API endpoint para obter contagem de perfis pendentes"""
    if request.user.is_staff:
        count = PerfilUsuario.objects.filter(nivel_acesso='pendente').count()
        return JsonResponse({'count': count})
    return JsonResponse({'count': 0})

@login_required
def painel_principal(request):
    """View para o painel principal com menu lateral"""
    from datetime import date
    total_inscricoes = Inscricao.objects.count()
    total_aprovados = Inscricao.objects.filter(aprovado=True).count()
    total_reprovados = Inscricao.objects.filter(aprovado=False, nota_teste__isnull=False).count()
    aguardando_nota = Inscricao.objects.filter(nota_teste__isnull=True).count()
    
    anos_academicos = AnoAcademico.objects.all()
    ano_atual = AnoAcademico.objects.filter(ativo=True).first()
    
    notificacoes_nao_lidas = Notificacao.objects.filter(
        Q(global_notificacao=True) | Q(destinatarios=request.user),
        ativa=True
    ).exclude(lida_por=request.user).count()
    
    notificacoes_recentes = Notificacao.objects.filter(
        Q(global_notificacao=True) | Q(destinatarios=request.user),
        ativa=True
    ).distinct().order_by('-data_criacao')[:3]
    
    subscricao = Subscricao.objects.filter(estado__in=['ativo', 'teste']).first()
    
    context = {
        'total_inscricoes': total_inscricoes,
        'total_aprovados': total_aprovados,
        'total_reprovados': total_reprovados,
        'aguardando_nota': aguardando_nota,
        'anos_academicos': anos_academicos,
        'ano_atual': ano_atual,
        'notificacoes_nao_lidas': notificacoes_nao_lidas,
        'notificacoes_recentes': notificacoes_recentes,
        'subscricao': subscricao,
        'now': date.today()
    }
    return render(request, 'core/painel_principal.html', context)

@login_required
def trocar_ano(request):
    """View para seleção de ano acadêmico"""
    anos_academicos = AnoAcademico.objects.all().order_by('-ano_inicio')
    ano_atual = AnoAcademico.objects.filter(ativo=True).first()
    
    context = {
        'anos_academicos': anos_academicos,
        'ano_atual': ano_atual
    }
    return render(request, 'core/trocar_ano.html', context)

@login_required
def perfil_usuario(request):
    """View para exibir e editar perfil do usuário"""
    context = {
        'user': request.user,
    }
    return render(request, 'core/perfil_usuario.html', context)

@login_required
def quadro_avisos(request):
    """View para exibir quadro de avisos"""
    avisos = Notificacao.objects.filter(
        Q(global_notificacao=True) | Q(destinatarios=request.user),
        ativa=True
    ).distinct().order_by('-data_criacao')
    
    context = {
        'avisos': avisos
    }
    return render(request, 'core/quadro_avisos.html', context)

@login_required
def gestao_academica(request):
    """View para página principal de gestão acadêmica"""
    return render(request, 'core/gestao_academica.html')

@login_required
def cursos_disciplinas(request):
    """View para gerenciar cursos e disciplinas"""
    from .models import Disciplina
    cursos = Curso.objects.all()
    disciplinas = Disciplina.objects.all()
    context = {
        'cursos': cursos,
        'disciplinas': disciplinas,
        'active': 'cursos'
    }
    return render(request, 'core/cursos_disciplinas.html', context)

@login_required
def grelha_curricular(request):
    """View para exibir grelha curricular"""
    context = {'active': 'grelha'}
    return render(request, 'core/grelha_curricular.html', context)

@login_required
def cronograma_academico(request):
    """View para exibir cronograma acadêmico"""
    context = {'active': 'cronograma'}
    return render(request, 'core/cronograma_academico.html', context)

@login_required
def periodo_letivo(request):
    """View para gerenciar período letivo"""
    context = {'active': 'periodo'}
    return render(request, 'core/periodo_letivo.html', context)

@login_required
def horarios(request):
    """View para gerenciar horários"""
    context = {'active': 'horarios'}
    return render(request, 'core/horarios.html', context)

@login_required
def titulos_academicos(request):
    """View para gerenciar títulos acadêmicos"""
    context = {'active': 'titulos'}
    return render(request, 'core/titulos_academicos.html', context)

@login_required
def modelo_avaliacao(request):
    """View para gerenciar modelo de avaliação"""
    context = {'active': 'modelo'}
    return render(request, 'core/modelo_avaliacao.html', context)

@login_required
def syllabus(request):
    """View para gerenciar syllabus acadêmico"""
    context = {'active': 'syllabus'}
    return render(request, 'core/syllabus.html', context)

@login_required
def gestao_estudantes(request):
    """View para página principal de gestão de estudantes"""
    return render(request, 'core/gestao_estudantes.html')

@login_required
def admissao(request):
    """View para admissão de estudantes"""
    context = {}
    return render(request, 'core/admissao_view.html', context)

@login_required
def matricula(request):
    """View para matrícula de estudantes"""
    context = {}
    return render(request, 'core/matricula_view.html', context)

@login_required
def lista_estudantes(request):
    """View para lista de estudantes"""
    context = {}
    return render(request, 'core/lista_estudantes_view.html', context)

@login_required
def assiduidade(request):
    """View para controle de assiduidade"""
    context = {}
    return render(request, 'core/assiduidade_view.html', context)

@login_required
def certificados(request):
    """View para gerenciar certificados"""
    context = {}
    return render(request, 'core/certificados_view.html', context)

@login_required
def historico(request):
    """View para histórico escolar"""
    context = {}
    return render(request, 'core/historico_view.html', context)

@login_required
def materiais(request):
    """View para materiais de apoio"""
    context = {}
    return render(request, 'core/materiais_view.html', context)

@login_required
def solicitacao_docs(request):
    """View para solicitação de documentos"""
    context = {}
    return render(request, 'core/solicitacao_docs_view.html', context)

@login_required
def atividades_extracurriculares(request):
    """View para atividades extracurriculares"""
    context = {}
    return render(request, 'core/atividades_extracurriculares_view.html', context)
