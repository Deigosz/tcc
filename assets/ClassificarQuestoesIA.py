import json
import os
from openai import OpenAI
from dotenv import load_dotenv


load_dotenv()

client = OpenAI(
    api_key = os.getenv("GPT_KEY"),
)

def ClassificarQuestao(jsonQuestao: json):
    materias_dict = {
        'Lógica': 1,
        'História': 2,
        'Geografia': 3,
        'Matemática': 4,
        'Ciências': 5,
        'Língua Portuguesa': 6,
        'Biologia': 7,
        'Cultura e Artes': 8,
        'Ciências Biológicas': 9,
        'Química': 10,
        'Física': 11,
        'Linguagem': 12,
        'Sociologia': 13,
        'Artes': 14,
        'Preposições': 15,
        'História da Arte': 16,
        'Literatura': 17,
        'Música': 18,
        'Cinema Brasileiro': 19,
        'História do Cinema Brasileiro': 20,
        'Esportes': 21,
        'História do Brasil': 22
    }
    
    classificacoes_dict = {
        'Conectivos Lógicos': 1,
        'Arte Rupestre': 2,
        'Patrimônio Cultural Brasileiro': 3,
        'Arqueologia': 4,
        'História da Cartografia': 5,
        'Números decimais': 6,
        'Geologia': 7,
        'Compreensão de texto': 8,
        'Conjunções': 9,
        'Ecologia': 10,
        'Conhecimentos Gerais': 11,
        'Relação entre botânica e arte': 12,
        'Cálculo de custo e rendimento de tinta': 13,
        'Geometria': 14,
        'Análise química': 15,
        'Modelo Atômico': 16,
        'Fórmulas químicas': 17,
        'Análise de linguagem verbal e não verbal': 18,
        'Cinemática': 19,
        'Cultura e Identidade': 20,
        'Análise de linguagem verbal e não-verbal': 21,
        'Interpretação de texto': 22,
        'Significado das preposições': 23,
        'Medicina Islâmica Medieval': 24,
        'Combinatória': 25,
        'Estilo artístico': 26,
        'Classificação de dados': 27,
        'Estilo Artístico': 28
    }
    
    materias_dict_json = json.dumps(materias_dict, ensure_ascii=False, indent=4)
    classificacoes_dict_json = json.dumps(classificacoes_dict, ensure_ascii=False, indent=4)
    
    prompt = f"""
    Classifique a seguinte questão:

    Questão:
    {jsonQuestao['Enunciado']}

    Alternativas:
    {json.dumps(jsonQuestao['Alternativas'], ensure_ascii=False, indent=4)}

    Regras de resposta (siga exatamente):
    - Dificuldade: número de 1 a 5 (apenas o número).
    - Matéria: escolha o número correspondente baseado nesta lista:
    {materias_dict_json}
    - Classificação da Questão: escolha o número correspondente baseado nesta lista:
    {classificacoes_dict_json}
    - Resposta Correta: apenas a letra (A, B, C, D ou E), sem texto adicional.

    Formato da resposta (exatamente neste padrão):
    Dificuldade: <número>
    Matéria: <número>
    ClassificaçãoQuestao: <número>
    RespostaCorreta: <letra>
    """


    
    completion = client.completions.create(
        model = "gpt-3.5-turbo-instruct",
        prompt = prompt,
        max_tokens = 150,
        temperature = 0,
    )
    resposta = completion.choices[0].text.strip()  
    try:
        linhas_resposta = resposta.split("\n")
        dificuldade = linhas_resposta[0].split(":")[1].strip()
        materia = linhas_resposta[1].split(":")[1].strip()
        classificacao = linhas_resposta[2].split(":")[1].strip()
        resposta_correta = linhas_resposta[3].split(":")[1].strip()
        
    except Exception as e:
        dificuldade = 0
        materia = "Desconhecido"
        classificacao = "Geral"
        resposta_correta = "A"
    
    jsonQuestao["Dificuldade"] = dificuldade
    jsonQuestao["Materia"] = materia
    jsonQuestao["ClassificacaoQuestao"] = classificacao
    jsonQuestao["RepostaCorreta"] = resposta_correta

    return jsonQuestao


with open(r"jsons/Questoes.json", "r", encoding="utf-8") as f:
    questoes = json.load(f)
    
    questoes_classificadas = []
    
    for i, questao in enumerate(questoes["Questões"]):
        if questao.get("Enunciado") == "":
            continue
        if questao.get("Alternativas") == "":
            continue
        
        questaoClassificada = ClassificarQuestao(questao)
        questaoClassificada["idQuestao"] = i + 1 
        questoes_classificadas.append(questaoClassificada)
        
        # Logging
        print(f"Classificando questão {i + 1}")
    
    with open(f"jsons/QuestoesClassificadas.json", "w", encoding="utf-8") as f:
        json.dump({"Questões": questoes_classificadas}, f, ensure_ascii=False, indent=4)