from flask import Flask, jsonify
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Utils._Conn import conectar_banco
from flask import request

app = Flask(__name__)

@app.route('/questoes', methods=['GET'])
def RetornarQuestoes():
    conn = conectar_banco()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            tq.id_questao AS Questao,
            tq.enunciado AS Enunciado,
            td.nome AS Dificuldade,
            tm.nome AS Materia,
            tc.nome AS TipoQuestao,
            ta.alternativa AS Alternativa,
            ta.descricao AS DescricaoAlternativa,
            tq.respostacorreta AS RespostaCorreta
        FROM tbl_questoes tq 
        INNER JOIN tbl_materia tm ON tq.id_materia = tm.id_materia
        INNER JOIN tbl_classificacaoquestao tc ON tq.id_classificacaoquestao = tc.id_classificacao
        INNER JOIN tbl_dificuldade td ON tq.id_dificuldade = td.id_dificuldade
        INNER JOIN tbl_alternativas ta ON tq.id_questao = ta.id_questao
        ORDER BY tq.id_questao ASC, ta.alternativa ASC
    """)
    
    rows = cursor.fetchall()

    questoes_dict = {}

    for row in rows:
        questao_id = row[0]

        if questao_id not in questoes_dict:
            questoes_dict[questao_id] = {
                "Questao": questao_id,
                "Enunciado": row[1],
                "Dificuldade": row[2],
                "Materia": row[3],
                "TipoQuestao": row[4],
                "Alternativas": [],
                "RespostaCorreta": row[7]
            }
        
        questoes_dict[questao_id]["Alternativas"].append({
            "Alternativa": row[5],
            "DescricaoAlternativa": row[6]
        })

    cursor.close()
    conn.close()

    resultado = list(questoes_dict.values())
    return jsonify(resultado)


@app.route('/questoes/<int:id>', methods=['GET'])
def RetornarQuestaoPorID(id):
    conn = conectar_banco()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            tq.id_questao AS Questao,
            tq.enunciado AS Enunciado,
            td.nome AS Dificuldade,
            tm.nome AS Materia,
            tc.nome AS TipoQuestao,
            ta.alternativa AS Alternativa,
            ta.descricao AS DescricaoAlternativa,
            tq.respostacorreta AS RespostaCorreta
        FROM tbl_questoes tq 
        INNER JOIN tbl_materia tm ON tq.id_materia = tm.id_materia
        INNER JOIN tbl_classificacaoquestao tc ON tq.id_classificacaoquestao = tc.id_classificacao
        INNER JOIN tbl_dificuldade td ON tq.id_dificuldade = td.id_dificuldade
        INNER JOIN tbl_alternativas ta ON tq.id_questao = ta.id_questao
        WHERE tq.id_questao = %s
        ORDER BY ta.alternativa ASC
    """, (id,))
    
    rows = cursor.fetchall()

    if not rows:
        cursor.close()
        conn.close()
        return jsonify({"erro": "Questão não encontrada"}), 404

    questao = {
        "Questao": rows[0][0],
        "Enunciado": rows[0][1],
        "Dificuldade": rows[0][2],
        "Materia": rows[0][3],
        "TipoQuestao": rows[0][4],
        "Alternativas": [],
        "RespostaCorreta": rows[0][7]
    }

    for row in rows:
        questao["Alternativas"].append({
            "Alternativa": row[5],
            "DescricaoAlternativa": row[6]
        })

    cursor.close()
    conn.close()

    return jsonify(questao)


@app.route('/materias', methods=['GET'])
def ListarMaterias():
    conn = conectar_banco()
    cursor = conn.cursor()

    cursor.execute("SELECT id_materia, nome FROM tbl_materia ORDER BY nome ASC")
    rows = cursor.fetchall()

    materias = [{"id": row[0], "nome": row[1]} for row in rows]

    cursor.close()
    conn.close()

    return jsonify(materias)


@app.route('/dificuldades', methods=['GET'])
def ListarDificuldades():
    conn = conectar_banco()
    cursor = conn.cursor()

    cursor.execute("SELECT id_dificuldade, nome FROM tbl_dificuldade ORDER BY nome ASC")
    rows = cursor.fetchall()

    dificuldades = [{"id": row[0], "nome": row[1]} for row in rows]

    cursor.close()
    conn.close()

    return jsonify(dificuldades)


