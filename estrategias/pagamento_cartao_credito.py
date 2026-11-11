"""
=============================================================================
 PAPEL NO PADRÃO STRATEGY: **Estratégia Concreta** nº 2
=============================================================================
Implementa a variação "Cartão de Crédito" do algoritmo de cobrança.
=============================================================================
"""

import random
from decimal import Decimal

from estrategias.estrategia_pagamento import EstrategiaPagamento, arredondar
from modelos.pedido import Pedido
from modelos.resultado import ResultadoPagamento


class PagamentoCartaoCredito(EstrategiaPagamento):
    """
    Cobrança via cartão de crédito.

    Regras de negócio desta estratégia:
      - Taxa da adquirente: 3,19% + R$ 0,39 por transação.
      - Parcelamento acima de 1x acrescenta 1,99% ao mês sobre o valor.
      - Recebimento em 30 dias (prazo típico da adquirente).
      - Máximo de 12 parcelas.

    Note que o algoritmo aqui é BEM mais complexo que o do Pix. Essa é a
    razão de existir do padrão: sem ele, toda essa lógica estaria dentro de
    um `if forma == "cartao"` no meio do processador de pagamento.
    """

    TAXA_PERCENTUAL = Decimal("0.0319")   # 3,19% da adquirente
    TAXA_FIXA = Decimal("0.39")           # R$ 0,39 por transação
    JUROS_PARCELAMENTO = Decimal("0.0199")  # 1,99% ao mês
    MAXIMO_PARCELAS = 12

    def __init__(self, bandeira: str, numero_mascarado: str, parcelas: int = 1):
        self._bandeira = bandeira
        self._numero_mascarado = numero_mascarado
        self._parcelas = parcelas

    @property
    def nome(self) -> str:
        """O nome muda conforme o parcelamento — aparece assim no comprovante."""
        if self._parcelas > 1:
            return f"Cartão de Crédito {self._bandeira} ({self._parcelas}x)"
        return f"Cartão de Crédito {self._bandeira} (à vista)"

    def calcular_taxa(self, valor: Decimal) -> Decimal:
        """Taxa do cartão: percentual + valor fixo por transação."""
        return arredondar(valor * self.TAXA_PERCENTUAL + self.TAXA_FIXA)

    def _aplicar_juros(self, valor: Decimal) -> Decimal:
        """
        Aplica juros de parcelamento ao valor cobrado do cliente.

        Fórmula de juros simples: valor * (1 + taxa * (parcelas - 1)).
        À vista (1 parcela) não há acréscimo nenhum.
        """
        if self._parcelas <= 1:
            return valor
        acrescimo = self.JUROS_PARCELAMENTO * (self._parcelas - 1)
        return arredondar(valor * (Decimal("1") + acrescimo))

    def processar(self, pedido: Pedido) -> ResultadoPagamento:
        """Autoriza a transação na adquirente e devolve o resultado."""
        valor_original = pedido.valor_total

        # Validação específica do cartão: limite de parcelas.
        if self._parcelas < 1 or self._parcelas > self.MAXIMO_PARCELAS:
            return ResultadoPagamento(
                sucesso=False,
                forma_pagamento=self.nome,
                valor_bruto=valor_original,
                taxa=Decimal("0.00"),
                valor_liquido=Decimal("0.00"),
                prazo_recebimento="-",
                identificador="-",
                mensagem=f"Parcelamento inválido. Permitido de 1 a {self.MAXIMO_PARCELAS}x.",
            )

        valor_cobrado = self._aplicar_juros(valor_original)
        taxa = self.calcular_taxa(valor_cobrado)
        valor_parcela = arredondar(valor_cobrado / self._parcelas)

        # NSU = Número Sequencial Único, o código que a maquininha imprime.
        nsu = f"{random.randint(100000, 999999)}"

        return ResultadoPagamento(
            sucesso=True,
            forma_pagamento=self.nome,
            valor_bruto=valor_cobrado,
            taxa=taxa,
            valor_liquido=arredondar(valor_cobrado - taxa),
            prazo_recebimento="30 dias",
            identificador=f"NSU {nsu}",
            mensagem="Transação autorizada pela adquirente.",
            detalhes={
                "cartao": self._numero_mascarado,
                "parcelas": f"{self._parcelas}x de R$ {valor_parcela}",
                "juros_embutidos": f"R$ {arredondar(valor_cobrado - valor_original)}",
            },
        )
