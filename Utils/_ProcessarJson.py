import json

def processar_json():
    # Carrega o arquivo JSON
    with open('questoes.json', 'r', encoding='utf-8') as f:
        dados = json.load(f)

    questoes = dados.get("Questões", [])
    questoes_processadas = []
    questoes_vistas = {}

    for questao in questoes:
        # Verifica se a questão tem enunciado e alternativas com texto
        if not questao["Enunciado"] or not any(questao["Respostas"].values()):
            continue  # Ignora questões sem enunciado ou sem alternativas com texto

        # Verifica se já vimos essa questão (idQuestao)
        if questao["idQuestao"] in questoes_vistas:
            # Se já vimos a questão, adiciona o enunciado da questão atual ao enunciado da anterior
            questoes_vistas[questao["idQuestao"]]["Enunciado"] += " " + questao["Enunciado"]
            
            # Reindexa as alternativas
            ultima_questao = questoes_vistas[questao["idQuestao"]]
            ultimo_id_alternativa = max([ord(letra) - ord('A') + 1 for letra in ultima_questao["Respostas"].keys()])
            
            for letra, resposta in questao["Respostas"].items():
                nova_letra = chr(ord('A') + ultimo_id_alternativa)
                ultima_questao["Respostas"][nova_letra] = resposta
                ultimo_id_alternativa += 1

        else:
            # Caso contrário, adiciona a questão ao dicionário de vistas
            questoes_vistas[questao["idQuestao"]] = questao

    # Agora, coletamos as questões processadas
    questoes_processadas = list(questoes_vistas.values())

    # Salva o novo JSON com as questões processadas
    with open('questoes_processadas.json', 'w', encoding='utf-8') as f:
        json.dump({"Questões": questoes_processadas}, f, ensure_ascii=False, indent=4)

processar_json()
