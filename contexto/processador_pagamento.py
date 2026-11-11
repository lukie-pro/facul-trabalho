"""
=============================================================================
 PAPEL NO PADRÃO STRATEGY: **Contexto**
=============================================================================

Segundo o Refactoring Guru:

    "O Contexto mantém uma referência para uma das estratégias concretas e
     se comunica com esse objeto através da interface da estratégia."
    "O contexto não sabe qual tipo de estratégia ele está trabalhando ou
     como o algoritmo é executado."

ESTE É O ARQUIVO MAIS IMPORTANTE DA APRESENTAÇÃO.

Procure por um `if forma_pagamento == ...` aqui dentro. Não existe nenhum.
O Contexto não importa PagamentoPix, nem PagamentoBoleto, nem nenhuma
estratégia concreta — só a interface EstrategiaPagamento. Por isso, para
adicionar "Vale-Refeição" amanhã, este arquivo não muda UMA LINHA.
=============================================================================
"""

from decimal import Decimal

from estrategias.estrategia_pagamento import EstrategiaPagamento
from modelos.pedido import Pedido
from modelos.resultado import ResultadoPagamento


class ProcessadorDePagamento:
    """
    O gateway de pagamento do restaurante.

    Responsabilidades que são DELE:
      - guardar a estratégia ativa;
      - manter o histórico de transações;
      - registrar log da operação.

    Responsabilidade que NÃO é dele:
      - saber como cada forma de pagamento cobra. Isso ele delega.
    """

    def __init__(self, estrategia: EstrategiaPagamento | None = None):
        """
        O Contexto aceita uma estratégia já no construtor (opcional).

        A anotação de tipo é `EstrategiaPagamento` — a INTERFACE. O Contexto
        nunca declara um tipo concreto.
        """
        self._estrategia = estrategia
        self._historico: list[ResultadoPagamento] = []

    def definir_estrategia(self, estrategia: EstrategiaPagamento) -> None:
        """
        O "setter" que permite trocar a estratégia EM TEMPO DE EXECUÇÃO.

        É este método que prova a frase-chave do padrão: trocar o algoritmo
        sem recriar o objeto que o usa. O mesmo processador atende Pix agora
        e cartão no segundo seguinte.
        """
        if not isinstance(estrategia, EstrategiaPagamento):
            raise TypeError(
                "A estratégia precisa implementar a interface EstrategiaPagamento."
            )
        self._estrategia = estrategia

    def simular_taxa(self, pedido: Pedido) -> Decimal:
        """
        Pergunta à estratégia ativa quanto ela cobraria, sem efetivar nada.

        Útil para mostrar ao cliente "no Pix sai mais barato" antes de cobrar.
        """
        self._garantir_estrategia()
        return self._estrategia.calcular_taxa(pedido.valor_total)

    def executar_pagamento(self, pedido: Pedido) -> ResultadoPagamento:
        """
        O coração do padrão: o Contexto DELEGA o trabalho para a estratégia.

        >>> COLOQUE O BREAKPOINT PRINCIPAL NA LINHA DO `self._estrategia.processar(...)`
        Dê Step Into (F11 no VS Code) e observe: dependendo de qual objeto
        está em `self._estrategia`, o depurador entra num arquivo DIFERENTE,
        mesmo sendo sempre a mesma linha de código aqui. Isso é polimorfismo.
        """
        self._garantir_estrategia()

        # O Contexto não sabe (e não quer saber) qual classe vai responder.
        # Ele só confia que o objeto cumpre o contrato da interface.
        resultado = self._estrategia.processar(pedido)

        self._historico.append(resultado)
        self._registrar_log(pedido, resultado)
        return resultado

    @property
    def estrategia_atual(self) -> str:
        """Nome da forma de pagamento ativa (ou aviso de que não há nenhuma)."""
        if self._estrategia is None:
            return "nenhuma estratégia definida"
        return self._estrategia.nome

    @property
    def historico(self) -> list[ResultadoPagamento]:
        """Cópia do histórico, para o chamador não alterar a lista interna."""
        return list(self._historico)

    def total_liquido_recebido(self) -> Decimal:
        """Soma do valor líquido de todas as transações aprovadas."""
        return sum(
            (r.valor_liquido for r in self._historico if r.sucesso),
            Decimal("0.00"),
        )

    def _garantir_estrategia(self) -> None:
        """Impede que o gateway rode sem forma de pagamento escolhida."""
        if self._estrategia is None:
            raise ValueError(
                "Nenhuma estratégia de pagamento foi definida. "
                "Use definir_estrategia() antes de cobrar."
            )

    def _registrar_log(self, pedido: Pedido, resultado: ResultadoPagamento) -> None:
        """Log simples no terminal — responsabilidade do Contexto, não da estratégia."""
        status = "OK " if resultado.sucesso else "ERRO"
        print(f"    [LOG {status}] pedido={pedido.numero} via {resultado.forma_pagamento}")
