# Roteiro da apresentação — Padrão Strategy

> Ajuste os tempos ao limite que o professor deu. O roteiro abaixo está
> calibrado para **15 minutos de apresentação + 5 minutos de arguição**.
> Se o grupo for menor ou maior, junte ou divida os blocos — a ordem é o
> que importa.

---

## Divisão sugerida por integrante

| Bloco | Tempo | Quem fala | Conteúdo |
|-------|-------|-----------|----------|
| 1. O problema | 3 min | Integrante A | Cenário real + código ruim |
| 2. O padrão | 3 min | Integrante B | Definição, estrutura, papéis |
| 3. O código | 4 min | Integrante C | Navegação pela IDE |
| 4. Ao vivo + debug | 4 min | Integrante D | Execução e depurador |
| 5. Prós, contras e fecho | 1 min | Integrante A | Quando NÃO usar |
| 6. Arguição | 5 min | Todos | Perguntas |

> **Regra de ouro:** quem fala do bloco 4 precisa ter ensaiado o depurador
> pelo menos 3 vezes. É o bloco que mais trava ao vivo.

---

## Bloco 1 — O problema (3 min)

**Abra com o cenário, não com a teoria.**

> "Imaginem o caixa de um restaurante. Hoje ele aceita Pix, cartão, boleto e
> dinheiro. Cada forma cobra uma taxa diferente, tem um prazo de recebimento
> diferente e regras de recusa diferentes. O Pix tem limite por transação, o
> boleto tem valor mínimo, o cartão tem limite de parcelas e o dinheiro
> precisa calcular troco."

**Agora mostre o código ruim.** Abra `comparativo_sem_o_padrao.py` na IDE e
role a cadeia de `if/elif`.

Pontos a destacar enquanto rola a tela:
1. A cadeia cresce a cada forma de pagamento nova.
2. A assinatura do método tem `parcelas`, `bandeira`, `valor_recebido` —
   parâmetros que só servem para um caso cada.
3. Para aceitar Vale-Refeição amanhã, é obrigatório editar esta classe.
4. Em equipe, todo mundo mexe no mesmo arquivo → conflito de merge.

Rode o arquivo (`python comparativo_sem_o_padrao.py`) e mostre que ele
**funciona**. Isso é importante:

> "O problema não é que o código não funciona. Ele funciona. O problema é
> manter isso vivo por dois anos."

---

## Bloco 2 — O padrão (3 min)

**Definição (decore esta frase):**

> "Strategy é um padrão comportamental que define uma família de algoritmos,
> coloca cada um em uma classe separada e torna esses objetos
> intercambiáveis."

**Os quatro papéis** — desenhe no quadro ou mostre um slide simples:

| Papel | No nosso projeto | Arquivo |
|-------|------------------|---------|
| **Estratégia** (interface) | `EstrategiaPagamento` | `estrategias/estrategia_pagamento.py` |
| **Estratégias Concretas** | `PagamentoPix`, `PagamentoCartaoCredito`, `PagamentoBoleto`, `PagamentoDinheiro` | `estrategias/*.py` |
| **Contexto** | `ProcessadorDePagamento` | `contexto/processador_pagamento.py` |
| **Cliente** | o menu do PDV | `main.py` |

**A analogia** (ajuda muito a turma a entender):

> "É como ir ao aeroporto. Ônibus, táxi ou bicicleta são estratégias
> diferentes. Você continua sendo a mesma pessoa indo para o mesmo lugar —
> o que você troca é o algoritmo de transporte."

**Classificação:** padrão **comportamental**, do catálogo GoF.
Baseado em **composição**, não em herança.

---

## Bloco 3 — Navegação pelo código (4 min)

> Esta é a parte que o enunciado cobra explicitamente: *"abrir a IDE e
> navegar pela estrutura das classes/interfaces do padrão"*.

**Ordem de abertura dos arquivos — siga exatamente esta:**

**1) `estrategias/estrategia_pagamento.py` — a interface**

Mostre `ABC` e `@abstractmethod`.

> "Em Python não existe a palavra `interface` como em Java. O equivalente é
> uma classe base abstrata. O efeito é o mesmo: quem herdar daqui é obrigado
> a implementar `calcular_taxa` e `processar`."

**Prova ao vivo (opcional, 20 segundos, mas impressiona):** no terminal,
abra o Python e tente instanciar a classe abstrata:
```python
from estrategias.estrategia_pagamento import EstrategiaPagamento
EstrategiaPagamento()
```
Ele levanta `TypeError: Can't instantiate abstract class`. É a prova de que
o contrato é real, e não só uma convenção.

**2) `estrategias/pagamento_pix.py` e `pagamento_cartao_credito.py`**

Abra os dois lado a lado (no VS Code: clique direito na aba → *Split Right*).

> "Repare: os dois têm o método `calcular_taxa` com a mesma assinatura. Mas o
> Pix é só percentual, e o cartão é percentual mais taxa fixa, e ainda tem
> juros de parcelamento. Mesma interface, algoritmos completamente diferentes."

Mostre também que cada estratégia tem **dados próprios** no construtor:
chave Pix, bandeira do cartão, CNPJ do beneficiário, valor recebido no caixa.

**3) `contexto/processador_pagamento.py` — o Contexto**

Este é o momento mais forte do bloco. Use `Ctrl`+`F` e procure por `if forma`.

