# Roteiro de demonstração no depurador (VS Code / PyCharm)

Objetivo: provar o padrão Strategy em tempo de execução, mostrando
**variáveis, polimorfismo, pilha de chamadas e instâncias na memória** —
exatamente os quatro itens que o enunciado pede.

Tempo estimado: 6 a 8 minutos.

---

## Antes de começar (faça isso ANTES de subir para apresentar)

1. Abra a pasta `gateway_pagamento/` no VS Code.
2. Rode uma vez no terminal para garantir que está tudo certo:
   ```
   python main.py
   ```
   Escolha a opção `0`. Se os comprovantes aparecerem, está pronto.
3. No VS Code, vá em **Run and Debug** → **create a launch.json file** →
   **Python File**. Ou simplesmente use `F5` com o `main.py` aberto.
4. Aumente a fonte do editor (`Ctrl` + `+`) até caber na projeção.
5. Deixe aberto o painel **VARIABLES** e o painel **CALL STACK** à esquerda.

> **Dica:** rode o programa com a opção `1` do menu. Ela chama
> `demonstrar_troca_em_tempo_de_execucao()`, que é a função desenhada
> especialmente para a demonstração no depurador.

---

## Os 4 breakpoints

| # | Arquivo | Linha | O que provar ali |
|---|---------|-------|------------------|
| 1 | `main.py` | **83** — `processador.definir_estrategia(estrategia)` | O Cliente escolhendo a estratégia |
| 2 | `contexto/processador_pagamento.py` | **88** — `resultado = self._estrategia.processar(pedido)` | **O coração do padrão** |
| 3 | `estrategias/pagamento_pix.py` | **44** — `def processar(...)` | A estratégia concreta sendo executada |
| 4 | `estrategias/pagamento_cartao_credito.py` | **65** — `def processar(...)` | Outra estratégia, mesma chamada |

Para colocar um breakpoint: clique na margem esquerda, ao lado do número da
linha. Aparece uma bolinha vermelha.

---

## Passo a passo do que falar

### Passo 1 — Pare no breakpoint 1 (`main.py`, linha 83)

**O que mostrar no painel VARIABLES:**
- Abra a variável `estrategias`. É uma lista com 5 objetos de classes
  **diferentes**: `PagamentoPix`, dois `PagamentoCartaoCredito`,
  `PagamentoBoleto`, `PagamentoDinheiro`.
- Abra a variável `processador`. Mostre que `_estrategia` ainda está `None`.

**Fala sugerida:**
> "O Cliente — nosso menu de PDV — montou uma lista de estratégias concretas.
> O processador foi criado uma única vez e ainda não tem forma de pagamento
> nenhuma. É o Cliente quem decide, não o Contexto."

### Passo 2 — Dê **Step Over** (`F10`) uma vez

**O que mostrar:**
- `processador._estrategia` deixou de ser `None` e agora é um
  `PagamentoPix`. No VS Code aparece algo como
  `_estrategia: <Estratégia: Pix>`.

**Fala sugerida:**
> "A estratégia foi injetada no Contexto em tempo de execução, pelo setter
> `definir_estrategia`. O objeto `processador` continua sendo o mesmo — repare
> no endereço de memória, ele não mudou."

> **Para mostrar instâncias na memória:** no painel **DEBUG CONSOLE**, digite
> `id(processador)` e dê Enter. Anote o número. Mais adiante, no laço, digite
> de novo — é o **mesmo número**. Depois digite `id(processador._estrategia)`
> antes e depois da troca — esse **muda**. Essa é a prova visual mais forte da
> apresentação inteira.

### Passo 3 — Vá até o breakpoint 2 (`F5` para continuar)

Você para em `contexto/processador_pagamento.py`, linha 88.

**O que mostrar:**
- No painel VARIABLES, abra `self`. Mostre `_estrategia`.
- Peça atenção para a linha: `resultado = self._estrategia.processar(pedido)`.

