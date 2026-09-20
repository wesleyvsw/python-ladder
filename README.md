# ladder-tia

Gera blocos Ladder (LAD) e tabelas de tags em XML para importar no TIA Portal.
## Instalação

```
pip install git+https://github.com/wesleyvsw/python-ladder.git
```

## Exemplo

```python
from python_ladder import ProjetoLadder, Elemento

projeto = ProjetoLadder("MeuBloco", pasta="saida")
projeto.adicionar_rede([
    Elemento("btn_liga",    "contato", "1", no_in=0, no_out=1),
    Elemento("btn_desliga", "contato", "f", no_in=1, no_out=2),
    Elemento("motor",       "bobina",  "1", no_in=2, no_out=3),
])
projeto.salvar()
```

## Como descrever o circuito

Cada elemento liga um nó de entrada (`no_in`) a um nó de saída (`no_out`).

- O nó **0** é o barramento energizado.
- Elementos em série: a saída de um é a entrada do próximo.
- Elementos em paralelo: terminam no mesmo nó de saída.

## Tipos e subtipos

| Tipo | Subtipo | Elemento |
|---|---|---|
| contato | `1` | normal |
| contato | `f` | negado |
| contato | `p` | borda de subida |
| contato | `n` | borda de descida |
| bobina | `1` ou `c` | normal |
| bobina | `r` | reset |
| bobina | `s` | set |
