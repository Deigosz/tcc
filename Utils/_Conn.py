import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()


def conectar_banco():
    conn = psycopg2.connect(
        dbname=os.getenv("dbname"), 
        user=os.getenv("user"),  
        password=os.getenv("password"), 
        host=os.getenv("host"), 
        port=os.getenv("port")
    )
    return conn


def testarConexao():
    try:
        conn = conectar_banco()
        cursor = conn.cursor()
        cursor.execute("SELECT 1;")
        resultado = cursor.fetchone()
        if resultado[0] == 1:
            print("Banco de dados conectado com sucesso!")
        else:
            print("Falha na conexão.")
    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
    finally:
        cursor.close()
        conn.close()
        
