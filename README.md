# Gateway de Pagamento — Padrão de Projeto Strategy

Mini-projeto funcional que demonstra o padrão comportamental **Strategy**
(GoF) num cenário real: o gateway de pagamento de um restaurante que aceita
Pix, cartão de crédito, boleto bancário e dinheiro em espécie.

Cada forma de pagamento tem sua própria fórmula de taxa, seu próprio prazo
de recebimento e suas próprias regras de recusa — exatamente o tipo de
variação que o Strategy foi feito para organizar.

---

## Como rodar

Requisito: **Python 3.10 ou superior** (o projeto usa a sintaxe `X | None`).
Nenhuma biblioteca externa é necessária.

```bash
cd gateway_pagamento
python main.py
```

O menu oferece três demonstrações:

| Opção | O que faz |
|-------|-----------|
| `1` | Roda o mesmo pedido nas 4 formas, trocando a estratégia em tempo de execução |
| `2` | Compara quanto cada forma de pagamento custa ao restaurante |
| `3` | Mostra as regras de recusa próprias de cada estratégia |
| `0` | Roda as três e encerra |

Para ver a versão **sem** o padrão (usada na comparação da apresentação):

```bash
python comparativo_sem_o_padrao.py
```

---

## Estrutura do projeto

```
gateway_pagamento/
├── main.py                          ← CLIENTE (escolhe a estratégia)
│
├── contexto/
│   └── processador_pagamento.py     ← CONTEXTO (delega o trabalho)
│
├── estrategias/
│   ├── estrategia_pagamento.py      ← ESTRATÉGIA (interface / ABC)
│   ├── pagamento_pix.py             ← Estratégia Concreta 1
│   ├── pagamento_cartao_credito.py  ← Estratégia Concreta 2
│   ├── pagamento_boleto.py          ← Estratégia Concreta 3
│   └── pagamento_dinheiro.py        ← Estratégia Concreta 4
│
├── modelos/
│   ├── pedido.py                    ← dado de domínio (não é do padrão)
│   └── resultado.py                 ← retorno padronizado das estratégias
│
├── comparativo_sem_o_padrao.py      ← apoio: o mesmo sistema com if/elif
│
└── docs/
    ├── ROTEIRO_APRESENTACAO.md      ← o que falar, em que ordem, por quanto tempo
    └── ROTEIRO_DEBUG.md             ← breakpoints e passo a passo no depurador
```

---

## Os papéis do padrão neste projeto

| Papel (Refactoring Guru) | Classe | Responsabilidade |
|--------------------------|--------|------------------|
| **Estratégia** | `EstrategiaPagamento` | Declara `calcular_taxa` e `processar`, que toda forma de pagamento precisa implementar |
| **Estratégias Concretas** | `PagamentoPix`, `PagamentoCartaoCredito`, `PagamentoBoleto`, `PagamentoDinheiro` | Implementam variações diferentes do mesmo algoritmo |
| **Contexto** | `ProcessadorDePagamento` | Guarda a estratégia ativa, registra log e histórico, e **delega** a cobrança |
| **Cliente** | `main.py` | Cria a estratégia concreta e entrega ao Contexto |

---

## Regras de negócio de cada estratégia

| Forma | Taxa | Recebimento | Regra de recusa |
|-------|------|-------------|-----------------|
| Pix | 0,99% do valor | Imediato | Acima de R$ 5.000,00 por transação |
| Cartão de crédito | 3,19% + R$ 0,39 | 30 dias | Fora da faixa de 1 a 12 parcelas |
| Boleto | R$ 3,49 fixo | Até 3 dias úteis | Abaixo de R$ 20,00 |
| Dinheiro | Zero | Imediato | Valor recebido menor que a conta |

O cartão ainda aplica 1,99% ao mês de juros quando parcelado — um algoritmo
que nenhuma outra estratégia tem.

---

## O ponto central do padrão

No arquivo `contexto/processador_pagamento.py`, **linha 88**:

```python
resultado = self._estrategia.processar(pedido)
```

Essa única linha executa quatro algoritmos completamente diferentes,
dependendo apenas de qual objeto está guardado em `self._estrategia`.

O Contexto:
- não tem nenhum `if` decidindo forma de pagamento;
- não importa nenhuma classe concreta, só a interface;
- não muda uma linha quando uma forma de pagamento nova é adicionada.

É isso que o depurador prova na demonstração ao vivo.

---

## Decisões técnicas que valem explicar na arguição

- **`Decimal` em vez de `float`** para valores monetários: `float` tem erro de
  representação binária (`0.1 + 0.2 != 0.3`), o que geraria divergência de
  centavos no fechamento de caixa.
- **`ROUND_HALF_UP`** no arredondamento: é a regra comercial brasileira. O
  padrão do Python é `ROUND_HALF_EVEN`, que arredondaria R$ 0,125 para R$ 0,12.
- **`ABC` + `@abstractmethod`**: é o equivalente Python de uma interface.
  Tentar instanciar `EstrategiaPagamento()` levanta `TypeError`.
- **Dados próprios no construtor de cada estratégia** (chave Pix, bandeira,
  CNPJ, valor em caixa): mantém a interface limpa e evita o problema de
  parâmetros que só servem para um caso, visível em `comparativo_sem_o_padrao.py`.

---

## Referência

Padrão Strategy — Refactoring Guru (pt-br):
https://refactoring.guru/pt-br/design-patterns/strategy
