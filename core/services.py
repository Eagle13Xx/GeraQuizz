# seu_app/services.py
import fitz
import google.generativeai as genai
import json
import os


api_key = os.getenv('GEMINI_API_KEY')

if not api_key:
    # Lança um erro se a chave não for encontrada
    raise ValueError("A variável de ambiente GEMINI_API_KEY não foi definida. Verifique seu arquivo .env")

genai.configure(api_key=api_key)

def extrair_texto_pdf(caminho_arquivo):
    """
    Extrai texto de um arquivo PDF, usando OCR se necessário.
    """
    texto_completo = ""
    try:
        doc = fitz.open(caminho_arquivo)
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            texto_pagina = page.get_text("text")
            texto_completo += texto_pagina + "\n\n"
        doc.close()
        return texto_completo
    except Exception as e:
        print(f"Erro ao extrair texto: {e}")
        return None

def gerar_perguntas_com_gemini(texto_material, num_perguntas=5):
    """
    Envia o texto para a API Gemini e espera um JSON estruturado de volta.
    """
    # Configuração do modelo
    generation_config = {
        "temperature": 0.7,
        "top_p": 1,
        "top_k": 1,
        "max_output_tokens": 8192,
        "response_mime_type": "application/json",
    }
    model = genai.GenerativeModel(
        model_name="gemini-2.5-pro",
        generation_config=generation_config
    )

    prompt = f"""
    Com base no seguinte texto extraído de um material de aula, gere exatamente {num_perguntas} perguntas 
    de múltipla escolha (MCQs) para um quiz.

    Formato de Resposta Obrigatório:
    Responda APENAS com um array JSON. Cada objeto no array deve ter a seguinte estrutura:
    {{
      "pergunta": "O texto da pergunta aqui",
      "alternativas": [
        "Texto da alternativa A",
        "Texto da alternativa B",
        "Texto da alternativa C",
        "Texto da alternativa D"
      ],
      "resposta_correta": "O texto exato de uma das alternativas acima",
      "justificativa": "Uma breve explicação do porquê esta é a resposta correta, 
                      baseada no texto."
    }}

    Texto para análise:
    ---
    {texto_material[:10000]} 
    ---
    """

    try:
        response = model.generate_content(prompt)
        dados_json = json.loads(response.text)
        return dados_json
    except Exception as e:
        print(f"Erro na API Gemini: {e}")
        print(f"Resposta recebida (se houver): {response.text if 'response' in locals() else 'N/A'}")
        return None