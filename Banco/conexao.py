import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

def conectar_banco(criar_database=False):
    host = os.getenv("DB_HOST")
    port = int(os.getenv("DB_PORT"))
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    database = os.getenv("DB_NAME")

    if criar_database:
        conexao_temp = mysql.connector.connect(
            host=host,
            user=user,
            password=password
        )
        cursor_temp = conexao_temp.cursor()
        cursor_temp.execute(f"CREATE DATABASE IF NOT EXISTS {database}")
        conexao_temp.commit()
        conexao_temp.close()

    return mysql.connector.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database
    )