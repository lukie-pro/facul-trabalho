"""
=============================================================================
 PAPEL NO PADRÃO STRATEGY: **Cliente**
=============================================================================

Segundo o Refactoring Guru:

    "O Cliente cria um objeto estratégia específico e passa ele para o
     contexto. O contexto expõe um setter que permite o cliente mudar a
     estratégia associada com contexto durante a execução."

Ou seja: a decisão de QUAL forma de pagamento usar é do Cliente (aqui, o
menu do PDV). O Contexto só executa.

COMO RODAR:
    python main.py
=============================================================================
"""

from decimal import Decimal

from contexto.processador_pagamento import ProcessadorDePagamento
from estrategias.estrategia_pagamento import EstrategiaPagamento
from estrategias.pagamento_boleto import PagamentoBoleto
from estrategias.pagamento_cartao_credito import PagamentoCartaoCredito
from estrategias.pagamento_dinheiro import PagamentoDinheiro
from estrategias.pagamento_pix import PagamentoPix
from modelos.pedido import Pedido

CNPJ_RESTAURANTE = "12.345.678/0001-90"
CHAVE_PIX_RESTAURANTE = "pagamentos@restaurante.com.br"


def montar_pedido_exemplo() -> Pedido:
    """Cria um pedido de restaurante para servir de base nas demonstrações."""
    pedido = Pedido(numero="2026-0847", cliente="Marina Albuquerque")
    pedido.adicionar_item("Moqueca de peixe (serve 2)", 1, "189.90")
    pedido.adicionar_item("Água de coco", 3, "12.00")
    pedido.adicionar_item("Pudim de tapioca", 2, "24.50")
    return pedido


def separador(titulo: str = "") -> None:
    """Imprime uma linha divisória com título, só para deixar o console legível."""
    if titulo:
        print(f"\n{'=' * 70}\n {titulo}\n{'=' * 70}")
    else:
        print("-" * 70)


# ---------------------------------------------------------------------------
# DEMONSTRAÇÃO 1 — a troca de estratégia em tempo de execução
# ---------------------------------------------------------------------------
def demonstrar_troca_em_tempo_de_execucao() -> None:
    """
    Roda o MESMO pedido no MESMO processador com as quatro formas de pagamento.

    >>> ESTA É A FUNÇÃO PARA DEMONSTRAR NO DEPURADOR.
    O objeto `processador` é criado UMA única vez, fora do laço. O que muda a
    cada volta é só o objeto dentro de `processador._estrategia`.
    """
    separador("DEMONSTRAÇÃO 1 — Trocando a estratégia em tempo de execução")

    pedido = montar_pedido_exemplo()
    print(pedido.resumo())

    # O Contexto é criado UMA vez. Note que ele nasce sem estratégia nenhuma.
    processador = ProcessadorDePagamento()

    # O Cliente monta a lista de estratégias concretas. Cada uma recebe os
    # dados que só ela precisa (chave Pix, bandeira, CNPJ, valor em caixa).
    estrategias: list[EstrategiaPagamento] = [
        PagamentoPix(chave_pix=CHAVE_PIX_RESTAURANTE),
        PagamentoCartaoCredito(bandeira="Visa", numero_mascarado="**** 4417", parcelas=1),
        PagamentoCartaoCredito(bandeira="Visa", numero_mascarado="**** 4417", parcelas=6),
        PagamentoBoleto(cnpj_beneficiario=CNPJ_RESTAURANTE),
        PagamentoDinheiro(valor_recebido="300.00", operador_caixa="andre"),
    ]

    for estrategia in estrategias:
        separador()
        # <<< BREAKPOINT 1: a troca de estratégia acontece aqui.
        processador.definir_estrategia(estrategia)
        print(f"  Forma selecionada: {processador.estrategia_atual}")

        # <<< BREAKPOINT 2: dê Step Into aqui e depois de novo no `processar`.
        resultado = processador.executar_pagamento(pedido)
        print(resultado)

    separador()
    aprovadas = [r for r in processador.historico if r.sucesso]
    print(f"  Transações registradas .... {len(processador.historico)}")
    print(f"  Aprovadas ................. {len(aprovadas)}")
    print(f"  Total líquido no caixa .... R$ {processador.total_liquido_recebido()}")


