# ============================================================
# SIFSM - SISTEMA INTEGRADO DE FUTURO SUSTENTÁVEL EM MARTE
# MISSÃO AURORA SIGER
# ============================================================

import sqlite3
import csv
import heapq
import math

from pathlib import Path
from collections import deque
from contextlib import contextmanager


# ============================================================
# CONFIGURAÇÕES
# ============================================================

PASTA = Path(__file__).resolve().parent

BANCO = PASTA / "aurora_siger.db"
ARQUIVO_SQL = PASTA / "banco_aurora_siger.sql"
ARQUIVO_CSV = PASTA / "dados_aurora_siger.csv"

fila_solicitacoes = deque()

CAPACIDADE_BATERIA = 800.0
ENERGIA_INICIAL = 400.0
EFICIENCIA_CARGA = 0.95


# ============================================================
# 1. CONEXÃO COM BANCO DE DADOS
# ============================================================

@contextmanager
def conectar():
    conexao = sqlite3.connect(BANCO)

    conexao.row_factory = sqlite3.Row
    conexao.execute("PRAGMA foreign_keys = ON")

    try:
        yield conexao
        conexao.commit()

    except Exception:
        conexao.rollback()
        raise

    finally:
        conexao.close()


def inicializar_banco():

    if BANCO.exists():
        return

    if not ARQUIVO_SQL.exists():
        raise FileNotFoundError(
            "Arquivo banco_aurora_siger.sql não encontrado."
        )

    if not ARQUIVO_CSV.exists():
        raise FileNotFoundError(
            "Arquivo dados_aurora_siger.csv não encontrado."
        )

    with conectar() as conexao:

        script = ARQUIVO_SQL.read_text(
            encoding="utf-8"
        )

        conexao.executescript(script)

        modulo = conexao.execute(
            """
            SELECT id
            FROM modulos
            WHERE nome = ?
            """,
            ("Centro de Controle",)
        ).fetchone()

        modulo_id = modulo["id"]

        with open(
            ARQUIVO_CSV,
            "r",
            encoding="utf-8"
        ) as arquivo:

            leitor = csv.DictReader(arquivo)

            for linha in leitor:

                conexao.execute(
                    """
                    INSERT INTO leituras_sensores (
                        modulo_id,
                        ciclo_horas,
                        geracao_kw,
                        consumo_kw,
                        umidade_percentual,
                        agua_percentual,
                        temperatura_c,
                        sensores_validos
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        modulo_id,
                        float(linha["ciclo_horas"]),
                        float(linha["geracao_kw"]),
                        float(linha["consumo_kw"]),
                        float(linha["umidade_percentual"]),
                        float(linha["agua_percentual"]),
                        float(linha["temperatura_c"]),
                        int(linha["sensores_validos"])
                    )
                )

    print("Banco de dados inicializado com sucesso.")


# ============================================================
# 2. CRUD - CREATE
# ============================================================

def cadastrar_modulo():

    print("\n===== CADASTRAR MÓDULO =====")

    nome = input("Nome: ").strip()
    tipo = input("Tipo: ").strip()

    try:
        consumo = float(input("Consumo em kW: "))
        prioridade = int(input("Prioridade (1-5): "))

        if consumo < 0 or not 1 <= prioridade <= 5:
            print("Valores fora dos limites permitidos.")
            return

        with conectar() as conexao:

            conexao.execute(
                """
                INSERT INTO modulos
                (nome, tipo, consumo_kw, prioridade, status)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    nome,
                    tipo,
                    consumo,
                    prioridade,
                    "ativo"
                )
            )

        print("Módulo cadastrado com sucesso.")

    except (ValueError, sqlite3.IntegrityError) as erro:
        print("Erro no cadastro:", erro)


# ============================================================
# 3. CRUD - READ
# ============================================================

def visualizar_modulos():

    with conectar() as conexao:

        registros = conexao.execute(
            "SELECT * FROM modulos ORDER BY id"
        ).fetchall()

    print("\n===== MÓDULOS DA COLÔNIA =====")

    for modulo in registros:

        print(
            f"\nID: {modulo['id']}"
            f"\nNome: {modulo['nome']}"
            f"\nTipo: {modulo['tipo']}"
            f"\nConsumo: {modulo['consumo_kw']} kW"
            f"\nPrioridade: {modulo['prioridade']}"
            f"\nStatus: {modulo['status']}"
        )


