from flask import Flask, render_template, request, send_file, redirect, url_for, session, Response
import os
from datetime import datetime
from io import BytesIO, StringIO
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
import csv

# -------------------- CONFIGURAÇÃO --------------------
load_dotenv()
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret")  # fallback dev

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Credenciais do admin
ADMIN_USER = os.environ.get("ADMIN_USER")
ADMIN_PASS = os.environ.get("ADMIN_PASS")

# -------------------- CONTEXT MANAGER --------------------
DATABASE_URL = os.environ.get("DATABASE_URL")

@contextmanager
def get_conn_cursor():
    """Abre conexão + cursor, fecha automaticamente no final"""
    conn = psycopg2.connect(DATABASE_URL)
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            yield conn, cursor
        conn.commit()
    finally:
        conn.close()

# -------------------- CRIAÇÃO DE TABELA --------------------
with get_conn_cursor() as (conn, cursor):
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cadastros (
        id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        data TIMESTAMP DEFAULT NOW(),
        nome TEXT,
        cpf TEXT,
        instituicao TEXT,
        email_usuario TEXT,
        telefone TEXT,
        nome_arquivo TEXT,
        arquivo_bytes BYTEA,
        lgpd_aceite TEXT
    )
    """)

# -------------------- FUNÇÕES AUXILIARES --------------------
def salvar_cadastro(nome, cpf, instituicao, email_usuario, telefone, nome_arquivo, arquivo_bytes, lgpd_aceite):
    with get_conn_cursor() as (conn, cursor):
        cursor.execute("""
            INSERT INTO cadastros (nome, cpf, instituicao, email_usuario, telefone, nome_arquivo, arquivo_bytes, lgpd_aceite)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (nome, cpf, instituicao, email_usuario, telefone, nome_arquivo, arquivo_bytes, lgpd_aceite))

def listar_cadastros():
    with get_conn_cursor() as (conn, cursor):
        cursor.execute("SELECT * FROM cadastros ORDER BY id DESC")
        return cursor.fetchall()

def obter_arquivo(cadastro_id):
    with get_conn_cursor() as (conn, cursor):
        cursor.execute("SELECT nome_arquivo, arquivo_bytes FROM cadastros WHERE id = %s", (cadastro_id,))
        return cursor.fetchone()

# -------------------- ROTAS PÚBLICAS --------------------
@app.route("/")
def index():
    return render_template("form.html")

@app.route("/enviar", methods=["POST"])
def enviar():
    nome = request.form.get("nome", "")
    cpf = request.form.get("cpf", "")
    instituicao = request.form.get("instituicao", "")
    email_usuario = request.form.get("email_usuario", "")
    telefone = request.form.get("telefone", "")
    lgpd_aceite = request.form.get("lgpd_aceite", "Não informado")

    arquivo = request.files.get("arquivo")
    nome_arquivo = None
    arquivo_bytes = None
    if arquivo and arquivo.filename != "":
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        nome_arquivo = f"{timestamp}_{arquivo.filename}"
        arquivo_bytes = arquivo.read()

    salvar_cadastro(nome, cpf, instituicao, email_usuario, telefone, nome_arquivo, arquivo_bytes, lgpd_aceite)
    return render_template("obrigado.html", nome=nome, instituicao=instituicao)

# -------------------- ROTAS ADMIN --------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form.get("usuario")
        senha = request.form.get("senha")
        if usuario == ADMIN_USER and senha == ADMIN_PASS:
            session["logged_in"] = True
            return redirect(url_for("lista"))
        else:
            return render_template("login.html", error="❌ Usuário ou senha inválidos")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("logged_in", None)
    return redirect(url_for("login"))

@app.route("/lista")
def lista():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    cadastros = listar_cadastros()
    return render_template("lista.html", cadastros=cadastros)

@app.route("/baixar-csv")
def baixar_csv():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["Data", "Nome", "CPF", "Instituição", "E-mail", "Telefone", "Arquivo", "LGPD"])
    for c in listar_cadastros():
        writer.writerow([
            c['data'], c['nome'], c['cpf'], c['instituicao'],
            c['email_usuario'], c['telefone'], c['nome_arquivo'], c['lgpd_aceite']
        ])
    output.seek(0)
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=cadastros.csv"}
    )

@app.route("/uploads/<int:cadastro_id>")
def uploads(cadastro_id):
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    arquivo = obter_arquivo(cadastro_id)
    if not arquivo or not arquivo['arquivo_bytes']:
        return "Arquivo não encontrado", 404
    return send_file(BytesIO(arquivo['arquivo_bytes']), download_name=arquivo['nome_arquivo'], as_attachment=True)

# -------------------- ROTA LIMPAR TUDO --------------------
@app.route("/limpar-tudo", methods=["POST"])
def limpar_tudo():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    with get_conn_cursor() as (conn, cursor):
        cursor.execute("DELETE FROM cadastros")
        conn.commit()

    return redirect(url_for("lista"))

# -------------------- MAIN --------------------
if __name__ == "__main__":
    app.run(debug=True)