> "Zero resultados. O Contexto não tem um único `if` decidindo forma de
> pagamento. Ele também não importa nenhuma classe concreta — só a interface.
> Olhem os imports no topo."

Mostre o `definir_estrategia` (o setter) e a linha 88 do `executar_pagamento`.

**4) `main.py` — o Cliente**

> "É aqui, e só aqui, que alguém decide qual forma de pagamento usar. O
> Cliente conhece as diferenças entre as estratégias; o Contexto não."

---

## Bloco 4 — Execução ao vivo + depurador (4 min)

**Primeiro rode normal**, sem depurador:
```
python main.py
```
Escolha a opção `2` (comparação de taxas). É rápida e visual:

```
FORMA DE PAGAMENTO                           TAXA   FICA PARA A CASA
Pix                                       R$ 2.72          R$ 272.18
Cartão de Crédito Visa (à vista)          R$ 9.16          R$ 265.74
Boleto Bancário                           R$ 3.49          R$ 271.41
Dinheiro                                  R$ 0.00          R$ 274.90
```

> "Mesmo pedido, quatro algoritmos de taxa diferentes, uma única chamada de
> método. O Contexto perguntou `calcular_taxa` quatro vezes sem saber para
> quem estava perguntando."

Depois rode a opção `3` para mostrar as regras de recusa de cada estratégia.

**Agora o depurador.** Siga o `docs/ROTEIRO_DEBUG.md`, que tem os
breakpoints, as teclas e as falas. Se o tempo apertar, use a versão de
3 minutos descrita lá no fim.

---

## Bloco 5 — Prós, contras e fecho (1 min)

**Vantagens (mostre que vocês entenderam o porquê, não só o como):**
- Trocar o algoritmo em tempo de execução.
- Princípio Aberto/Fechado: forma nova = arquivo novo, Contexto intocado.
- Substitui herança por composição.
- Cada algoritmo testável isoladamente.

**Desvantagens (falar isso vale ponto — mostra senso crítico):**
- Se forem só dois algoritmos que nunca mudam, o padrão só adiciona classes
  à toa.
- O Cliente precisa conhecer as diferenças entre as estratégias para escolher
  a certa.
- Em Python, funções são objetos de primeira classe: para casos simples dá
  para passar uma função em vez de uma classe inteira, sem o peso do padrão.

**Frase de fecho:**
> "Trocamos uma classe que sabia tudo por cinco classes que sabem uma coisa
> cada. O código ficou maior em número de arquivos e menor em complexidade
> por arquivo. Esse é o trade-off do Strategy."

---

## Bloco 6 — Arguição: perguntas prováveis

**"Por que não usar só um if/elif?"**
> Funciona para dois ou três casos. O problema aparece na manutenção: cada
> forma nova obriga a editar uma classe que já está em produção e já foi
> testada. Com o Strategy, criamos um arquivo novo e não tocamos no que
> funciona.

**"Qual a diferença entre Strategy e State?"**
> A estrutura é quase idêntica, mas a intenção é outra. No Strategy as
> estratégias são independentes e não sabem uma da outra — quem troca é o
> Cliente. No State, os estados podem trocar o próprio estado do Contexto
> sozinhos, e geralmente conhecem uns aos outros.

**"E a diferença para o Template Method?"**
> Template Method usa herança e funciona em tempo de compilação — a variação
> fica em subclasses. Strategy usa composição e funciona em tempo de
> execução — dá para trocar o comportamento com o programa rodando.

**"Onde exatamente está o polimorfismo?"**
> Na linha 88 de `processador_pagamento.py`: `self._estrategia.processar(pedido)`.
> A mesma linha executa código de arquivos diferentes dependendo de qual
> objeto está na variável. Foi isso que mostramos no depurador.

**"Como vocês adicionariam Vale-Refeição?"**
> Criaríamos `estrategias/pagamento_vale_refeicao.py` herdando de
> `EstrategiaPagamento`, implementaríamos os dois métodos e acrescentaríamos
> uma linha no `main.py`. Nenhum arquivo existente do Contexto ou das outras
> estratégias seria alterado.

**"Python tem interface de verdade?"**
> Não tem a palavra-chave. Usamos `ABC` com `@abstractmethod`, que impede a
> instanciação de quem não implementar o contrato — podemos demonstrar isso
> no terminal agora, se quiser.

**"Por que `Decimal` e não `float`?"**
> Porque `float` tem erro de representação binária: `0.1 + 0.2` não dá `0.3`.
> Em sistema que lida com dinheiro isso gera divergência de centavos no
> fechamento de caixa.

---

## Checklist final — confira na véspera

- [ ] O projeto roda com `python main.py` sem erro.
- [ ] As opções 1, 2 e 3 do menu funcionam.
- [ ] `comparativo_sem_o_padrao.py` roda.
- [ ] Os 4 breakpoints estão marcados e salvos no VS Code.
- [ ] A fonte do editor está grande o suficiente para a projeção.
- [ ] Cada integrante ensaiou o bloco dele pelo menos uma vez em voz alta.
- [ ] Quem apresenta o depurador ensaiou pelo menos 3 vezes.
- [ ] Vocês prepararam uma pergunta técnica para fazer a cada outro grupo
      (o enunciado dá ponto extra individual por isso).