def consultar_modulo():

    try:
        identificador = int(input("ID do módulo: "))

        with conectar() as conexao:

            modulo = conexao.execute(
                "SELECT * FROM modulos WHERE id = ?",
                (identificador,)
            ).fetchone()

        if modulo:

            print("\n===== MÓDULO ENCONTRADO =====")

            for chave in modulo.keys():
                print(f"{chave}: {modulo[chave]}")

        else:
            print("Módulo não encontrado.")

    except ValueError:
        print("ID inválido.")


# ============================================================
# 4. CRUD - UPDATE
# ============================================================

def atualizar_modulo():

    try:
        identificador = int(input("ID do módulo: "))

        consumo = float(
            input("Novo consumo em kW: ")
        )

        status = input(
            "Novo status (ativo/manutencao/alerta): "
        ).strip().lower()

        if consumo < 0:
            print("Consumo não pode ser negativo.")
            return

        if status not in (
            "ativo",
            "manutencao",
            "alerta"
        ):
            print("Status inválido.")
            return

        with conectar() as conexao:

            cursor = conexao.execute(
                """
                UPDATE modulos
                SET consumo_kw = ?, status = ?
                WHERE id = ?
                """,
                (consumo, status, identificador)
            )

            alterados = cursor.rowcount

        if alterados:
            print("Módulo atualizado.")
        else:
            print("Módulo não encontrado.")

    except ValueError:
        print("Entrada inválida.")


# ============================================================
# 5. CRUD - DELETE
# ============================================================

def excluir_modulo():

    try:
        identificador = int(input("ID do módulo: "))

        confirmar = input(
            "Confirmar exclusão? (s/n): "
        ).lower()

        if confirmar != "s":
            print("Operação cancelada.")
            return

        with conectar() as conexao:

            cursor = conexao.execute(
                "DELETE FROM modulos WHERE id = ?",
                (identificador,)
            )

            excluidos = cursor.rowcount

        if excluidos:
            print("Módulo excluído.")
        else:
            print("Módulo não encontrado.")

    except ValueError:
        print("ID inválido.")


# ============================================================
# 6. CONSULTA DE SENSORES
# ============================================================

def obter_leituras():

    with conectar() as conexao:

        leituras = conexao.execute(
            """
            SELECT *
            FROM leituras_sensores
            ORDER BY ciclo_horas
            """
        ).fetchall()

    return leituras


def consultar_sensores():

    print("\n===== SENSORES DA COLÔNIA =====")

    for leitura in obter_leituras():

        print(
            f"\nCiclo: {leitura['ciclo_horas']} h"
            f"\nGeração: {leitura['geracao_kw']} kW"
            f"\nConsumo: {leitura['consumo_kw']} kW"
            f"\nUmidade: {leitura['umidade_percentual']}%"
            f"\nÁgua: {leitura['agua_percentual']}%"
            f"\nTemperatura: {leitura['temperatura_c']}°C"
        )


# ============================================================
# 7. REGRAS BOOLEANAS
# ============================================================

def verificar_irrigacao(
    modulo_ativo,
    umidade,
    nivel_agua,
    sensores_validos
):

    umidade_baixa = umidade < 40
    agua_disponivel = nivel_agua > 20

    autorizada = (
        modulo_ativo
        and umidade_baixa
        and agua_disponivel
        and sensores_validos
    )

    return autorizada


def executar_decisoes():

    leituras = obter_leituras()

    if not leituras:
        print("Nenhuma leitura disponível.")
        return

    ultima = leituras[-1]

    with conectar() as conexao:

        agricultura = conexao.execute(
            """
            SELECT status
            FROM modulos
            WHERE nome = 'Agricultura'
            """
        ).fetchone()

    modulo_ativo = (
        agricultura is not None
        and agricultura["status"] == "ativo"
    )

    irrigacao = verificar_irrigacao(
        modulo_ativo,
        ultima["umidade_percentual"],
        ultima["agua_percentual"],
        bool(ultima["sensores_validos"])
    )

    print("\n===== DECISÕES AUTOMÁTICAS =====")

    if irrigacao:
        print("IRRIGAÇÃO AUTORIZADA NA SIMULAÇÃO.")
    else:
        print("IRRIGAÇÃO BLOQUEADA.")

    geracao = ultima["geracao_kw"]
    consumo = ultima["consumo_kw"]

    if consumo > geracao:
        print("ALERTA: consumo maior que geração.")

    elif geracao > consumo:
        print("SUGESTÃO: armazenar energia excedente.")

    else:
        print("Sistema energético em equilíbrio.")

    print(
        "As decisões são simuladas e não acionam "
        "equipamentos reais."
    )


