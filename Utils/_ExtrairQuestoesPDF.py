import fitz  
import re
import json

def LimparTexto(texto: str) -> str:
    texto = texto.replace('\n', ' ') 
    texto = texto.replace('\u00a0', ' ')
    texto = re.sub(r'\s+', ' ', texto)  
    return texto.strip()


def ExtrairQuestoes(pdf: str = None):
    doc = fitz.open(pdf)
    questoes = []
    questaoAtual = None
    letraAtual = None

    padrao_questao = re.compile(r"Questão\s*(\d+)", re.IGNORECASE)
    padrao_alternativa = re.compile(r"\(([A-E])\)")

    ignorar_textos = [
        "VESTIBULAR 1o SEM/2024",
    ]

    for pagina in doc:
        blocos = pagina.get_text("blocks")
        blocos.sort(key=lambda b: b[1])

        for bloco in blocos:
            texto = bloco[4].strip()
            texto_limpo = LimparTexto(texto)

            if any(ignorar in texto_limpo for ignorar in ignorar_textos):
                continue

            match_questao = padrao_questao.match(texto_limpo)

            if match_questao:
                if questaoAtual:
                    questoes.append(questaoAtual)
                questaoAtual = {
                    "idQuestao": match_questao.group(1),
                    "Materia": "",
                    "ClassificacaoQuestao": "",
                    "Dificuldade": "",
                    "Enunciado": "",
                    "Alternativas": {},
                    "RepostaCorreta": ""
                }
                letra_atual = None
                continue
        
            alternativas = padrao_alternativa.split(texto_limpo)
            if len(alternativas) > 1:
                for i in range(1, len(alternativas), 2):
                    letra = alternativas[i]
                    texto_alt = LimparTexto(alternativas[i + 1])

                    if questaoAtual and isinstance(questaoAtual.get("Alternativas"), dict):
                        questaoAtual["Alternativas"][letra] = texto_alt
                continue

            if questaoAtual and not letra_atual:
                questaoAtual["Enunciado"] += " " + texto_limpo

    if questaoAtual:
        questoes.append(questaoAtual)

    doc.close()
    dados_json = {"Questões": questoes}
    with open(r"jsons/Questoes.json", "w", encoding="utf-8") as f:
        json.dump(dados_json, f, ensure_ascii=False, indent=4)


ExtrairQuestoes(r"C:\Users\diego.souza\Documents\Faculdade\TCC\vestibulares\S01A2024FATEC.pdf")

