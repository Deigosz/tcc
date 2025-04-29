from flask import Flask
from flask_restx import Api, Resource, fields
import sys
import os
from flask import jsonify

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Utils._Conn import conectar_banco

app = Flask(__name__)
api = Api(app, version='1.0', title='API de Questões',
          description='API para gerenciamento de questões, matérias e dificuldades')

# Namespaces
ns_questoes = api.namespace('questoes', description='Operações relacionadas a questões')
ns_materias = api.namespace('materias', description='Operações relacionadas a matérias')
ns_dificuldades = api.namespace('dificuldades', description='Operações relacionadas a dificuldades')

# Models para documentação Swagger
alternativa_model = api.model('Alternativa', {
    'Alternativa': fields.String(required=True, description='Letra da alternativa'),
    'DescricaoAlternativa': fields.String(required=True, description='Descrição da alternativa')
})

questao_model = api.model('Questao', {
    'Questao': fields.Integer(required=True, description='ID da questão'),
    'Enunciado': fields.String(required=True, description='Enunciado da questão'),
    'Dificuldade': fields.String(required=True, description='Dificuldade'),
    'Materia': fields.String(required=True, description='Matéria'),
    'TipoQuestao': fields.String(required=True, description='Tipo de questão'),
    'Alternativas': fields.List(fields.Nested(alternativa_model)),
    'RespostaCorreta': fields.String(required=True, description='Resposta correta')
})

materia_model = api.model('Materia', {
    'id': fields.Integer(description='ID da matéria'),
    'nome': fields.String(description='Nome da matéria')
})

dificuldade_model = api.model('Dificuldade', {
    'id': fields.Integer(description='ID da dificuldade'),
    'nome': fields.String(description='Nome da dificuldade')
})

# Endpoints
@ns_questoes.route('/')
class Questoes(Resource):
    @ns_questoes.marshal_list_with(questao_model)
    def get(self):
        """Listar todas as questões"""
        conn = conectar_banco()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT 
                tq.id_questao, tq.enunciado, td.nome, tm.nome, 
                tc.nome, ta.alternativa, ta.descricao, tq.respostacorreta
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

        return list(questoes_dict.values())

@ns_questoes.route('/<int:id>')
class QuestaoPorID(Resource):
    @ns_questoes.marshal_with(questao_model)
    def get(self, id):
        """Buscar uma questão por ID"""
        conn = conectar_banco()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT 
                tq.id_questao, tq.enunciado, td.nome, tm.nome, 
                tc.nome, ta.alternativa, ta.descricao, tq.respostacorreta
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
            api.abort(404, "Questão não encontrada")

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

        return questao

@ns_materias.route('/')
class Materias(Resource):
    @ns_materias.marshal_list_with(materia_model)
    def get(self):
        """Listar todas as matérias"""
        conn = conectar_banco()
        cursor = conn.cursor()

        cursor.execute("SELECT id_materia, nome FROM tbl_materia ORDER BY nome ASC")
        rows = cursor.fetchall()

        materias = [{"id": row[0], "nome": row[1]} for row in rows]

        cursor.close()
        conn.close()

        return materias

@ns_dificuldades.route('/')
class Dificuldades(Resource):
    @ns_dificuldades.marshal_list_with(dificuldade_model)
    def get(self):
        """Listar todas as dificuldades"""
        conn = conectar_banco()
        cursor = conn.cursor()

        cursor.execute("SELECT id_dificuldade, nome FROM tbl_dificuldade ORDER BY nome ASC")
        rows = cursor.fetchall()

        dificuldades = [{"id": row[0], "nome": row[1]} for row in rows]

        cursor.close()
        conn.close()

        return dificuldades

@ns_questoes.route('/materia/<string:materia>')
class QuestoesPorMateria(Resource):
    @ns_questoes.marshal_list_with(questao_model)
    def get(self, materia):
        """Buscar questões por matéria"""
        conn = conectar_banco()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT 
                tq.id_questao, tq.enunciado, td.nome, tm.nome, 
                tc.nome, ta.alternativa, ta.descricao, tq.respostacorreta
            FROM tbl_questoes tq
            INNER JOIN tbl_materia tm ON tq.id_materia = tm.id_materia
            INNER JOIN tbl_classificacaoquestao tc ON tq.id_classificacaoquestao = tc.id_classificacao
            INNER JOIN tbl_dificuldade td ON tq.id_dificuldade = td.id_dificuldade
            INNER JOIN tbl_alternativas ta ON tq.id_questao = ta.id_questao
            WHERE tm.nome = %s
            ORDER BY tq.id_questao ASC, ta.alternativa ASC
        """, (materia,))
        
        rows = cursor.fetchall()
        if not rows:
            cursor.close()
            conn.close()
            api.abort(404, "Nenhuma questão encontrada para a matéria fornecida")

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

        return list(questoes_dict.values())

@ns_questoes.route('/dificuldade/<string:dificuldade>')
class QuestoesPorDificuldade(Resource):
    @ns_questoes.marshal_list_with(questao_model)
    def get(self, dificuldade):
        """Buscar questões por dificuldade"""
        conn = conectar_banco()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT 
                tq.id_questao, tq.enunciado, td.nome, tm.nome, 
                tc.nome, ta.alternativa, ta.descricao, tq.respostacorreta
            FROM tbl_questoes tq
            INNER JOIN tbl_materia tm ON tq.id_materia = tm.id_materia
            INNER JOIN tbl_classificacaoquestao tc ON tq.id_classificacaoquestao = tc.id_classificacao
            INNER JOIN tbl_dificuldade td ON tq.id_dificuldade = td.id_dificuldade
            INNER JOIN tbl_alternativas ta ON tq.id_questao = ta.id_questao
            WHERE td.nome = %s
            ORDER BY tq.id_questao ASC, ta.alternativa ASC
        """, (dificuldade,))
        
        rows = cursor.fetchall()
        if not rows:
            cursor.close()
            conn.close()
            api.abort(404, "Nenhuma questão encontrada para a dificuldade fornecida")

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

        return list(questoes_dict.values())

if __name__ == '__main__':
    app.run(debug=True)
