import sqlite3

conn = sqlite3.connect("db/database.db")
cursor = conn.cursor()

cursor.execute("ALTER TABLE usuarios_tb ADD COLUMN id_perfil INTEGER")
conn.commit()
conn.close()

print("Coluna 'id_perfil' adicionada com sucesso!")
