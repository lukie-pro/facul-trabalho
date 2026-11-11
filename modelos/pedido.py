"""
Modelo de domínio: o Pedido que será pago.

Esta classe NÃO faz parte do padrão Strategy. Ela é apenas o dado que
circula pelo sistema. Está aqui para que o exemplo seja um cenário real
(um pedido de um restaurante) e não um exemplo abstrato.
"""

from dataclasses import dataclass, field
from decimal import Decimal


@dataclass
class ItemPedido:
    """Uma linha do pedido: um produto, sua quantidade e o preço unitário."""

    descricao: str
    quantidade: int
    preco_unitario: Decimal

    @property
    def subtotal(self) -> Decimal:
        """Quanto esta linha representa no total do pedido."""
        return self.preco_unitario * self.quantidade


@dataclass
class Pedido:
    """
    Representa um pedido fechado, pronto para ser pago.

    O Pedido não sabe NADA sobre formas de pagamento. Essa é justamente a
    vantagem do padrão Strategy: a regra de "como cobrar" mora em outro lugar.
    """

    numero: str
    cliente: str
    itens: list[ItemPedido] = field(default_factory=list)

    def adicionar_item(self, descricao: str, quantidade: int, preco_unitario: str) -> None:
        """Adiciona um produto ao pedido. O preço vem como texto e vira Decimal."""
        self.itens.append(
            ItemPedido(
                descricao=descricao,
                quantidade=quantidade,
                # Decimal a partir de string evita o erro clássico de float com dinheiro
                # (0.1 + 0.2 != 0.3). Em sistema financeiro, nunca use float.
                preco_unitario=Decimal(preco_unitario),
            )
        )

    @property
    def valor_total(self) -> Decimal:
        """Soma de todos os subtotais do pedido."""
        return sum((item.subtotal for item in self.itens), Decimal("0"))

    def resumo(self) -> str:
        """Texto legível do pedido, usado só para exibição no terminal."""
        linhas = [f"Pedido {self.numero} - Cliente: {self.cliente}"]
        for item in self.itens:
            linhas.append(
                f"  {item.quantidade}x {item.descricao:<28} "
                f"R$ {item.preco_unitario:>8} = R$ {item.subtotal:>9}"
            )
        linhas.append(f"  {'TOTAL':<46}R$ {self.valor_total:>9}")
        return "\n".join(linhas)
