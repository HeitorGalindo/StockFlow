from Backend.models import EstoqueModel
from flask import session
import os
from werkzeug.utils import secure_filename
import uuid

UPLOAD_FOLDER = 'Frontend/static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

db = EstoqueModel()

def cadastrar_produto_controller(form, arquivos):
    nome = form.get("nome")
    categoria = form.get("categoria") or "Sem categoria"
    try:
        preco_compra = float(form.get("preco_compra"))
        preco_revenda = float(form.get("preco_revenda"))
        quantidade = int(form.get("quantidade"))
    except (TypeError, ValueError):
        return
    descricao = form.get("descricao") or "Sem descrição"

    imagem = arquivos.get("imagem")
    caminho_imagem = "/static/no-image.png"

    if imagem and imagem.filename:
        extensao = os.path.splitext(imagem.filename)[1].lower()  
        nome_unico = f"{uuid.uuid4()}{extensao}"
        caminho_imagem_completo = os.path.join(UPLOAD_FOLDER, nome_unico)

        try:
            imagem.save(caminho_imagem_completo)
            caminho_imagem = f"/static/uploads/{nome_unico}"
        except Exception as e:
            print(f"Erro ao salvar a imagem: {e}")
            caminho_imagem = "/static/no-image.png"

    db.cadastrar_produto(
        nome=nome,
        categoria=categoria,
        descricao=descricao,
        preco=preco_revenda,
        quantidade=quantidade,
        preco_compra=preco_compra,
        preco_revenda=preco_revenda,
        imagem=caminho_imagem
    )
    return True

def listar_produtos_nomes_controller():
    return db.buscar_todos_produtos()

def listar_produtos_detalhes_controller():
    return db.buscar_relatorio_produtos()

def listar_produtos_para_venda():
    produtos = db.buscar_relatorio_produtos()
    return [p for p in produtos if isinstance(p.get("id"), int) and p["id"] > 0 and p["quantidade"] > 0]

def relatorio_produtos():
    return db.buscar_relatorio_produtos()

def relatorio_vendas():
    return db.buscar_relatorio_vendas()

def cadastrar_funcionario_controller(form):
    nome = form.get("nome")
    cargo = form.get("cargo")
    chegada = form.get("chegada")
    almoco = form.get("almoco")
    saida = form.get("saida")
    carga = int(form.get("carga"))
    db.inserir_funcionario(nome, cargo, chegada, almoco, saida, carga)

def listar_funcionarios_controller():
    return db.buscar_funcionarios()

def listar_vendedores_controller():
    return db.buscar_todos_vendedores()

def verificar_funcionario_controller(nome, cargo):
    funcionarios = db.buscar_funcionarios()
    for f in funcionarios:
        if f["nome"].lower() == nome.lower() and f["cargo"].lower() == cargo.lower():
            return True
    return False

def registrar_venda_controller(form):
    try:
        produto_id = int(form.get("produto_id"))
    except (ValueError, TypeError):
        return False
    quantidade = int(form.get("quantidade"))
    vendedor = session["usuario"]["nome"] if "usuario" in session else "Desconhecido"
    return db.registrar_venda(produto_id, quantidade, vendedor)


def listar_produtos_estoque_controller():
    produtos = db.buscar_relatorio_produtos()
    estoque_disponivel = []
    for p in produtos:
        if not p or not isinstance(p, dict):
            continue
        quantidade = p.get("quantidade", 0)
        nome = p.get("nome", "").strip()
        if isinstance(quantidade, int) and quantidade > 0 and nome:
            estoque_disponivel.append(p)
    return estoque_disponivel

def excluir_produto_controller(produto_id):
    produto = db.buscar_produto_por_id(produto_id)
    if produto and produto.get("imagem") and produto["imagem"] != "/static/no-image.png":
        caminho_absoluto = os.path.join(os.getcwd(), "Frontend", produto["imagem"].lstrip("/static/"))
        if os.path.exists(caminho_absoluto):
            os.remove(caminho_absoluto)
    db.excluir_produto(produto_id)