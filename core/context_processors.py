from .models import Subscricao, ConfiguracaoEscola

def subscricao_context(request):
    """Context processor para adicionar informações de subscrição em todos os templates"""
    try:
        subscricao = Subscricao.objects.filter(estado__in=['ativo', 'teste']).first()
    except:
        subscricao = None
    
    try:
        config = ConfiguracaoEscola.objects.first()
    except:
        config = None
    
    return {
        'subscricao': subscricao,
        'config': config,
        'versao_sistema': '1.0.0',
        'desenvolvedor': 'Eng. Osvaldo Queta'
    }
