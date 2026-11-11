"""
=============================================================================
 PAPEL NO PADRÃO STRATEGY: **Estratégia** (a interface comum)
=============================================================================

Segundo o Refactoring Guru:

    "A interface Estratégia é comum a todas as estratégias concretas.
     Ela declara um método que o contexto usa para executar uma estratégia."

Em Python não existe a palavra-chave `interface` como em Java ou C#. O
equivalente é uma Classe Base Abstrata (ABC) com métodos marcados como
@abstractmethod. O efeito é o mesmo:

  1. Quem herdar desta classe É OBRIGADO a implementar `calcular_taxa`,
     `processar` e a propriedade `nome` — senão o Python levanta TypeError
     na hora de instanciar.
  2. O Contexto consegue chamar qualquer estratégia sem saber qual é a
     classe concreta por trás. Isso é POLIMORFISMO.
=============================================================================
"""

from abc import ABC, abstractmethod
from decimal import Decimal, ROUND_HALF_UP

from modelos.pedido import Pedido
from modelos.resultado import ResultadoPagamento


def arredondar(valor: Decimal) -> Decimal:
    """
    Arredonda um valor monetário para 2 casas decimais.

    Usa ROUND_HALF_UP (meio para cima), que é a regra comercial brasileira.
    O padrão do Python é ROUND_HALF_EVEN, que arredondaria 0,125 para 0,12.
    """
    return valor.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


class EstrategiaPagamento(ABC):
    """
    Contrato que toda forma de pagamento do gateway precisa cumprir.

    O Contexto (ProcessadorDePagamento) conhece APENAS esta classe. Ele nunca
    importa PagamentoPix, PagamentoCartaoCredito etc. É por isso que dá para
    adicionar uma forma de pagamento nova sem tocar numa linha do Contexto
    (Princípio Aberto/Fechado do SOLID).
    """

    @property
    @abstractmethod
    def nome(self) -> str:
        """Nome da forma de pagamento, como aparece no comprovante."""
        raise NotImplementedError

    @abstractmethod
    def calcular_taxa(self, valor: Decimal) -> Decimal:
        """
        Calcula quanto a operadora/banco cobra para processar este valor.

        Cada forma de pagamento tem sua própria fórmula: percentual, taxa
        fixa, percentual + fixa, ou taxa zero. É exatamente essa variação
        que o Strategy encapsula.
        """
        raise NotImplementedError

    @abstractmethod
    def processar(self, pedido: Pedido) -> ResultadoPagamento:
        """
        Executa a cobrança do pedido e devolve um resultado padronizado.

        Este é "o método que o contexto usa para executar uma estratégia".
        """
        raise NotImplementedError

    def __str__(self) -> str:
        """Facilita a leitura do objeto durante a depuração."""
        return f"<Estratégia: {self.nome}>"
