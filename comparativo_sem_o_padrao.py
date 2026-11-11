"""
=============================================================================
 ARQUIVO DE APOIO PARA A APRESENTAÇÃO — **NÃO FAZ PARTE DO SISTEMA**
=============================================================================

Este arquivo mostra como o MESMO gateway ficaria SEM o padrão Strategy.
Ele existe só para a comparação "antes x depois" na apresentação.

Use-o para responder a pergunta mais provável do professor:
    "Por que vocês não resolveram isso com um simples if/elif?"

Problemas visíveis no código abaixo:

  1. CONDICIONAL GIGANTE — uma cadeia de if/elif que cresce a cada nova
     forma de pagamento. O Refactoring Guru lista isso como gatilho direto
     para aplicar o Strategy.

  2. VIOLA O PRINCÍPIO ABERTO/FECHADO — para aceitar Vale-Refeição amanhã,
     é obrigatório EDITAR esta classe. Na versão com Strategy, basta criar
     um arquivo novo e não tocar em nada do que já funciona.

  3. VIOLA O PRINCÍPIO DA RESPONSABILIDADE ÚNICA — uma classe só sabe as
     regras do Pix, do cartão, do boleto e do dinheiro ao mesmo tempo.

  4. PARÂMETROS QUE SÓ SERVEM PARA UM CASO — repare em `valor_recebido`,
     `parcelas` e `bandeira`: ficam no método sempre, mas só são usados por
     uma forma de pagamento cada. Quem chama precisa passar None o tempo todo.

  5. DIFÍCIL DE TESTAR — não dá para testar a regra do boleto isoladamente
     sem passar por todo o resto do método.

  6. CONFLITO DE MERGE EM EQUIPE — todo mundo edita o mesmo arquivo.
=============================================================================
"""

from decimal import Decimal

from estrategias.estrategia_pagamento import arredondar
from modelos.pedido import Pedido


class ProcessadorDePagamentoRuim:
    """A versão inchada, que o padrão Strategy veio resolver."""

    def processar(
        self,
        pedido: Pedido,
        forma: str,
        parcelas: int = 1,
        bandeira: str | None = None,
        valor_recebido: Decimal | None = None,
        chave_pix: str | None = None,
    ) -> str:
        """
        Um único método que tenta dar conta de tudo.

        Compare este método com o `executar_pagamento` do Contexto na versão
        com padrão: lá são 3 linhas de lógica, aqui são dezenas — e crescendo.
        """
        valor = pedido.valor_total

        # ------------------------------------------------- PIX
        if forma == "pix":
            if valor > Decimal("5000.00"):
                return "[RECUSADO] Acima do limite do Pix."
            taxa = arredondar(valor * Decimal("0.0099"))
            return f"[APROVADO] Pix | taxa R$ {taxa} | líquido R$ {arredondar(valor - taxa)}"

        # ------------------------------------------------- CARTÃO DE CRÉDITO
        elif forma == "cartao":
            if parcelas < 1 or parcelas > 12:
                return "[RECUSADO] Parcelamento inválido."
            if parcelas > 1:
                acrescimo = Decimal("0.0199") * (parcelas - 1)
                valor = arredondar(valor * (Decimal("1") + acrescimo))
            taxa = arredondar(valor * Decimal("0.0319") + Decimal("0.39"))
            return (
                f"[APROVADO] Cartão {bandeira} {parcelas}x | taxa R$ {taxa} "
                f"| líquido R$ {arredondar(valor - taxa)}"
            )

        # ------------------------------------------------- BOLETO
        elif forma == "boleto":
            if valor < Decimal("20.00"):
                return "[RECUSADO] Abaixo do mínimo para boleto."
            taxa = Decimal("3.49")
            return f"[APROVADO] Boleto | taxa R$ {taxa} | líquido R$ {arredondar(valor - taxa)}"

        # ------------------------------------------------- DINHEIRO
        elif forma == "dinheiro":
            if valor_recebido is None or valor_recebido < valor:
                return "[RECUSADO] Valor insuficiente."
            troco = arredondar(valor_recebido - valor)
            return f"[APROVADO] Dinheiro | troco R$ {troco} | líquido R$ {arredondar(valor)}"

        # ------------------------------------------------- E amanhã?
        # elif forma == "vale_refeicao":   <- precisa editar ESTA classe
        # elif forma == "pix_parcelado":   <- de novo
        # elif forma == "cripto":          <- de novo...

        return "[ERRO] Forma de pagamento desconhecida."


if __name__ == "__main__":
    pedido = Pedido(numero="2026-0847", cliente="Marina Albuquerque")
    pedido.adicionar_item("Moqueca de peixe (serve 2)", 1, "189.90")
    pedido.adicionar_item("Água de coco", 3, "12.00")
    pedido.adicionar_item("Pudim de tapioca", 2, "24.50")

    processador = ProcessadorDePagamentoRuim()

    print("\n  VERSÃO SEM O PADRÃO STRATEGY (para comparação)\n")
    print(" ", processador.processar(pedido, "pix"))
    print(" ", processador.processar(pedido, "cartao", parcelas=6, bandeira="Visa"))
    print(" ", processador.processar(pedido, "boleto"))
    print(" ", processador.processar(pedido, "dinheiro", valor_recebido=Decimal("300.00")))
    print("\n  Repare: quem chama precisa saber de parcelas, bandeira E valor_recebido,")
    print("  mesmo quando a forma escolhida não usa nenhum deles.\n")