# ============================================================
# 8. FILAS
# ============================================================

def gerenciar_solicitacoes():

    print("\n===== GERENCIAMENTO DE SOLICITAÇÕES =====")

    print("1 - Adicionar solicitação")
    print("2 - Atender próxima solicitação")
    print("3 - Visualizar fila")

    opcao = input("Escolha: ")

    if opcao == "1":

        solicitacao = input("Solicitação: ").strip()

        if solicitacao:
            fila_solicitacoes.append(solicitacao)
            print("Solicitação adicionada.")

    elif opcao == "2":

        if fila_solicitacoes:
            print(
                "Atendendo:",
                fila_solicitacoes.popleft()
            )
        else:
            print("Fila vazia.")

    elif opcao == "3":

        print(list(fila_solicitacoes))


# ============================================================
# 9. HEAP - PRIORIDADE DE ALERTAS
# ============================================================

def priorizar_alertas():

    with conectar() as conexao:

        alertas = conexao.execute(
            """
            SELECT
                a.id,
                m.nome,
                a.descricao,
                a.prioridade
            FROM alertas a
            JOIN modulos m ON m.id = a.modulo_id
            WHERE a.status = 'pendente'
            """
        ).fetchall()

    heap = []

    for alerta in alertas:

        heapq.heappush(
            heap,
            (
                -alerta["prioridade"],
                alerta["id"],
                alerta["nome"],
                alerta["descricao"]
            )
        )

    print("\n===== ALERTAS PRIORIZADOS =====")

    while heap:

        prioridade, identificador, modulo, descricao = (
            heapq.heappop(heap)
        )

        print(
            f"Prioridade {-prioridade} | "
            f"{modulo} | {descricao}"
        )


# ============================================================
# 10. GRAFOS E BFS
# ============================================================

GRAFO = {

    "Armazenamento de Energia": [
        "Habitação",
        "Centro de Controle",
        "Agricultura"
    ],

    "Habitação": [
        "Armazenamento de Energia",
        "Suporte Médico",
        "Produção de Oxigênio"
    ],

    "Centro de Controle": [
        "Armazenamento de Energia",
        "Comunicação",
        "Laboratório Científico"
    ],

    "Agricultura": [
        "Armazenamento de Energia",
        "Produção de Oxigênio",
        "Laboratório Científico"
    ],

    "Laboratório Científico": [
        "Centro de Controle",
        "Agricultura"
    ],

    "Comunicação": [
        "Centro de Controle"
    ],

    "Suporte Médico": [
        "Habitação"
    ],

    "Produção de Oxigênio": [
        "Habitação",
        "Agricultura"
    ]
}


def bfs(origem, destino):

    if origem not in GRAFO or destino not in GRAFO:
        return []

    fila = deque([(origem, [origem])])
    visitados = {origem}

    while fila:

        atual, caminho = fila.popleft()

        if atual == destino:
            return caminho

        for vizinho in GRAFO[atual]:

            if vizinho not in visitados:

                visitados.add(vizinho)

                fila.append(
                    (vizinho, caminho + [vizinho])
                )

    return []


def consultar_rede():

    print("\n===== REDE DA COLÔNIA =====")

    for modulo, vizinhos in GRAFO.items():

        print(f"\n{modulo}:")

        for vizinho in vizinhos:
            print(" ->", vizinho)

    origem = input("\nOrigem: ")
    destino = input("Destino: ")

    caminho = bfs(origem, destino)

    if caminho:
        print("\nCaminho encontrado:")
        print(" -> ".join(caminho))
    else:
        print("Caminho não encontrado.")


# ============================================================
# 11. INTEGRAÇÃO NUMÉRICA E ENERGIA
# ============================================================

