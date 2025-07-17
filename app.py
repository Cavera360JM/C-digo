from flask import Flask, render_template, request, redirect, session, flash, url_for
import sqlite3
import os
from werkzeug.utils import secure_filename
from models import init_db

app = Flask(__name__)
app.secret_key = "segredo123"
init_db()

UPLOAD_FOLDER = 'static/imagens'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf', 'docx'}

def conectar():
    return sqlite3.connect("db/database.db")

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios_tb WHERE email=? AND senha=?", (email, senha))
        user = cursor.fetchone()
        conn.close()
        if user:
            session['usuario'] = user[0]
            return redirect('/dashboard')
        else:
            return render_template('login.html', error="Login inválido")
    return render_template('login.html')

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM perfis_permissoes_tb")
    perfis = cursor.fetchall()

    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']
        id_perfil = request.form.get('id_perfil')
        try:
            cursor.execute("INSERT INTO usuarios_tb (nome_completo, email, senha, id_perfil) VALUES (?, ?, ?, ?)", (nome, email, senha, id_perfil))
            conn.commit()
            flash("Cadastro realizado com sucesso! Faça login.")
            return redirect('/login')
        except sqlite3.IntegrityError:
            return render_template('cadastro.html', error="Email já cadastrado.", perfis=perfis)
        finally:
            conn.close()
    return render_template('cadastro.html', perfis=perfis)

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'usuario' not in session:
        return redirect('/login')

    conn = conectar()
    cursor = conn.cursor()
    mensagem = None

    if request.method == 'POST':
        if 'acao' in request.form and request.form['acao'] == 'atualizar_nome':
            novo_nome = request.form['novo_nome']
            cursor.execute("UPDATE usuarios_tb SET nome_completo=? WHERE id_usuario=?", (novo_nome, session['usuario']))
            conn.commit()
            mensagem = "Nome alterado com sucesso!"
        elif 'imagem' in request.files:
            file = request.files['imagem']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                cursor.execute("UPDATE usuarios_tb SET imagem_perfil=? WHERE id_usuario=?", (filename, session['usuario']))
                conn.commit()
                mensagem = "Imagem alterada com sucesso!"

    cursor.execute("SELECT nome_completo, imagem_perfil FROM usuarios_tb WHERE id_usuario = ?", (session['usuario'],))
    user_data = cursor.fetchone()
    nome = user_data[0]
    imagem = user_data[1] if user_data[1] else "imagem.jpg"

    cursor.execute('''
        SELECT e.id_equipe, e.nome_equipe
        FROM membros_equipe_tb m
        JOIN equipes_tb e ON m.id_equipe = e.id_equipe
        WHERE m.id_usuario = ?
    ''', (session['usuario'],))
    equipes = cursor.fetchall()

    conn.close()

    return render_template('dashboard.html', nome=nome, imagem=imagem, mensagem=mensagem, equipes=equipes)

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('usuario', None)
    return redirect('/login')

@app.route('/nova_equipe', methods=['GET', 'POST'])
def nova_equipe():
    if 'usuario' not in session:
        return redirect('/login')
    if request.method == 'POST':
        nome = request.form['nome']
        descricao = request.form['descricao']
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO equipes_tb (nome_equipe, descricao) VALUES (?, ?)", (nome, descricao))
        conn.commit()
        conn.close()
        return redirect('/equipes')
    return render_template('nova_equipe.html')

@app.route('/equipes')
def equipes():
    if 'usuario' not in session:
        return redirect('/login')
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM equipes_tb")
    equipes = cursor.fetchall()

    cursor.execute("SELECT * FROM perfis_permissoes_tb")
    perfis = cursor.fetchall()

    permissoes_por_perfil = {}
    for perfil in perfis:
        id_perfil = perfil[0]
        cursor.execute("SELECT nome_permissao, permitido FROM permissoes_tb WHERE id_perfil = ?", (id_perfil,))
        permissoes = cursor.fetchall()
        permissoes_por_perfil[id_perfil] = permissoes

    conn.close()
    return render_template('equipes.html', equipes=equipes, perfis=perfis, permissoes_por_perfil=permissoes_por_perfil)