@app.route('/questoes/materia/<string:materia>', methods=['GET'])
def FiltrarQuestoesPorMateria(materia):
    conn = conectar_banco()
    cursor = conn.cursor()

    query = """
        SELECT 
            tq.id_questao AS Questao,
            tq.enunciado AS Enunciado,
            td.nome AS Dificuldade,
            tm.nome AS Materia,
            tc.nome AS TipoQuestao,
            ta.alternativa AS Alternativa,
            ta.descricao AS DescricaoAlternativa,
            tq.respostacorreta AS RespostaCorreta
        FROM tbl_questoes tq 
        INNER JOIN tbl_materia tm ON tq.id_materia = tm.id_materia
        INNER JOIN tbl_classificacaoquestao tc ON tq.id_classificacaoquestao = tc.id_classificacao
        INNER JOIN tbl_dificuldade td ON tq.id_dificuldade = td.id_dificuldade
        INNER JOIN tbl_alternativas ta ON tq.id_questao = ta.id_questao
        WHERE tm.nome = %s
        ORDER BY tq.id_questao ASC, ta.alternativa ASC
    """

    cursor.execute(query, (materia,))
    rows = cursor.fetchall()

    if not rows:
        cursor.close()
        conn.close()
        return jsonify({"erro": "Nenhuma questão encontrada para a matéria fornecida."}), 404

    questoes_dict = {}

    for row in rows:
        questao_id = row[0]

        if questao_id not in questoes_dict:
            questoes_dict[questao_id] = {
                "Questao": questao_id,
                "Enunciado": row[1],
                "Dificuldade": row[2],
                "Materia": row[3],
                "TipoQuestao": row[4],
                "Alternativas": [],
                "RespostaCorreta": row[7]
            }
        
        questoes_dict[questao_id]["Alternativas"].append({
            "Alternativa": row[5],
            "DescricaoAlternativa": row[6]
        })

    cursor.close()
    conn.close()

    resultado = list(questoes_dict.values())
    return jsonify(resultado)


@app.route('/questoes/dificuldade/<string:dificuldade>', methods=['GET'])
def FiltrarQuestoesPorDificuldade(dificuldade):
    conn = conectar_banco()
    cursor = conn.cursor()

    query = """
        SELECT 
            tq.id_questao AS Questao,
            tq.enunciado AS Enunciado,
            td.nome AS Dificuldade,
            tm.nome AS Materia,
            tc.nome AS TipoQuestao,
            ta.alternativa AS Alternativa,
            ta.descricao AS DescricaoAlternativa,
            tq.respostacorreta AS RespostaCorreta
        FROM tbl_questoes tq 
        INNER JOIN tbl_materia tm ON tq.id_materia = tm.id_materia
        INNER JOIN tbl_classificacaoquestao tc ON tq.id_classificacaoquestao = tc.id_classificacao
        INNER JOIN tbl_dificuldade td ON tq.id_dificuldade = td.id_dificuldade
        INNER JOIN tbl_alternativas ta ON tq.id_questao = ta.id_questao
        WHERE td.nome = %s
        ORDER BY tq.id_questao ASC, ta.alternativa ASC
    """

    cursor.execute(query, (dificuldade,))
    rows = cursor.fetchall()

    if not rows:
        cursor.close()
        conn.close()
        return jsonify({"erro": "Nenhuma questão encontrada para a dificuldade fornecida."}), 404

    questoes_dict = {}

    for row in rows:
        questao_id = row[0]

        if questao_id not in questoes_dict:
            questoes_dict[questao_id] = {
                "Questao": questao_id,
                "Enunciado": row[1],
                "Dificuldade": row[2],
                "Materia": row[3],
                "TipoQuestao": row[4],
                "Alternativas": [],
                "RespostaCorreta": row[7]
            }
        
        questoes_dict[questao_id]["Alternativas"].append({
            "Alternativa": row[5],
            "DescricaoAlternativa": row[6]
        })

    cursor.close()
    conn.close()

    resultado = list(questoes_dict.values())
    return jsonify(resultado)


