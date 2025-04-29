import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Utils._Conn import conectar_banco
import json

def salvarQuestoesAlternativas(JsonFile):
    with open(JsonFile, "r", encoding="utf-8") as f:
        dados = json.load(f)
        
        conn = conectar_banco()
        cursor = conn.cursor()
        
        for i, questao in enumerate(dados["Questões"]):
            print(f"Processando questão {i + 1}: {questao['Enunciado'][:50]}...")

            # Inserir a questão na tabela tbl_questoes e retornar o ID gerado
            query_questao = """
            INSERT INTO tbl_questoes (id_materia, id_classificacaoquestao, id_dificuldade, enunciado, respostacorreta)
            VALUES (%s, %s, %s, %s, %s) RETURNING id_questao
            """
            valores_questao = (
                questao["Materia"],  # id_materia
                questao["ClassificacaoQuestao"],  # id_classificacaoquestao
                questao["Dificuldade"],  # id_dificuldade
                questao["Enunciado"],  # enunciado
                questao["RepostaCorreta"]  # respostacorreta
            )
            cursor.execute(query_questao, valores_questao)

            id_questao = cursor.fetchone()[0]
            print(f"Questão {i + 1} inserida com ID {id_questao}.")

            for letra, texto in questao["Alternativas"].items():
                query_alternativa = """
                INSERT INTO tbl_alternativas (id_questao, alternativa, descricao)
                VALUES (%s, %s, %s)
                """
                valores_alternativa = (id_questao, letra, texto)
                cursor.execute(query_alternativa, valores_alternativa)
                print(f"  Alternativa {letra} inserida para a questão {id_questao}.")

        conn.commit()
        cursor.close()
        conn.close()
        print("Todas as questões e alternativas foram salvas com sucesso!")

salvarQuestoesAlternativas(r"jsons/QuestoesClassificadas.json")