@app.route('/adicionar_membro/<int:id_equipe>', methods=['GET', 'POST'])
def adicionar_membro(id_equipe):
    if 'usuario' not in session:
        return redirect('/login')

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT nome_equipe FROM equipes_tb WHERE id_equipe = ?", (id_equipe,))
    equipe = cursor.fetchone()

    cursor.execute("SELECT id_usuario, nome_completo FROM usuarios_tb")
    usuarios = cursor.fetchall()

    if request.method == 'POST':
        id_usuario = request.form['id_usuario']
        papel = request.form['papel']
        cursor.execute("""
            INSERT INTO membros_equipe_tb (id_usuario, id_equipe, papel_na_equipe)
            VALUES (?, ?, ?)
        """, (id_usuario, id_equipe, papel))
        conn.commit()
        conn.close()
        return redirect('/equipes')

    conn.close()
    return render_template('adicionar_membro.html', usuarios=usuarios, equipe=equipe, id_equipe=id_equipe)

@app.route('/editar_equipe/<int:id_equipe>', methods=['GET', 'POST'])
def editar_equipe(id_equipe):
    if 'usuario' not in session:
        return redirect('/login')

    conn = conectar()
    cursor = conn.cursor()

    if request.method == 'POST':
        novo_nome = request.form['nome']
        nova_descricao = request.form['descricao']
        cursor.execute("UPDATE equipes_tb SET nome_equipe = ?, descricao = ? WHERE id_equipe = ?", (novo_nome, nova_descricao, id_equipe))
        conn.commit()
        conn.close()
        return redirect('/equipes')

    cursor.execute("SELECT * FROM equipes_tb WHERE id_equipe = ?", (id_equipe,))
    equipe = cursor.fetchone()
    conn.close()
    return render_template('editar_equipe.html', equipe=equipe)

@app.route('/excluir_equipe/<int:id_equipe>', methods=['POST'])
def excluir_equipe(id_equipe):
    if 'usuario' not in session:
        return redirect('/login')

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM membros_equipe_tb WHERE id_equipe = ?", (id_equipe,))
    cursor.execute("DELETE FROM equipes_tb WHERE id_equipe = ?", (id_equipe,))
    conn.commit()
    conn.close()
    return redirect('/equipes')

@app.route('/projetos/<int:id_equipe>', methods=['GET', 'POST'])
def projetos(id_equipe):
    if 'usuario' not in session:
        return redirect('/login')

    conn = conectar()
    cursor = conn.cursor()

    if request.method == 'POST':
        nome_projeto = request.form['nome_projeto']
        descricao = request.form['descricao']
        data_inicio = request.form.get('data_inicio')
        data_fim = request.form.get('data_fim')

        cursor.execute('''
            INSERT INTO projetos_tb (id_equipe, nome_projeto, descricao, data_inicio, data_fim)
            VALUES (?, ?, ?, ?, ?)
        ''', (id_equipe, nome_projeto, descricao, data_inicio, data_fim))
        conn.commit()

    cursor.execute('SELECT nome_equipe FROM equipes_tb WHERE id_equipe = ?', (id_equipe,))
    equipe = cursor.fetchone()

    cursor.execute('SELECT * FROM projetos_tb WHERE id_equipe = ?', (id_equipe,))
    projetos = cursor.fetchall()

    conn.close()
    return render_template('projetos.html', equipe=equipe, projetos=projetos, id_equipe=id_equipe)

