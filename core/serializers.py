# seu_app/serializers.py
from rest_framework import serializers
from .models import Material, PerguntaGerada, Alternativa, TentativaQuiz, RespostaAluno


class AlternativaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alternativa
        fields = ['id', 'texto_alternativa']


class PerguntaQuizSerializer(serializers.ModelSerializer):
    alternativas = AlternativaSerializer(many=True, read_only=True)

    class Meta:
        model = PerguntaGerada
        fields = ['id', 'texto_pergunta', 'alternativas']


class MaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = ['id', 'titulo', 'arquivo']
        read_only_fields = ['id']


# --- Serializers para Revisão ---

class AlternativaCorretaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alternativa
        fields = ['id', 'texto_alternativa', 'eh_correta']


class PerguntaRevisaoSerializer(serializers.ModelSerializer):
    alternativas = AlternativaCorretaSerializer(many=True, read_only=True)

    class Meta:
        model = PerguntaGerada
        fields = ['id', 'texto_pergunta', 'alternativas', 'justificativa']


class RespostaRevisaoSerializer(serializers.ModelSerializer):
    pergunta = PerguntaRevisaoSerializer(read_only=True)
    alternativa_selecionada = AlternativaSerializer(read_only=True)

    class Meta:
        model = RespostaAluno
        fields = ['pergunta', 'alternativa_selecionada', 'foi_correta']


class TentativaRevisaoSerializer(serializers.ModelSerializer):
    respostas = RespostaRevisaoSerializer(many=True, read_only=True)

    class Meta:
        model = TentativaQuiz
        fields = ['id', 'aluno', 'material', 'pontuacao', 'concluido_em', 'respostas']