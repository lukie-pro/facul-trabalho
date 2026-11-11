"""
=============================================================================
 PAPEL NO PADRÃO STRATEGY: **Estratégia Concreta** nº 1
=============================================================================
Implementa a variação "Pix" do algoritmo de cobrança.
=============================================================================
"""

import uuid
from decimal import Decimal

from estrategias.estrategia_pagamento import EstrategiaPagamento, arredondar
from modelos.pedido import Pedido
from modelos.resultado import ResultadoPagamento


class PagamentoPix(EstrategiaPagamento):
    """
    Cobrança via Pix.

    Regras de negócio desta estratégia:
      - Taxa de 0,99% sobre o valor da transação.
      - Crédito na conta é imediato.
      - Existe um teto por transação (limite antifraude noturno, por ex.).

    Repare que a chave Pix e o limite são DADOS PRÓPRIOS desta estratégia.
    Nenhuma outra classe precisa saber que eles existem — nem o Contexto.
    """

    TAXA_PERCENTUAL = Decimal("0.0099")  # 0,99%

    def __init__(self, chave_pix: str, limite_por_transacao: str = "5000.00"):
        self._chave_pix = chave_pix
        self._limite = Decimal(limite_por_transacao)

    @property
    def nome(self) -> str:
        return "Pix"

    def calcular_taxa(self, valor: Decimal) -> Decimal:
        """Taxa do Pix: percentual puro, sem valor fixo."""
        return arredondar(valor * self.TAXA_PERCENTUAL)

    def processar(self, pedido: Pedido) -> ResultadoPagamento:
        """Gera a cobrança Pix e devolve o resultado padronizado."""
        valor = pedido.valor_total

        # Validação específica do Pix: acima do limite, a transação é barrada.
        if valor > self._limite:
            return ResultadoPagamento(
                sucesso=False,
                forma_pagamento=self.nome,
                valor_bruto=valor,
                taxa=Decimal("0.00"),
                valor_liquido=Decimal("0.00"),
                prazo_recebimento="-",
                identificador="-",
                mensagem=f"Valor acima do limite de R$ {self._limite} por transação Pix.",
            )

        taxa = self.calcular_taxa(valor)

        # O "txid" é o identificador da cobrança Pix no padrão do Banco Central.
        txid = uuid.uuid4().hex[:25].upper()

        return ResultadoPagamento(
            sucesso=True,
            forma_pagamento=self.nome,
            valor_bruto=arredondar(valor),
            taxa=taxa,
            valor_liquido=arredondar(valor - taxa),
            prazo_recebimento="Imediato",
            identificador=txid,
            mensagem="QR Code gerado e pagamento confirmado pelo PSP.",
            detalhes={"chave_pix": self._chave_pix},
        )