@app.route('/tarefas/<int:id_projeto>', methods=['GET', 'POST'])
def tarefas(id_projeto):
    if 'usuario' not in session:
        return redirect('/login')

    conn = conectar()
    cursor = conn.cursor()

    if request.method == 'POST':
        titulo = request.form['titulo']
        descricao = request.form['descricao']
        status = request.form.get('status', 'Pendente')
        prioridade = request.form.get('prioridade', 'Média')
        data_criacao = request.form.get('data_criacao')
        data_entrega = request.form.get('data_entrega')

        cursor.execute('''
            INSERT INTO tarefas_tb (id_projeto, titulo, descricao, status, prioridade, data_criacao, data_entrega)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (id_projeto, titulo, descricao, status, prioridade, data_criacao, data_entrega))
        conn.commit()

    cursor.execute('SELECT nome_projeto, id_equipe FROM projetos_tb WHERE id_projeto = ?', (id_projeto,))
    projeto = cursor.fetchone()
    id_equipe = projeto[1]

    cursor.execute('SELECT * FROM tarefas_tb WHERE id_projeto = ?', (id_projeto,))
    tarefas = cursor.fetchall()

    conn.close()
    return render_template('tarefas.html', projeto=projeto, tarefas=tarefas, id_projeto=id_projeto, id_equipe=id_equipe)

@app.route('/subtarefas/<int:id_tarefa>', methods=['GET', 'POST'])
def subtarefas(id_tarefa):
    if 'usuario' not in session:
        return redirect('/login')
    conn = conectar()
    cursor = conn.cursor()

    if request.method == 'POST':
        titulo = request.form['titulo']
        status = request.form.get('status', 'Pendente')
        cursor.execute('''
            INSERT INTO subtarefas_tb (id_tarefa, titulo, status) VALUES (?, ?, ?)
        ''', (id_tarefa, titulo, status))
        conn.commit()

    cursor.execute('SELECT titulo, id_projeto FROM tarefas_tb WHERE id_tarefa = ?', (id_tarefa,))
    tarefa = cursor.fetchone()

    cursor.execute('SELECT * FROM subtarefas_tb WHERE id_tarefa = ?', (id_tarefa,))
    subtarefas = cursor.fetchall()
    conn.close()

    return render_template('subtarefas.html', tarefa=tarefa, subtarefas=subtarefas, id_tarefa=id_tarefa)

@app.route('/comentarios/<int:id_tarefa>', methods=['GET', 'POST'])
def comentarios(id_tarefa):
    if 'usuario' not in session:
        return redirect('/login')

    conn = conectar()
    cursor = conn.cursor()

    if request.method == 'POST':
        comentario = request.form['comentario']
        id_usuario = session['usuario']
        cursor.execute('''
            INSERT INTO comentarios_tarefa_tb (id_tarefa, id_usuario, comentario)
            VALUES (?, ?, ?)
        ''', (id_tarefa, id_usuario, comentario))
        conn.commit()

    cursor.execute('SELECT titulo, id_projeto FROM tarefas_tb WHERE id_tarefa = ?', (id_tarefa,))
    tarefa = cursor.fetchone()

    cursor.execute('''
        SELECT c.id_comentario, u.nome_completo, c.comentario, c.data_comentario
        FROM comentarios_tarefa_tb c
        JOIN usuarios_tb u ON c.id_usuario = u.id_usuario
        WHERE c.id_tarefa = ?
        ORDER BY c.data_comentario DESC
    ''', (id_tarefa,))
    comentarios_raw = cursor.fetchall()

    from datetime import datetime, timedelta
    comentarios = []
    for c in comentarios_raw:
        data_utc = datetime.strptime(c[3], "%Y-%m-%d %H:%M:%S")
        data_local = data_utc - timedelta(hours=3)
        comentarios.append((c[0], c[1], c[2], data_local.strftime("%d/%m/%Y %H:%M")))

    conn.close()

    return render_template('comentarios.html', tarefa=tarefa, comentarios=comentarios, id_tarefa=id_tarefa)

@app.route('/anexos/<int:id_tarefa>', methods=['GET', 'POST'])
def anexos(id_tarefa):
    if 'usuario' not in session:
        return redirect('/login')

    conn = conectar()
    cursor = conn.cursor()

    if request.method == 'POST':
        file = request.files.get('arquivo')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            caminho = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(caminho)
            cursor.execute('''
                INSERT INTO anexos_tarefa_tb (id_tarefa, nome_arquivo, caminho_arquivo)
                VALUES (?, ?, ?)
            ''', (id_tarefa, filename, caminho))
            conn.commit()
            flash('Arquivo anexado com sucesso!')
        else:
            flash('Arquivo inválido!')

    cursor.execute('SELECT titulo, id_projeto FROM tarefas_tb WHERE id_tarefa = ?', (id_tarefa,))
    tarefa = cursor.fetchone()

    cursor.execute('SELECT * FROM anexos_tarefa_tb WHERE id_tarefa = ?', (id_tarefa,))
    anexos = cursor.fetchall()
    conn.close()

    return render_template('anexos.html', tarefa=tarefa, anexos=anexos, id_tarefa=id_tarefa)

@app.route('/atribuicoes/<int:id_tarefa>', methods=['GET', 'POST'])
def atribuicoes(id_tarefa):
    if 'usuario' not in session:
        return redirect('/login')

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute('SELECT titulo, id_projeto FROM tarefas_tb WHERE id_tarefa = ?', (id_tarefa,))
    tarefa = cursor.fetchone()

    cursor.execute('SELECT id_usuario, nome_completo FROM usuarios_tb')
    usuarios = cursor.fetchall()

    if request.method == 'POST':
        id_usuario = request.form['id_usuario']
        papel = request.form['papel']
        cursor.execute('''
            INSERT INTO atribuicoes_tarefa_tb (id_tarefa, id_usuario, papel)
            VALUES (?, ?, ?)
        ''', (id_tarefa, id_usuario, papel))
        conn.commit()

    cursor.execute('''
        SELECT a.id_atribuicao, u.nome_completo, a.papel
        FROM atribuicoes_tarefa_tb a
        JOIN usuarios_tb u ON a.id_usuario = u.id_usuario
        WHERE a.id_tarefa = ?
    ''', (id_tarefa,))
    atribuicoes = cursor.fetchall()
    conn.close()

    return render_template('atribuicoes.html', tarefa=tarefa, usuarios=usuarios, atribuicoes=atribuicoes, id_tarefa=id_tarefa)

@app.route('/perfis', methods=['GET', 'POST'])
def perfis():
    if 'usuario' not in session:
        return redirect('/login')

    conn = conectar()
    cursor = conn.cursor()

    if request.method == 'POST':
        nome_perfil = request.form['nome_perfil']
        try:
            cursor.execute("INSERT INTO perfis_permissoes_tb (nome_perfil) VALUES (?)", (nome_perfil,))
            conn.commit()
        except sqlite3.IntegrityError:
            flash("Nome de perfil já existe.")
    cursor.execute('SELECT * FROM perfis_permissoes_tb')
    perfis = cursor.fetchall()

    conn.close()
    return render_template('perfis.html', perfis=perfis)

@app.route('/excluir_perfil/<int:id_perfil>', methods=['POST'])
def excluir_perfil(id_perfil):
    if 'usuario' not in session:
        return redirect('/login')

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM permissoes_tb WHERE id_perfil = ?", (id_perfil,))
    cursor.execute("DELETE FROM perfis_permissoes_tb WHERE id_perfil = ?", (id_perfil,))
    conn.commit()
    conn.close()
    flash("Perfil excluído com sucesso.")
    return redirect(url_for('perfis'))

@app.route('/perfis/<int:id_perfil>', methods=['GET', 'POST'])
def perfil_permissoes(id_perfil):
    if 'usuario' not in session:
        return redirect('/login')

    conn = conectar()
    cursor = conn.cursor()

    if request.method == 'POST':
        nome_permissao = request.form['nome_permissao']
        permitido = 1 if 'permitido' in request.form else 0
        cursor.execute('''
            INSERT INTO permissoes_tb (id_perfil, nome_permissao, permitido)
            VALUES (?, ?, ?)
        ''', (id_perfil, nome_permissao, permitido))
        conn.commit()

    cursor.execute('SELECT nome_perfil FROM perfis_permissoes_tb WHERE id_perfil = ?', (id_perfil,))
    perfil = cursor.fetchone()

    cursor.execute('SELECT * FROM permissoes_tb WHERE id_perfil = ?', (id_perfil,))
    permissoes = cursor.fetchall()

    conn.close()

    return render_template('perfil_permissoes.html', perfil=perfil, permissoes=permissoes, id_perfil=id_perfil)

@app.route('/excluir_permissao/<int:id_permissao>/<int:id_perfil>', methods=['POST'])
def excluir_permissao(id_permissao, id_perfil):
    if 'usuario' not in session:
        return redirect('/login')

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM permissoes_tb WHERE id_permissao = ?", (id_permissao,))
    conn.commit()
    conn.close()
    flash("Permissão excluída com sucesso.")
    return redirect(url_for('perfil_permissoes', id_perfil=id_perfil))

if __name__ == '__main__':
    app.run(debug=True)
