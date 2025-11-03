# seu_app/models.py
from django.db import models
from django.contrib.auth.models import User

class Material(models.Model):
    """
    Armazena o arquivo PDF/Slide enviado pelo professor.
    """
    professor = models.ForeignKey(User, on_delete=models.CASCADE)
    titulo = models.CharField(max_length=255)
    arquivo = models.FileField(upload_to='materiais/')
    texto_extraido = models.TextField(blank=True, null=True, help_text="Cache do texto extraído do PDF.")
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titulo

class PerguntaGerada(models.Model):
    """
    Uma única pergunta (e sua justificativa) gerada pela API Gemini.
    """
    material = models.ForeignKey(Material, related_name='perguntas', on_delete=models.CASCADE)
    texto_pergunta = models.TextField()
    justificativa = models.TextField(help_text="Explicação da resposta correta (fornecida pela IA).")

    def __str__(self):
        return self.texto_pergunta[:50] + "..."

class Alternativa(models.Model):
    """
    Uma alternativa (opção de múltipla escolha) para uma PerguntaGerada.
    """
    pergunta = models.ForeignKey(PerguntaGerada, related_name='alternativas', on_delete=models.CASCADE)
    texto_alternativa = models.CharField(max_length=500)
    eh_correta = models.BooleanField(default=False, help_text="Definido pela IA como a resposta correta.")

    def __str__(self):
        return self.texto_alternativa

class TentativaQuiz(models.Model):
    """
    Registra a tentativa de um aluno em um quiz de um material específico.
    """
    aluno = models.ForeignKey(User, on_delete=models.CASCADE)
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    pontuacao = models.IntegerField(default=0)
    concluido_em = models.DateTimeField(auto_now_add=True)

class RespostaAluno(models.Model):
    """
    Armazena a resposta específica que um aluno deu em uma tentativa.
    """
    tentativa = models.ForeignKey(TentativaQuiz, related_name='respostas', on_delete=models.CASCADE)
    pergunta = models.ForeignKey(PerguntaGerada, on_delete=models.CASCADE)
    alternativa_selecionada = models.ForeignKey(Alternativa, on_delete=models.CASCADE)
    foi_correta = models.BooleanField()