# ---------------------------------------------------------------------------
# DEMONSTRAÇÃO 2 — comparando o custo de cada forma antes de cobrar
# ---------------------------------------------------------------------------
def demonstrar_comparacao_de_taxas() -> None:
    """
    Usa `simular_taxa` para mostrar quanto cada forma custaria ao restaurante.

    Mostra que o método `calcular_taxa` tem a MESMA assinatura em todas as
    estratégias, mas fórmulas completamente diferentes por baixo.
    """
    separador("DEMONSTRAÇÃO 2 — Qual forma de pagamento custa menos?")

    pedido = montar_pedido_exemplo()
    processador = ProcessadorDePagamento()

    opcoes: list[EstrategiaPagamento] = [
        PagamentoPix(chave_pix=CHAVE_PIX_RESTAURANTE),
        PagamentoCartaoCredito(bandeira="Visa", numero_mascarado="**** 4417"),
        PagamentoBoleto(cnpj_beneficiario=CNPJ_RESTAURANTE),
        PagamentoDinheiro(valor_recebido="300.00", operador_caixa="andre"),
    ]

    print(f"  Valor do pedido: R$ {pedido.valor_total}\n")
    print(f"  {'FORMA DE PAGAMENTO':<36} {'TAXA':>12} {'FICA PARA A CASA':>18}")
    print(f"  {'-' * 36} {'-' * 12} {'-' * 18}")

    for opcao in opcoes:
        processador.definir_estrategia(opcao)
        taxa = processador.simular_taxa(pedido)
        liquido = pedido.valor_total - taxa
        print(f"  {opcao.nome:<36} {('R$ ' + str(taxa)):>12} {('R$ ' + str(liquido)):>18}")


# ---------------------------------------------------------------------------
# DEMONSTRAÇÃO 3 — as validações próprias de cada estratégia
# ---------------------------------------------------------------------------
def demonstrar_recusas() -> None:
    """
    Mostra que cada estratégia tem suas PRÓPRIAS regras de recusa.

    O Contexto recebe a recusa pela mesma interface de sempre — ele não
    precisa aprender nenhuma regra nova para lidar com isso.
    """
    separador("DEMONSTRAÇÃO 3 — Cada estratégia tem suas próprias regras")

    processador = ProcessadorDePagamento()

    # Caso A: pedido caro demais para o limite do Pix.
    pedido_caro = Pedido(numero="2026-0848", cliente="Evento Corporativo")
    pedido_caro.adicionar_item("Buffet fechado para 60 pessoas", 1, "7400.00")
    processador.definir_estrategia(PagamentoPix(chave_pix=CHAVE_PIX_RESTAURANTE))
    print(f"\n  A) Pix de R$ {pedido_caro.valor_total} (limite R$ 5000,00):")
    print(f"  {processador.executar_pagamento(pedido_caro)}")

    # Caso B: pedido barato demais para compensar um boleto.
    pedido_barato = Pedido(numero="2026-0849", cliente="Cliente do balcão")
    pedido_barato.adicionar_item("Café expresso", 1, "8.00")
    processador.definir_estrategia(PagamentoBoleto(cnpj_beneficiario=CNPJ_RESTAURANTE))
    print(f"\n  B) Boleto de R$ {pedido_barato.valor_total} (mínimo R$ 20,00):")
    print(f"  {processador.executar_pagamento(pedido_barato)}")

    # Caso C: cliente entregou menos dinheiro do que a conta.
    pedido_normal = montar_pedido_exemplo()
    processador.definir_estrategia(
        PagamentoDinheiro(valor_recebido="100.00", operador_caixa="andre")
    )
    print(f"\n  C) Dinheiro: conta de R$ {pedido_normal.valor_total}, cliente deu R$ 100,00:")
    print(f"  {processador.executar_pagamento(pedido_normal)}")

    # Caso D: parcelamento acima do permitido.
    processador.definir_estrategia(
        PagamentoCartaoCredito(bandeira="Elo", numero_mascarado="**** 9023", parcelas=18)
    )
    print(f"\n  D) Cartão em 18x (máximo 12x):")
    print(f"  {processador.executar_pagamento(pedido_normal)}")


# ---------------------------------------------------------------------------
# MENU — ponto de entrada do programa
# ---------------------------------------------------------------------------
def main() -> None:
    """Menu do PDV. É aqui que o Cliente escolhe o que demonstrar."""
    opcoes = {
        "1": ("Trocar a estratégia em tempo de execução", demonstrar_troca_em_tempo_de_execucao),
        "2": ("Comparar as taxas de cada forma", demonstrar_comparacao_de_taxas),
        "3": ("Ver as recusas de cada estratégia", demonstrar_recusas),
    }

    while True:
        separador("GATEWAY DE PAGAMENTO — Padrão Strategy")
        for chave, (rotulo, _) in opcoes.items():
            print(f"  {chave}) {rotulo}")
        print("  0) Rodar tudo e sair")
        print("  q) Sair")

        escolha = input("\n  Escolha uma opção: ").strip().lower()

        if escolha == "q":
            print("\n  Até mais!\n")
            break
        if escolha == "0":
            for _, funcao in opcoes.values():
                funcao()
            print()
            break
        if escolha in opcoes:
            opcoes[escolha][1]()
        else:
            print("\n  Opção inválida.")


if __name__ == "__main__":
    main()
