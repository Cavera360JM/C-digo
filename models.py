import sqlite3
import os

def init_db():
    os.makedirs('db', exist_ok=True)
    conn = sqlite3.connect('db/database.db')
    cursor = conn.cursor()

    # Tabela de usuários (agora com id_perfil)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios_tb (
            id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_completo TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL,
            imagem_perfil TEXT,
            id_perfil INTEGER,
            FOREIGN KEY(id_perfil) REFERENCES perfis_permissoes_tb(id_perfil)
        )
    ''')

    # Equipes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS equipes_tb (
            id_equipe INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_equipe TEXT NOT NULL,
            descricao TEXT
        )
    ''')

    # Membros da equipe
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

    # Projetos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS projetos_tb (
            id_projeto INTEGER PRIMARY KEY AUTOINCREMENT,
            id_equipe INTEGER,
            nome_projeto TEXT NOT NULL,
            descricao TEXT,
            data_inicio DATE,
            data_fim DATE,
            FOREIGN KEY(id_equipe) REFERENCES equipes_tb(id_equipe)
        )
    ''')

    # Tarefas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tarefas_tb (
            id_tarefa INTEGER PRIMARY KEY AUTOINCREMENT,
            id_projeto INTEGER,
            titulo TEXT NOT NULL,
            descricao TEXT,
            status TEXT,
            prioridade TEXT,
            data_criacao DATE,
            data_entrega DATE,
            FOREIGN KEY(id_projeto) REFERENCES projetos_tb(id_projeto)
        )
    ''')

    # Subtarefas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS subtarefas_tb (
            id_subtarefa INTEGER PRIMARY KEY AUTOINCREMENT,
            id_tarefa INTEGER,
            titulo TEXT NOT NULL,
            status TEXT,
            FOREIGN KEY(id_tarefa) REFERENCES tarefas_tb(id_tarefa)
        )
    ''')

    # Anexos de tarefa
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS anexos_tarefa_tb (
            id_anexo INTEGER PRIMARY KEY AUTOINCREMENT,
            id_tarefa INTEGER,
            nome_arquivo TEXT NOT NULL,
            caminho_arquivo TEXT NOT NULL,
            FOREIGN KEY(id_tarefa) REFERENCES tarefas_tb(id_tarefa)
        )
    ''')

    # Comentários de tarefa
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS comentarios_tarefa_tb (
            id_comentario INTEGER PRIMARY KEY AUTOINCREMENT,
            id_tarefa INTEGER,
            id_usuario INTEGER,
            comentario TEXT NOT NULL,
            data_comentario DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(id_tarefa) REFERENCES tarefas_tb(id_tarefa),
            FOREIGN KEY(id_usuario) REFERENCES usuarios_tb(id_usuario)
        )
    ''')

    # Atribuições de tarefa
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS atribuicoes_tarefa_tb (
            id_atribuicao INTEGER PRIMARY KEY AUTOINCREMENT,
            id_tarefa INTEGER,
            id_usuario INTEGER,
            papel TEXT,
            FOREIGN KEY(id_tarefa) REFERENCES tarefas_tb(id_tarefa),
            FOREIGN KEY(id_usuario) REFERENCES usuarios_tb(id_usuario)
        )
    ''')

    # Perfis de permissão
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS perfis_permissoes_tb (
            id_perfil INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_perfil TEXT NOT NULL
        )
    ''')

    # Permissões por perfil
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS permissoes_tb (
            id_permissao INTEGER PRIMARY KEY AUTOINCREMENT,
            id_perfil INTEGER,
            nome_permissao TEXT NOT NULL,
            permitido BOOLEAN NOT NULL,
            FOREIGN KEY(id_perfil) REFERENCES perfis_permissoes_tb(id_perfil)
        )
    ''')

    conn.commit()
    conn.close()
