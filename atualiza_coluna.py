import sqlite3

conn = sqlite3.connect('db/database.db')
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE usuarios_tb ADD COLUMN imagem_perfil TEXT")
    print("✅ Campo 'imagem_perfil' adicionado com sucesso.")
except sqlite3.OperationalError as e:
    print("⚠️  Já existe ou erro:", e)

conn.commit()
conn.close()