def simular_energia():

    leituras = obter_leituras()

    if len(leituras) < 2:
        print("Dados insuficientes.")
        return

    energia = ENERGIA_INICIAL

    print("\n===== SIMULAÇÃO ENERGÉTICA =====")

    print(f"Capacidade: {CAPACIDADE_BATERIA} kWh")
    print(f"Reserva inicial: {energia} kWh")

    for indice in range(1, len(leituras)):

        anterior = leituras[indice - 1]
        atual = leituras[indice]

        tempo = (
            atual["ciclo_horas"]
            - anterior["ciclo_horas"]
        )

        if tempo <= 0:
            continue

        saldo_anterior = (
            anterior["geracao_kw"]
            - anterior["consumo_kw"]
        )

        saldo_atual = (
            atual["geracao_kw"]
            - atual["consumo_kw"]
        )

        # Regra dos trapézios

        variacao = (
            (saldo_anterior + saldo_atual)
            / 2
        ) * tempo

        if variacao > 0:
            variacao *= EFICIENCIA_CARGA

        energia += variacao

        energia = max(
            0,
            min(CAPACIDADE_BATERIA, energia)
        )

        print(
            f"Ciclo {atual['ciclo_horas']:.0f} h | "
            f"Reserva: {energia:.2f} kWh"
        )

    print(
        f"\nReserva final: {energia:.2f} kWh"
    )


# ============================================================
# 12. REGRESSÃO LINEAR
# ============================================================

def calcular_regressao(x, y):

    n = len(x)

    media_x = sum(x) / n
    media_y = sum(y) / n

    numerador = sum(
        (x[i] - media_x) * (y[i] - media_y)
        for i in range(n)
    )

    denominador = sum(
        (valor - media_x) ** 2
        for valor in x
    )

    if denominador == 0:
        raise ValueError("Não há variação em x.")

    b = numerador / denominador
    a = media_y - b * media_x

    return a, b


def executar_regressao():

    leituras = obter_leituras()

    if len(leituras) < 4:
        print("Dados insuficientes.")
        return

    # Treino com os primeiros registros.
    # Teste com os dois últimos.

    treino = leituras[:-2]
    teste = leituras[-2:]

    x_treino = [
        linha["ciclo_horas"]
        for linha in treino
    ]

    y_treino = [
        linha["consumo_kw"]
        for linha in treino
    ]

    a, b = calcular_regressao(
        x_treino,
        y_treino
    )

    erros = []

    print("\n===== REGRESSÃO LINEAR =====")

    print(f"Modelo: C(t) = {a:.3f} + {b:.3f}t")

    for linha in teste:

        real = linha["consumo_kw"]

        previsto = (
            a + b * linha["ciclo_horas"]
        )

        erros.append(real - previsto)

        print(
            f"Real: {real:.2f} kW | "
            f"Previsto: {previsto:.2f} kW"
        )

    mae = sum(
        abs(erro) for erro in erros
    ) / len(erros)

    mse = sum(
        erro ** 2 for erro in erros
    ) / len(erros)

    rmse = math.sqrt(mse)

    print(f"\nMAE: {mae:.3f}")
    print(f"MSE: {mse:.3f}")
    print(f"RMSE: {rmse:.3f}")

    proximo_ciclo = (
        leituras[-1]["ciclo_horas"] + 1
    )

    previsao = a + b * proximo_ciclo

    print(
        f"\nConsumo previsto para o ciclo "
        f"{proximo_ciclo:.0f}: "
        f"{previsao:.2f} kW"
    )


# ============================================================
# 13. AGENTES INTELIGENTES SIMULADOS
# ============================================================

def agente_energia(leitura):

    geracao = leitura["geracao_kw"]
    consumo = leitura["consumo_kw"]

    if consumo > geracao:
        return (
            "AGENTE ENERGÉTICO: "
            "recomenda reduzir cargas não essenciais."
        )

    return (
        "AGENTE ENERGÉTICO: "
        "geração suficiente no ciclo analisado."
    )


def agente_ambiental(leitura):

    umidade = leitura["umidade_percentual"]
    agua = leitura["agua_percentual"]

    if agua <= 20:
        return (
            "AGENTE AMBIENTAL: "
            "reserva de água insuficiente."
        )

    if umidade < 40:
        return (
            "AGENTE AMBIENTAL: "
            "recomenda avaliar irrigação."
        )

    return (
        "AGENTE AMBIENTAL: "
        "umidade dentro do limite simulado."
    )


def agente_manutencao():

    with conectar() as conexao:

        alerta = conexao.execute(
            """
            SELECT descricao, prioridade
            FROM alertas
            WHERE status = 'pendente'
            ORDER BY prioridade DESC
            LIMIT 1
            """
        ).fetchone()

    if alerta:

        return (
            "AGENTE DE MANUTENÇÃO: "
            f"prioridade {alerta['prioridade']} - "
            f"{alerta['descricao']}"
        )

    return "AGENTE DE MANUTENÇÃO: sem alertas pendentes."