**Fala sugerida:**
> "Esta é a única linha do Contexto que executa a cobrança. Ela não sabe se
> vai cobrar Pix, cartão ou boleto. Procurem um `if` neste arquivo — não
> existe nenhum. O Contexto conhece apenas a interface."

### Passo 4 — Dê **Step Into** (`F11`)

Você cai dentro de `estrategias/pagamento_pix.py`, no método `processar`.

**O que mostrar no painel CALL STACK:**
```
processar            pagamento_pix.py
executar_pagamento   processador_pagamento.py
demonstrar_troca...  main.py
main                 main.py
```

**Fala sugerida:**
> "A pilha de chamadas mostra o caminho: o Cliente chamou o Contexto, e o
> Contexto delegou para a estratégia concreta. Três camadas, cada uma com
> uma responsabilidade só."

Continue com **Step Over** (`F10`) dentro do `processar` para mostrar:
- a validação do limite do Pix sendo avaliada;
- a variável `taxa` sendo calculada como 0,99% do valor;
- o objeto `ResultadoPagamento` sendo montado.

### Passo 5 — O golpe de misericórdia: a MESMA linha, outro arquivo

Dê `F5` até voltar ao breakpoint 2 (segunda volta do laço).
A estratégia agora é `PagamentoCartaoCredito`.

Dê **Step Into** (`F11`) na mesma linha 88 de antes.

**O que acontece:** o depurador abre `pagamento_cartao_credito.py`, e não
mais o arquivo do Pix.

**Fala sugerida — esta é a frase mais importante da apresentação:**
> "Prestem atenção: é exatamente a mesma linha de código do Contexto, a linha
> 88, que executamos nas duas vezes. Na primeira ela nos levou para o arquivo
> do Pix. Agora ela nos levou para o arquivo do cartão. O Contexto não mudou.
> Isso é polimorfismo acontecendo em tempo de execução, e é o que o padrão
> Strategy entrega."

### Passo 6 — Mostre que os algoritmos são realmente diferentes

Ainda dentro de `pagamento_cartao_credito.py`, dê `F11` em `_aplicar_juros`
e mostre o cálculo dos juros de parcelamento — uma lógica que **não existe**
em nenhuma das outras estratégias.

**Fala sugerida:**
> "O cartão tem juros de parcelamento, o dinheiro calcula troco, o boleto gera
> linha digitável. Três algoritmos totalmente diferentes, chamados pela mesma
> linha. Cada um isolado no seu arquivo."

---

## Se o tempo apertar (versão de 3 minutos)

Use só os breakpoints **2** e **4**:

1. Pare na linha 88 do Contexto.
2. `F11` → cai no Pix.
3. `F5` até voltar na linha 88.
4. `F11` → cai no cartão.
5. Fale a frase do Passo 5.

Só isso já prova o padrão.

---

## Teclas de atalho (cole num papel e leve)

| Ação | VS Code | PyCharm |
|------|---------|---------|
| Iniciar / continuar | `F5` | `Shift`+`F9` / `F9` |
| Step Over (próxima linha) | `F10` | `F8` |
| Step Into (entrar na função) | `F11` | `F7` |
| Step Out (sair da função) | `Shift`+`F11` | `Shift`+`F8` |
| Parar | `Shift`+`F5` | `Ctrl`+`F2` |

---

## Erros comuns na hora H

| Problema | Solução |
|----------|---------|
| `ModuleNotFoundError: No module named 'modelos'` | Você rodou de dentro de uma subpasta. Abra o terminal na raiz do projeto (`gateway_pagamento/`) e rode `python main.py`. |
| O `F11` pula a função e não entra | Você estava numa linha que não tem chamada de função. Confirme que parou exatamente na linha 88. |
| O depurador entra em arquivos do Python | Em `launch.json`, confirme que `"justMyCode": true` está ativo. |
| O programa termina antes do breakpoint | Você escolheu a opção errada no menu. Digite `1`. |
