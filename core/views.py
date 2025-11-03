from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import transaction
from .models import Material, PerguntaGerada, Alternativa, TentativaQuiz, RespostaAluno
from .services import extrair_texto_pdf, gerar_perguntas_com_gemini
from django.contrib.auth import login
from .forms import CustomUserCreationForm
@login_required
def home(request):
    materiais = Material.objects.filter(
        professor=request.user
    ).order_by('-criado_em')

    context = {
        'materiais': materiais
    }
    return render(request, 'home.html', context)

@login_required
@transaction.atomic
def upload_material(request):
    if request.method == 'POST':
        titulo = request.POST.get('titulo')
        arquivo = request.FILES.get('arquivo')

        try:
            num_perguntas = int(request.POST.get('num_perguntas', 5))
        except ValueError:
            num_perguntas = 5

        # Impõe um limite de segurança (mesmo que o 'max' do HTML seja alterado)
        if num_perguntas > 20:
            num_perguntas = 20
        if num_perguntas < 1:
            num_perguntas = 1

        if not titulo or not arquivo:
            # Adiciona lógica de mensagem de erro
            return render(request, 'upload.html', {'error': 'Título e arquivo são obrigatórios.'})

        # 1. Salva o material
        material = Material.objects.create(
            professor=request.user,
            titulo=titulo,
            arquivo=arquivo
        )

        # 2. Extrai o texto
        texto = extrair_texto_pdf(material.arquivo.path)
        if not texto:
            return render(request, 'upload.html', {'error': 'Não foi possível ler o PDF.'})

        material.texto_extraido = texto
        material.save()

        # 3. Gera perguntas com a IA
        perguntas_json = gerar_perguntas_com_gemini(texto, num_perguntas)  # <-- PARÂMETRO ADICIONADO

        if not perguntas_json:
            return render(request, 'upload.html', {'error': 'Falha ao gerar perguntas com a IA.'})

        # 4. Salva no banco de dados
        for item in perguntas_json:
            pergunta = PerguntaGerada.objects.create(
                material=material,
                texto_pergunta=item['pergunta'],
                justificativa=item['justificativa']
            )
            for alt_texto in item['alternativas']:
                Alternativa.objects.create(
                    pergunta=pergunta,
                    texto_alternativa=alt_texto,
                    eh_correta=(alt_texto == item['resposta_correta'])
                )

        # Redireciona para o quiz recém-criado
        return redirect('iniciar_quiz', material_id=material.id)

    return render(request, 'upload.html')


@login_required
def iniciar_quiz(request, material_id):
    material = get_object_or_404(Material, id=material_id)
    # prefetch_related otimiza a consulta, buscando todas as alternativas de uma vez
    perguntas = material.perguntas.all().prefetch_related('alternativas')

    context = {
        'material': material,
        'perguntas': perguntas
    }
    return render(request, 'quiz.html', context)


@login_required
@transaction.atomic
def submeter_quiz(request, material_id):
    if request.method != 'POST':
        return redirect('iniciar_quiz', material_id=material_id)

    material = get_object_or_404(Material, id=material_id)
    perguntas = material.perguntas.all()
    aluno = request.user

    tentativa = TentativaQuiz.objects.create(aluno=aluno, material=material)
    pontuacao_final = 0

    for pergunta in perguntas:
        alternativa_id = request.POST.get(f'pergunta_{pergunta.id}')

        if alternativa_id:
            try:
                alternativa = Alternativa.objects.get(id=alternativa_id)
                eh_correta = alternativa.eh_correta
                if eh_correta:
                    pontuacao_final += 1

                RespostaAluno.objects.create(
                    tentativa=tentativa,
                    pergunta=pergunta,
                    alternativa_selecionada=alternativa,
                    foi_correta=eh_correta
                )
            except Alternativa.DoesNotExist:
                RespostaAluno.objects.create(
                    tentativa=tentativa,
                    pergunta=pergunta,
                    alternativa_selecionada=None,
                    foi_correta=False
                )
        else:
            # O aluno não respondeu
            RespostaAluno.objects.create(
                tentativa=tentativa,
                pergunta=pergunta,
                alternativa_selecionada=None,
                foi_correta=False
            )

    tentativa.pontuacao = pontuacao_final
    tentativa.save()

    return redirect('revisar_tentativa', tentativa_id=tentativa.id)


@login_required
def revisar_tentativa(request, tentativa_id):
    tentativa = get_object_or_404(
        TentativaQuiz.objects.prefetch_related(
            'respostas__pergunta__alternativas',
            'respostas__alternativa_selecionada'
        ),
        id=tentativa_id,
        aluno=request.user
    )

    context = {
        'tentativa': tentativa
    }
    return render(request, 'revisao.html', context)


@login_required
def historico_quiz(request):
    """
    Busca e exibe todas as tentativas de quiz
    feitas pelo usuário logado.
    """
    tentativas = TentativaQuiz.objects.filter(
        aluno=request.user
    ).select_related('material').order_by('-concluido_em')

    context = {
        'tentativas': tentativas
    }

    return render(request, 'historico.html', context)


def registrar(request):
    """
    Gerencia a página de registro de novos usuários.
    """
    # Se o usuário já está logado, redireciona para a home
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)

        if form.is_valid():
            # 1. Se o formulário é válido, salva o usuário
            user = form.save()

            # 2. Loga o usuário recém-criado
            login(request, user)

            # 3. Redireciona para a página inicial
            return redirect('home')

        # Se o formulário NÃO for válido, ele será renderizado
        # novamente, agora contendo as mensagens de erro

    else:
        # Se for um GET, apenas cria um formulário em branco
        form = CustomUserCreationForm()

    return render(request, 'registration/registrar.html', {'form': form})


@login_required
def estudar_flashcards(request, material_id):
    """
    Exibe as perguntas de um material em modo 'flashcard'.
    """
    material = get_object_or_404(Material, id=material_id)

    # Busca todas as perguntas E suas alternativas de uma vez
    # Isso é essencial para encontrar a resposta correta no template
    perguntas = material.perguntas.all().prefetch_related('alternativas')

    context = {
        'material': material,
        'perguntas': perguntas
    }
    return render(request, 'flashcards.html', context)