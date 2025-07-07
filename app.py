from flask import Flask, render_template, request, redirect, session
import sqlite3
import os
from werkzeug.utils import secure_filename
from models import init_db

app = Flask(__name__)
app.secret_key = "segredo123"
init_db()

UPLOAD_FOLDER = 'static/imagens'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

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
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']
        conn = conectar()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO usuarios_tb (nome_completo, email, senha) VALUES (?, ?, ?)", (nome, email, senha))
            conn.commit()
            return redirect('/login')
        except sqlite3.IntegrityError:
            return render_template('cadastro.html', error="Email já cadastrado.")
        finally:
            conn.close()
    return render_template('cadastro.html')

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
    conn.close()

    nome = user_data[0]
    imagem = user_data[1] if user_data[1] else "imagem.jpg"

    return render_template('dashboard.html', nome=nome, imagem=imagem, mensagem=mensagem)

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
    conn.close()
    return render_template('equipes.html', equipes=equipes)

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

if __name__ == '__main__':
    app.run(debug=True)