def executar_agentes():

    leituras = obter_leituras()

    if not leituras:
        print("Sem leituras disponíveis.")
        return

    ultima = leituras[-1]

    print("\n===== SISTEMA MULTIAGENTE =====")

    print("\nCoordenador encaminhando solicitações...")

    print(agente_energia(ultima))
    print(agente_ambiental(ultima))
    print(agente_manutencao())

    print(
        "\nGUARDRAIL: recomendações críticas "
        "dependem de validação humana."
    )


# ============================================================
# 14. SUSTENTABILIDADE
# ============================================================

def analisar_sustentabilidade():

    leituras = obter_leituras()

    if not leituras:
        return

    ultima = leituras[-1]

    print("\n===== SUSTENTABILIDADE =====")

    geracao = ultima["geracao_kw"]
    consumo = ultima["consumo_kw"]

    print(f"Geração: {geracao} kW")
    print(f"Consumo: {consumo} kW")

    if consumo > geracao:

        print(
            "Recomendação: reduzir consumo "
            "de sistemas não essenciais."
        )

    else:

        print(
            "Recomendação: aproveitar o excedente "
            "para armazenamento."
        )

    print(
        "\nPrincípios ESG:"
        "\n- Eficiência energética"
        "\n- Uso responsável da água"
        "\n- Transparência das decisões"
        "\n- Supervisão humana"
        "\n- Planejamento sustentável"
    )


# ============================================================
# 15. ARQUITETURA COMPUTACIONAL
# ============================================================

def arquitetura_computacional():

    print("\n===== ARQUITETURA COMPUTACIONAL =====")

    print("""
CPU:
Executa o Python, o banco SQLite e as regras.

GPU:
Poderia acelerar simulações paralelas.

NPU:
Poderia executar modelos locais de IA.

TPU:
Exemplo de acelerador especializado
em aprendizado de máquina.

RAM:
Mantém dados temporários em execução.

SSD:
Armazena o banco de dados.

BARRAMENTOS:
Transportam informações entre componentes.

CHIPLETS:
Permitem organizar componentes computacionais
em múltiplos blocos integrados.
""")


# ============================================================
# 16. MENU PRINCIPAL
# ============================================================

def menu():

    inicializar_banco()

    while True:

        print("\n======================================")
        print("       SIFSM - AURORA SIGER")
        print("======================================")

        print("1  - Visualizar módulos")
        print("2  - Cadastrar módulo")
        print("3  - Consultar módulo")
        print("4  - Atualizar módulo")
        print("5  - Excluir módulo")
        print("6  - Consultar sensores")
        print("7  - Executar decisões automáticas")
        print("8  - Exibir regra lógica")
        print("9  - Gerenciar solicitações")
        print("10 - Priorizar alertas")
        print("11 - Consultar rede da colônia")
        print("12 - Simular energia")
        print("13 - Calcular energia acumulada")
        print("14 - Executar regressão linear")
        print("15 - Executar agentes inteligentes")
        print("16 - Analisar sustentabilidade")
        print("17 - Arquitetura computacional")
        print("0  - Sair")

        opcao = input("\nEscolha uma opção: ")

        if opcao == "1":
            visualizar_modulos()

        elif opcao == "2":
            cadastrar_modulo()

        elif opcao == "3":
            consultar_modulo()

        elif opcao == "4":
            atualizar_modulo()

        elif opcao == "5":
            excluir_modulo()

        elif opcao == "6":
            consultar_sensores()

        elif opcao == "7":
            executar_decisoes()

        elif opcao == "8":
            print(
                "\nI = A AND U AND R AND S"
                "\nA = módulo ativo"
                "\nU = umidade baixa"
                "\nR = água disponível"
                "\nS = sensores válidos"
            )

        elif opcao == "9":
            gerenciar_solicitacoes()

        elif opcao == "10":
            priorizar_alertas()

        elif opcao == "11":
            consultar_rede()

        elif opcao in ("12", "13"):
            simular_energia()

        elif opcao == "14":
            executar_regressao()

        elif opcao == "15":
            executar_agentes()

        elif opcao == "16":
            analisar_sustentabilidade()

        elif opcao == "17":
            arquitetura_computacional()

        elif opcao == "0":
            print("Encerrando SIFSM...")
            break

        else:
            print("Opção inválida.")


if __name__ == "__main__":
    menu()