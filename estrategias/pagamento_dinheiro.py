"""
=============================================================================
 PAPEL NO PADRÃO STRATEGY: **Estratégia Concreta** nº 4
=============================================================================
Implementa a variação "Dinheiro" do algoritmo de cobrança.
=============================================================================
"""

from decimal import Decimal

from estrategias.estrategia_pagamento import EstrategiaPagamento, arredondar
from modelos.pedido import Pedido
from modelos.resultado import ResultadoPagamento


class PagamentoDinheiro(EstrategiaPagamento):
    """
    Cobrança em espécie, no caixa.

    Regras de negócio desta estratégia:
      - Taxa ZERO: não existe intermediário cobrando nada.
      - Recebimento imediato.
      - Precisa calcular o TROCO, algo que nenhuma outra forma faz.
      - Se o cliente entregar menos que o total, o pagamento é recusado.

    Esta estratégia é a prova de que o Contexto não precisa saber de nada:
    o cálculo de troco só existe aqui dentro, e mesmo assim o Contexto
    consegue executá-la com exatamente a mesma chamada das outras três.
    """

    def __init__(self, valor_recebido: str, operador_caixa: str):
        self._valor_recebido = Decimal(valor_recebido)
        self._operador_caixa = operador_caixa

    @property
    def nome(self) -> str:
        return "Dinheiro"

    def calcular_taxa(self, valor: Decimal) -> Decimal:
        """Dinheiro em espécie não tem taxa de intermediação."""
        return Decimal("0.00")

    def processar(self, pedido: Pedido) -> ResultadoPagamento:
        """Confere o valor recebido, calcula o troco e fecha a venda."""
        valor = pedido.valor_total

        # Validação específica do dinheiro: o cliente entregou o suficiente?
        if self._valor_recebido < valor:
            falta = arredondar(valor - self._valor_recebido)
            return ResultadoPagamento(
                sucesso=False,
                forma_pagamento=self.nome,
                valor_bruto=valor,
                taxa=Decimal("0.00"),
                valor_liquido=Decimal("0.00"),
                prazo_recebimento="-",
                identificador="-",
                mensagem=f"Valor insuficiente. Faltam R$ {falta}.",
            )

        taxa = self.calcular_taxa(valor)
        troco = arredondar(self._valor_recebido - valor)

        return ResultadoPagamento(
            sucesso=True,
            forma_pagamento=self.nome,
            valor_bruto=arredondar(valor),
            taxa=taxa,
            valor_liquido=arredondar(valor - taxa),
            prazo_recebimento="Imediato",
            identificador=f"CAIXA-{self._operador_caixa.upper()}",
            mensagem="Pagamento recebido no caixa.",
            detalhes={
                "recebido": f"R$ {arredondar(self._valor_recebido)}",
                "troco": f"R$ {troco}",
            },
        )
