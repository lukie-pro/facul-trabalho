"""
=============================================================================
 PAPEL NO PADRÃO STRATEGY: **Estratégia Concreta** nº 3
=============================================================================
Implementa a variação "Boleto Bancário" do algoritmo de cobrança.
=============================================================================
"""

import random
from datetime import date, timedelta
from decimal import Decimal

from estrategias.estrategia_pagamento import EstrategiaPagamento, arredondar
from modelos.pedido import Pedido
from modelos.resultado import ResultadoPagamento


class PagamentoBoleto(EstrategiaPagamento):
    """
    Cobrança via boleto bancário.

    Regras de negócio desta estratégia:
      - Taxa FIXA de R$ 3,49 por boleto emitido (não é percentual!).
      - Compensação em até 3 dias úteis após o pagamento.
      - Valor mínimo de R$ 20,00 (abaixo disso a taxa inviabiliza a venda).

    Compare com o Pix: aqui a taxa não depende do valor. É o mesmo "método"
    `calcular_taxa` com uma fórmula completamente diferente — polimorfismo.
    """

    TAXA_FIXA = Decimal("3.49")
    VALOR_MINIMO = Decimal("20.00")

    def __init__(self, cnpj_beneficiario: str, dias_para_vencimento: int = 3):
        self._cnpj_beneficiario = cnpj_beneficiario
        self._dias_para_vencimento = dias_para_vencimento

    @property
    def nome(self) -> str:
        return "Boleto Bancário"

    def calcular_taxa(self, valor: Decimal) -> Decimal:
        """
        Taxa do boleto: valor fixo, independente do total do pedido.

        O parâmetro `valor` é ignorado de propósito — a assinatura precisa
        ser igual à da interface para que as estratégias sejam intercambiáveis.
        """
        return self.TAXA_FIXA

    def _gerar_linha_digitavel(self) -> str:
        """Gera uma linha digitável fictícia no formato visual de 47 dígitos."""
        blocos = [
            f"{random.randint(10000, 99999)}.{random.randint(10000, 99999)}",
            f"{random.randint(10000, 99999)}.{random.randint(100000, 999999)}",
            f"{random.randint(10000, 99999)}.{random.randint(100000, 999999)}",
            f"{random.randint(1, 9)}",
            f"{random.randint(10000000000000, 99999999999999)}",
        ]
        return " ".join(blocos)

    def processar(self, pedido: Pedido) -> ResultadoPagamento:
        """Emite o boleto e devolve o resultado padronizado."""
        valor = pedido.valor_total

        # Validação específica do boleto: valor mínimo.
        if valor < self.VALOR_MINIMO:
            return ResultadoPagamento(
                sucesso=False,
                forma_pagamento=self.nome,
                valor_bruto=valor,
                taxa=Decimal("0.00"),
                valor_liquido=Decimal("0.00"),
                prazo_recebimento="-",
                identificador="-",
                mensagem=f"Boleto exige valor mínimo de R$ {self.VALOR_MINIMO}.",
            )

        taxa = self.calcular_taxa(valor)
        vencimento = date.today() + timedelta(days=self._dias_para_vencimento)

        return ResultadoPagamento(
            sucesso=True,
            forma_pagamento=self.nome,
            valor_bruto=arredondar(valor),
            taxa=taxa,
            valor_liquido=arredondar(valor - taxa),
            prazo_recebimento="Até 3 dias úteis após o pagamento",
            identificador=self._gerar_linha_digitavel(),
            mensagem="Boleto registrado no banco e enviado ao cliente.",
            detalhes={
                "beneficiario": self._cnpj_beneficiario,
                "vencimento": vencimento.strftime("%d/%m/%Y"),
            },
        )
