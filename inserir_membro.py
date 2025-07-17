import sqlite3

DB_PATH = 'db/database.db'
email_usuario = 'jdiassilva17@gmail.com'
nome_equipe = 'Site'
papel = 'Dono'  # ou 'Membro'

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Descobre o id_usuario pelo email
cursor.execute("SELECT id_usuario FROM usuarios_tb WHERE email = ?", (email_usuario,))
row = cursor.fetchone()
if not row:
    raise ValueError(f"Usuário com email {email_usuario} não encontrado.")
id_usuario = row[0]

# Descobre o id_equipe pelo nome
cursor.execute("SELECT id_equipe FROM equipes_tb WHERE nome_equipe = ?", (nome_equipe,))
row = cursor.fetchone()
if not row:
    raise ValueError(f"Equipe com nome {nome_equipe} não encontrada.")
id_equipe = row[0]

# Insere na tabela de membros
cursor.execute('''
    INSERT INTO membros_equipe_tb (id_usuario, id_equipe, papel_na_equipe)
    VALUES (?, ?, ?)
''', (id_usuario, id_equipe, papel))

conn.commit()
conn.close()

print(f"Usuário {id_usuario} vinculado à equipe {id_equipe}!")
