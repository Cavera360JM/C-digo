import sqlite3

def conectar():
    return sqlite3.connect("db/database.db")

def criar_perfis_e_permissoes():
    conn = conectar()
    cursor = conn.cursor()

    # Criar perfil
    cursor.execute("INSERT INTO perfis_permissoes_tb (nome_perfil) VALUES (?)", ("Administrador",))
    id_perfil = cursor.lastrowid

    # Permissões padrão
    permissoes = [
        ("Criar Equipe", 1),
        ("Editar Equipe", 1),
        ("Excluir Equipe", 1),
        ("Visualizar Projetos", 1),
        ("Editar Projetos", 1),
        ("Criar Tarefa", 1),
        ("Editar Tarefa", 1),
        ("Excluir Tarefa", 1),
        ("Visualizar Comentários", 1),
        ("Adicionar Anexo", 1)
    ]

    for nome, permitido in permissoes:
        cursor.execute('''
            INSERT INTO permissoes_tb (id_perfil, nome_permissao, permitido)
            VALUES (?, ?, ?)
        ''', (id_perfil, nome, permitido))

    conn.commit()
    conn.close()
    print("Perfil 'Administrador' criado com permissões!")

if __name__ == "__main__":
    criar_perfis_e_permissoes()
