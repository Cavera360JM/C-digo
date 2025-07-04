import sqlite3
import os

def init_db():
    os.makedirs('db', exist_ok=True)
    conn = sqlite3.connect('db/database.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios_tb (
            id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_completo TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS equipes_tb (
            id_equipe INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_equipe TEXT NOT NULL,
            descricao TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS membros_equipe_tb (
            id_membro_equipe INTEGER PRIMARY KEY AUTOINCREMENT,
            id_usuario INTEGER,
            id_equipe INTEGER,
            papel_na_equipe TEXT,
            FOREIGN KEY(id_usuario) REFERENCES usuarios_tb(id_usuario),
            FOREIGN KEY(id_equipe) REFERENCES equipes_tb(id_equipe)
        )
    ''')

    conn.commit()
    conn.close()
