# ============================================================
# SIMULAÇÃO COMPUTACIONAL - AURORA SIGER
# ============================================================

from codigo_fonte import (
    inicializar_banco,
    simular_energia,
    executar_regressao,
    executar_decisoes,
    executar_agentes,
    analisar_sustentabilidade
)


def executar_simulacao():

    print("=" * 50)
    print("SIMULAÇÃO COMPUTACIONAL - AURORA SIGER")
    print("=" * 50)

    inicializar_banco()

    print("\nETAPA 1 - DECISÕES AUTOMÁTICAS")
    executar_decisoes()

    print("\nETAPA 2 - SIMULAÇÃO ENERGÉTICA")
    simular_energia()

    print("\nETAPA 3 - REGRESSÃO LINEAR")
    executar_regressao()

    print("\nETAPA 4 - SISTEMA MULTIAGENTE")
    executar_agentes()

    print("\nETAPA 5 - SUSTENTABILIDADE")
    analisar_sustentabilidade()

    print("\nSIMULAÇÃO FINALIZADA.")


if __name__ == "__main__":
    executar_simulacao()