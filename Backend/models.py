from datetime import datetime
from Banco.conexao import conectar_banco

class EstoqueModel:
    def __init__(self):
        self.criar_banco()
        self.conexao = conectar_banco()
        self.cursor = self.conexao.cursor()
        self.criar_tabelas()
        self.resetar_banco()

    def criar_banco(self):
        conexao_temp = conectar_banco(criar_database=True)
        cursor_temp = conexao_temp.cursor()
        cursor_temp.execute("CREATE DATABASE IF NOT EXISTS estoque")
        conexao_temp.commit()
        conexao_temp.close()

    def criar_tabelas(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS produtos (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nome VARCHAR(100) NOT NULL,
                categoria VARCHAR(100),
                descricao VARCHAR(100),
                quantidade INT NOT NULL,
                preco DECIMAL(10, 2) NOT NULL,
                preco_compra DECIMAL(10, 2) DEFAULT 0,
                preco_revenda DECIMAL(10, 2) DEFAULT 0,
                imagem TEXT,
                data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS vendas (
                id INT AUTO_INCREMENT PRIMARY KEY,
                produto_id INT,
                vendedor VARCHAR(100),
                quantidade INT NOT NULL,
                data_venda DATETIME NOT NULL,
                FOREIGN KEY (produto_id) REFERENCES produtos(id)
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS funcionarios (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nome VARCHAR(100) NOT NULL,
                cargo VARCHAR(100),
                chegada TIME,
                almoco TIME,
                saida TIME,
                carga INT
            )
        """)
        self.conexao.commit()

    def cadastrar_produto(self, nome, categoria, descricao, preco, quantidade, preco_compra, preco_revenda, imagem=None):
        if imagem is None or imagem.strip() == "":
            imagem = "/static/no-image.png"
        self.cursor.execute("""
            INSERT INTO produtos (nome, categoria, descricao, preco, quantidade, preco_compra, preco_revenda, imagem)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (nome, categoria, descricao, preco, quantidade, preco_compra, preco_revenda, imagem))
        self.conexao.commit()

    def buscar_todos_produtos(self):
        self.cursor.execute("""
            SELECT id, nome, categoria, descricao, quantidade, preco, preco_compra, preco_revenda, imagem, data_cadastro
            FROM produtos
            ORDER BY nome ASC
        """)
        return [
            {
                "id": id,
                "nome": nome,
                "categoria": categoria,
                "descricao": descricao,
                "quantidade": quantidade,
                "preco": float(preco),
                "preco_compra": float(preco_compra or 0),
                "preco_revenda": float(preco_revenda or 0),
                "lucro_unitario": float(preco_revenda or 0) - float(preco_compra or 0),
                "imagem": imagem,
                "data_cadastro": data_cadastro
            }
            for (id, nome, categoria, descricao, quantidade, preco, preco_compra, preco_revenda, imagem, data_cadastro) in self.cursor.fetchall()
        ]

    def buscar_relatorio_produtos(self):
        self.cursor.execute("""
            SELECT id, nome, categoria, descricao, quantidade, preco, preco_compra, preco_revenda, imagem, data_cadastro
            FROM produtos
            WHERE quantidade > 0
            ORDER BY nome ASC
        """)
        return [
            {
                "id": id,
                "nome": nome,
                "categoria": categoria,
                "descricao": descricao,
                "quantidade": qtd,
                "preco": float(preco),
                "preco_compra": float(preco_compra or 0),
                "preco_revenda": float(preco_revenda or 0),
                "lucro_unitario": float(preco_revenda or 0) - float(preco_compra or 0),
                "imagem": imagem,
                "data_cadastro": data_cadastro
            }
            for (id, nome, categoria, descricao, qtd, preco, preco_compra, preco_revenda, imagem, data_cadastro) in self.cursor.fetchall()
        ]

    def buscar_relatorio_vendas(self):
        self.cursor.execute("""
            SELECT p.nome, v.vendedor, v.quantidade, v.data_venda, p.preco_compra, p.preco_revenda
            FROM vendas v
            JOIN produtos p ON v.produto_id = p.id
            ORDER BY v.data_venda DESC
        """)
        return [
            {
                "nome_produto": nome,
                "vendedor": vendedor,
                "quantidade": qtd,
                "data_venda": data,
                "lucro_total": (float(preco_revenda or 0) - float(preco_compra or 0)) * qtd
            }
            for (nome, vendedor, qtd, data, preco_compra, preco_revenda) in self.cursor.fetchall()
        ]

    def buscar_todos_vendedores(self):
        self.cursor.execute("SELECT nome FROM funcionarios WHERE LOWER(cargo) = 'vendedor'")
        return [nome for (nome,) in self.cursor.fetchall()]

    def registrar_venda(self, produto_id, quantidade, vendedor):
        try:
            produto_id = int(produto_id)
            quantidade = int(quantidade)
        except ValueError:
            return False

        self.cursor.execute("SELECT quantidade FROM produtos WHERE id = %s", (produto_id,))
        resultado = self.cursor.fetchone()

        while self.cursor.nextset():
            pass

        if resultado:
            estoque_atual = resultado[0]
            if estoque_atual >= quantidade:
                nova_qtd = estoque_atual - quantidade
                self.cursor.execute("UPDATE produtos SET quantidade = %s WHERE id = %s", (nova_qtd, produto_id))
                self.conexao.commit()
                self.cursor.execute("""
                    INSERT INTO vendas (produto_id, vendedor, quantidade, data_venda)
                    VALUES (%s, %s, %s, %s)
                """, (produto_id, vendedor, quantidade, datetime.now()))
                self.conexao.commit()
                return True
        return False

    def inserir_funcionario(self, nome, cargo, chegada, almoco, saida, carga):
        self.cursor.execute("""
            INSERT INTO funcionarios (nome, cargo, chegada, almoco, saida, carga)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (nome, cargo, chegada, almoco, saida, carga))
        self.conexao.commit()

    def buscar_funcionarios(self):
        self.cursor.execute("SELECT nome, cargo, chegada, almoco, saida, carga FROM funcionarios")
        return [
            {
                "nome": nome,
                "cargo": cargo,
                "chegada": str(chegada),
                "almoco": str(almoco),
                "saida": str(saida),
                "carga": carga
            }
            for (nome, cargo, chegada, almoco, saida, carga) in self.cursor.fetchall()
        ]

    def resetar_banco(self):
        self.cursor.execute("DELETE FROM vendas")
        self.cursor.execute("DELETE FROM produtos")
        self.cursor.execute("DELETE FROM funcionarios")
        self.conexao.commit()
        self.cursor.execute("""
            INSERT INTO funcionarios (nome, cargo, chegada, almoco, saida, carga)
            VALUES ('admin', 'adm', '08:00:00', '12:00:00', '18:00:00', 8)
        """)
        self.conexao.commit()

    def buscar_produto_por_id(self, produto_id):
        self.cursor.execute("SELECT * FROM produtos WHERE id = %s", (produto_id,))
        resultado = self.cursor.fetchone()
        if resultado:
            colunas = [col[0] for col in self.cursor.description]
            return dict(zip(colunas, resultado))
        return None
    def excluir_produto(self, produto_id):
        self.cursor.execute("DELETE FROM produtos WHERE id = %s", (produto_id,))
        self.conexao.commit()