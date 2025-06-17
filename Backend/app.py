from flask import Flask, render_template, request, redirect, url_for, session
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from controllers import (
    cadastrar_produto_controller,
    listar_produtos_nomes_controller,
    listar_vendedores_controller,
    listar_produtos_para_venda,
    relatorio_produtos,
    relatorio_vendas,
    cadastrar_funcionario_controller,
    listar_funcionarios_controller,
    verificar_funcionario_controller,
    registrar_venda_controller,
    listar_produtos_estoque_controller,
    excluir_produto_controller,
)

from models import EstoqueModel

app = Flask(
    __name__,
    template_folder="../Frontend/templates",
    static_url_path='/static',
    static_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), "../Frontend/static"))
)
app.secret_key = 'chave-secreta-muito-segura'
app.config['JSON_AS_ASCII'] = False
db = EstoqueModel()

def usuario_logado():
    return "usuario" in session

def cargo_eh(cargos):
    return usuario_logado() and session["usuario"]["cargo"].lower() in cargos

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        nome = request.form.get("nome")
        cargo = request.form.get("cargo").lower()
        if verificar_funcionario_controller(nome, cargo):
            session["usuario"] = {"nome": nome, "cargo": cargo}
            return redirect(url_for("index"))
        else:
            return render_template("login.html", erro=True)
    return render_template("login.html")

@app.route("/")
def index():
    if not usuario_logado():
        return redirect(url_for("login"))
    return render_template("index.html", usuario=session["usuario"])

@app.route("/produtos", methods=["GET", "POST"])
def produtos():
    if not cargo_eh(["gerente", "adm"]):
        return redirect(url_for("index"))
    if request.method == "POST":
        sucesso = cadastrar_produto_controller(request.form, request.files)
        if not sucesso:
            vendedores = listar_vendedores_controller()
            return render_template("produtos.html", vendedores=vendedores, erro=True)
        return redirect(url_for("produtos"))
    vendedores = listar_vendedores_controller()
    return render_template("produtos.html", vendedores=vendedores)

@app.route("/vendas", methods=["GET", "POST"])
def vendas():
    if not cargo_eh(["vendedor", "adm"]):
        return redirect(url_for("index"))
    produtos = [p for p in listar_produtos_para_venda() if p.get("id")]
    return render_template("vendas.html", produtos=produtos)

@app.route("/registrar_venda", methods=["POST"])
def registrar_venda():
    if not cargo_eh(["vendedor", "adm"]):
        return redirect(url_for("index"))
    sucesso = registrar_venda_controller(request.form)
    if not sucesso:
        produtos = [p for p in listar_produtos_para_venda() if p.get("id")]
        return render_template("vendas.html", produtos=produtos, erro=True)
    return redirect(url_for("vendas"))

@app.route("/relatorios")
def relatorios():
    if not cargo_eh(["gerente", "adm"]):
        return redirect(url_for("index"))
    produtos = relatorio_produtos()
    vendas = relatorio_vendas()
    lucro_total_geral = sum(v["lucro_total"] for v in vendas)
    return render_template("relatorios.html", produtos=produtos, vendas=vendas, lucro_total_geral=lucro_total_geral)

@app.route("/estoque")
def estoque():
    if not cargo_eh(["gerente", "adm","vendedor"]):
        return redirect(url_for("index"))
    produtos = listar_produtos_estoque_controller()
    return render_template("estoque.html", produtos=produtos)

@app.route("/funcionarios", methods=["GET", "POST"])
def funcionarios():
    if not cargo_eh(["adm"]):
        return redirect(url_for("index"))
    if request.method == "POST":
        cadastrar_funcionario_controller(request.form)
        return redirect(url_for("funcionarios"))
    lista_funcionarios = listar_funcionarios_controller()
    return render_template("funcionarios.html", funcionarios=lista_funcionarios)

@app.route("/resetar_banco")
def resetar_banco():
    if not cargo_eh(["adm"]):
        return redirect(url_for("index"))
    db.resetar_banco()
    return "<h3>Banco resetado com sucesso!</h3><a href='/'>Voltar ao início</a>"

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/excluir_produto/<int:produto_id>", methods=["POST"])
def excluir_produto(produto_id):
    if not cargo_eh(["gerente", "adm"]):
        return redirect(url_for("index"))
    excluir_produto_controller(produto_id)
    return redirect(url_for("estoque"))

@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404

if __name__ != "__main__":
    gunicorn_app = app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)