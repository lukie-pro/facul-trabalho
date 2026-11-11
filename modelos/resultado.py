"""
Modelo de domínio: o resultado devolvido por qualquer forma de pagamento.

Ponto importante para a apresentação: TODAS as estratégias concretas
devolvem este mesmo tipo. É isso que as torna intercambiáveis — o Contexto
recebe sempre um ResultadoPagamento, não importa qual estratégia rodou.
"""

from dataclasses import dataclass, field
from decimal import Decimal


@dataclass
class ResultadoPagamento:
    """Retorno padronizado de qualquer estratégia de pagamento."""

    sucesso: bool
    forma_pagamento: str
    valor_bruto: Decimal
    taxa: Decimal
    valor_liquido: Decimal
    prazo_recebimento: str
    identificador: str
    mensagem: str
    # Campos que só algumas formas de pagamento usam (troco, parcelas,
    # linha digitável...). Fica num dicionário para não poluir a interface.
    detalhes: dict = field(default_factory=dict)

    def __str__(self) -> str:
        """Formata o comprovante que aparece no terminal."""
        if not self.sucesso:
            return f"[RECUSADO] {self.forma_pagamento}: {self.mensagem}"

        linhas = [
            f"[APROVADO] {self.forma_pagamento}",
            f"  Identificador .... {self.identificador}",
            f"  Valor bruto ...... R$ {self.valor_bruto}",
            f"  Taxa ............. R$ {self.taxa}",
            f"  Valor líquido .... R$ {self.valor_liquido}",
            f"  Recebimento ...... {self.prazo_recebimento}",
        ]
        for chave, valor in self.detalhes.items():
            rotulo = chave.replace("_", " ").capitalize()
            linhas.append(f"  {rotulo} {'.' * max(1, 17 - len(rotulo))} {valor}")
        linhas.append(f"  {self.mensagem}")
        return "\n".join(linhas)
