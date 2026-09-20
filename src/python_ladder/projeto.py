from __future__ import annotations
from pathlib import Path
from typing import Iterable, Union
from .bloco import BlocoFC
from .rede import Rede
from .tags import TabelaTags

class ProjetoLadder:
    def __init__(self, nome_bloco: str = "Block_1", pasta: Union[str, Path] = "."):
        self.nome_bloco = nome_bloco
        self.pasta = Path(pasta)
        self.redes: list[Rede] = []

    def adicionar_rede(self, elementos: Iterable[Union[Elemento, list]]) -> "ProjetoLadder":
        """Aceita objetos Elemento ou listas no formato antigo. Devolve self (encadeável)."""
        self.redes.append(Rede(elementos))
        return self

    def salvar(self) -> tuple[Path, Path]:
        if not self.redes:
            raise ValueError("Adicione pelo menos uma rede antes de salvar.")
        self.pasta.mkdir(parents=True, exist_ok=True)
        bloco = BlocoFC(self.nome_bloco, self.redes).salvar(self.pasta)
        todos = [el for rede in self.redes for el in rede.elementos]
        tags = TabelaTags(todos).salvar(self.pasta)
        return bloco, tags


def criar_network(lista, nome_bloco: str = "Block_1", pasta: Union[str, Path] = "."):
    """Compatível com a função antiga: `lista` é uma lista de networks (formato antigo)."""
    projeto = ProjetoLadder(nome_bloco, pasta)
    for elementos in lista:
        projeto.adicionar_rede(elementos)
    return projeto.salvar()