@app.route('/criar_trilha', methods=['POST'])
def CriarTrilha():
    dados = request.get_json()
    id_usuario = dados.get("id_usuario")
    nome_trilha = dados.get("nome_trilha")
    materias = dados.get("materias")      # Ex: ["História", "Matemática"]
    dificuldades = dados.get("dificuldades")  # Ex: ["Difícil"]

    if not all([id_usuario, nome_trilha, materias, dificuldades]):
        return jsonify({"erro": "Dados incompletos"}), 400

    conn = conectar_banco()
    cursor = conn.cursor()

    # 1. Inserir trilha
    cursor.execute("""
        INSERT INTO tbl_trilhas (id_usuario, nome_trilha) VALUES (%s, %s)
        RETURNING id_trilha
    """, (id_usuario, nome_trilha))
    id_trilha = cursor.fetchone()[0]

    # 2. Buscar questões
    query = """
        SELECT tq.id_questao
        FROM tbl_questoes tq
        INNER JOIN tbl_materia tm ON tq.id_materia = tm.id_materia
        INNER JOIN tbl_dificuldade td ON tq.id_dificuldade = td.id_dificuldade
        WHERE tm.nome = ANY(%s) AND td.nome = ANY(%s)
    """
    cursor.execute(query, (materias, dificuldades))
    questoes = cursor.fetchall()

    if not questoes:
        conn.rollback()
        cursor.close()
        conn.close()
        return jsonify({"erro": "Nenhuma questão encontrada com os critérios fornecidos."}), 404

    # 3. Associar questões à trilha
    for (id_questao,) in questoes:
        cursor.execute("""
            INSERT INTO tbl_trilha_questao (id_trilha, id_questao)
            VALUES (%s, %s)
        """, (id_trilha, id_questao))

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({
        "id_trilha": id_trilha,
        "nome_trilha": nome_trilha,
        "questoes_adicionadas": [q[0] for q in questoes]
    }), 201


@app.route('/trilha/<int:id_trilha>', methods=['GET'])
def obter_questoes_da_trilha(id_trilha):
    conn = conectar_banco()
    cursor = conn.cursor()

    # Query ajustada para incluir a trilha
    query = """
    SELECT 
        t.nome_trilha AS NomeTrilha,
        tq.id_questao AS Questao,
        tq.enunciado AS Enunciado,
        td.nome AS Dificuldade,
        tm.nome AS Materia,
        tc.nome AS TipoQuestao,
        ta.alternativa AS Alternativa,
        ta.descricao AS DescricaoAlternativa,
        tq.respostacorreta AS RespostaCorreta
    FROM tbl_questoes tq
    INNER JOIN tbl_materia tm ON tq.id_materia = tm.id_materia
    INNER JOIN tbl_classificacaoquestao tc ON tq.id_classificacaoquestao = tc.id_classificacao
    INNER JOIN tbl_dificuldade td ON tq.id_dificuldade = td.id_dificuldade
    INNER JOIN tbl_alternativas ta ON tq.id_questao = ta.id_questao
    INNER JOIN tbl_trilha_questao tqq ON tqq.id_questao = tq.id_questao
    INNER JOIN tbl_trilhas t ON t.id_trilha = tqq.id_trilha
    WHERE t.id_trilha = %s
    ORDER BY tq.id_questao ASC, ta.alternativa ASC;
    """

    cursor.execute(query, (id_trilha,))
    rows = cursor.fetchall()

    questoes = {}
    for row in rows:
        id_q = row[1]
        if id_q not in questoes:
            questoes[id_q] = {
                "NomeTrilha": row[0],
                "Questao": id_q,
                "Enunciado": row[2],
                "Dificuldade": row[3],
                "Materia": row[4],
                "TipoQuestao": row[5],
                "Alternativas": [],
                "RespostaCorreta": row[8]
            }
        questoes[id_q]["Alternativas"].append({
            "Alternativa": row[6],
            "DescricaoAlternativa": row[7]
        })

    conn.close()
    return jsonify(list(questoes.values()))


@app.route('/trilhas', methods=['GET'])
def listar_trilhas():
    conn = conectar_banco()
    cursor = conn.cursor()

    # Query para listar todas as trilhas
    query = "SELECT id_trilha, nome_trilha FROM tbl_trilhas ORDER BY nome_trilha ASC"
    
    cursor.execute(query)
    rows = cursor.fetchall()

    # Preparando a resposta em formato JSON
    trilhas = []
    for row in rows:
        trilhas.append({
            "id_trilha": row[0],
            "nome_trilha": row[1]
        })
    
    conn.close()
    return jsonify(trilhas)



if __name__ == '__main__':
    app.run(debug=True)
