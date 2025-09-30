from flask import Flask, render_template, request, send_file, send_from_directory
import os
import csv
from datetime import datetime

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
CSV_FILE = "cadastros.csv"

# Cria pastas e CSV se não existirem
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Data", "Nome", "CPF", "Instituição", "E-mail", "Telefone", "Arquivo"])

@app.route("/")
def index():
    return render_template("form.html")

@app.route("/enviar", methods=["POST"])
def enviar():
    nome = request.form["nome"]
    cpf = request.form["cpf"]
    instituicao = request.form["instituicao"]
    email_usuario = request.form["email_usuario"]
    telefone = request.form["telefone"]

    # Salvar arquivo, se houver
    arquivo = request.files.get("arquivo")
    nome_arquivo = ""
    if arquivo and arquivo.filename != "":
        nome_arquivo = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{arquivo.filename}"
        caminho = os.path.join(UPLOAD_FOLDER, nome_arquivo)
        arquivo.save(caminho)

    # Salvar dados no CSV
    with open(CSV_FILE, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), nome, cpf, instituicao, email_usuario, telefone, nome_arquivo])

    return "✅ Cadastro enviado com sucesso!"

# Rota para baixar o CSV
@app.route("/baixar-csv")
def baixar_csv():
    return send_file(CSV_FILE, as_attachment=True)

# Rota para visualizar uploads
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

# Rota para listar arquivos da pasta uploads
@app.route('/ver-uploads')
def ver_uploads():
    arquivos = os.listdir(UPLOAD_FOLDER)
    arquivos = [f for f in arquivos if os.path.isfile(os.path.join(UPLOAD_FOLDER, f))]
    links = [f"<a href='/uploads/{a}' target='_blank'>{a}</a>" for a in arquivos]
    return "<br>".join(links)

# Rota para listar cadastros
@app.route("/lista")
def lista():
    cadastros = []
    with open(CSV_FILE, mode='r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            cadastros.append(row)
    # Mostra cada cadastro com link para arquivo se houver
    html = "<h2>Lista de Cadastros</h2><table border='1' cellpadding='5'><tr><th>Data</th><th>Nome</th><th>CPF</th><th>Instituição</th><th>E-mail</th><th>Telefone</th><th>Arquivo</th></tr>"
    for c in cadastros:
        arquivo_link = f"<a href='/uploads/{c['Arquivo']}' target='_blank'>{c['Arquivo']}</a>" if c['Arquivo'] else ""
        html += f"<tr><td>{c['Data']}</td><td>{c['Nome']}</td><td>{c['CPF']}</td><td>{c['Instituição']}</td><td>{c['E-mail']}</td><td>{c['Telefone']}</td><td>{arquivo_link}</td></tr>"
    html += "</table>"
    html += "<br><a href='/baixar-csv'>Baixar CSV</a><br>"
    html += "<a href='/ver-uploads'>Ver arquivos enviados</a>"
    return html

if __name__ == "__main__":
    app.run(debug=True)













