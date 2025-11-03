from django.contrib import admin
from .models import Material, PerguntaGerada, Alternativa, TentativaQuiz, RespostaAluno


class AlternativaInline(admin.TabularInline):
    """
    Permite editar as Alternativas DENTRO da página da Pergunta.
    'TabularInline' mostra como uma tabela compacta.
    """
    model = Alternativa
    extra = 0
    max_num = 5
    fields = ('texto_alternativa', 'eh_correta')


@admin.register(PerguntaGerada)
class PerguntaGeradaAdmin(admin.ModelAdmin):
    """
    Personaliza a lista de Perguntas no Admin.
    """
    model = PerguntaGerada
    inlines = [AlternativaInline]

    list_display = ('texto_pergunta_curto', 'material', 'get_resposta_correta')

    list_filter = ('material',)

    search_fields = ('texto_pergunta', 'justificativa')

    @admin.display(description='Pergunta')
    def texto_pergunta_curto(self, obj):
        if len(obj.texto_pergunta) > 100:
            return obj.texto_pergunta[:100] + '...'
        return obj.texto_pergunta

    @admin.display(description='Resposta Correta')
    def get_resposta_correta(self, obj):
        try:
            return obj.alternativas.get(eh_correta=True).texto_alternativa
        except Alternativa.DoesNotExist:
            return "N/A (Corrija!)"
        except Alternativa.MultipleObjectsReturned:
            return "ERRO (Múltiplas corretas!)"


#Painel de Administração para Materiais (os PDFs)

@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'professor', 'criado_em', 'get_total_perguntas')
    list_filter = ('professor',)
    search_fields = ('titulo',)

    readonly_fields = ('texto_extraido',)

    @admin.display(description='Nº de Perguntas')
    def get_total_perguntas(self, obj):
        return obj.perguntas.count()


# Painel de Administração para Resultados (Tentativas dos Alunos)

class RespostaAlunoInline(admin.TabularInline):
    """
    Mostra as respostas que o aluno deu em uma tentativa.
    """
    model = RespostaAluno
    extra = 0
    readonly_fields = ('pergunta', 'alternativa_selecionada', 'foi_correta')

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(TentativaQuiz)
class TentativaQuizAdmin(admin.ModelAdmin):
    list_display = ('material', 'aluno', 'pontuacao', 'concluido_em')
    list_filter = ('material', 'aluno')

    inlines = [RespostaAlunoInline]

    readonly_fields = ('aluno', 'material', 'pontuacao', 'concluido_em')