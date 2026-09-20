from __future__ import annotations
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import Optional
from .constantes import PARTS_TIA
@dataclass
class Elemento:
    """Contato ou bobina ligado entre dois nós do diagrama.

    tipo    : 'contato' | 'bobina'
    subtipo : contato -> '1' normal, 'f' negado, 'p' borda de subida, 'n' borda de descida
              bobina  -> '1' / 'c' normal, 'r' reset, 's' set
    """

    nome: str
    tipo: str
    subtipo: str
    no_in: int
    no_out: int
    ocorrencia: int = 0  # 0 na 1ª vez que o mesmo (nome, tipo, subtipo) aparece, 1 na 2ª...

    # Preenchidos pela Rede
    uid_nome: Optional[int] = field(default=None, repr=False)
    uid_memoria: Optional[int] = field(default=None, repr=False)
    uid_part: Optional[int] = field(default=None, repr=False)

    def __post_init__(self):
        self.subtipo = str(self.subtipo)
        if self.tipo not in PARTS_TIA:
            raise ValueError(f"Tipo '{self.tipo}' inválido. Use: {list(PARTS_TIA)}")
        if self.subtipo not in PARTS_TIA[self.tipo]:
            raise ValueError(
                f"Subtipo '{self.subtipo}' inválido para '{self.tipo}'. "
                f"Use: {list(PARTS_TIA[self.tipo])}"
            )

    @classmethod
    def de_lista(cls, item) -> "Elemento":
        """Aceita o formato antigo: [(nome, tipo, subtipo, 0), no_in, no_out]."""
        (nome, tipo, subtipo, *_), no_in, no_out = item
        return cls(nome, tipo, subtipo, no_in, no_out)

    # ---- regras do tipo de elemento -------------------------------------
    @property
    def tem_borda(self) -> bool:
        """Contatos P/N precisam de uma memória auxiliar de borda."""
        return self.tipo == "contato" and self.subtipo in ("p", "n")

    @property
    def nome_memoria(self) -> str:
        return f"{self.nome}_Mem"

    @property
    def porta_entrada(self) -> str:
        return "pre" if self.tem_borda else "in"

    @property
    def nome_part(self) -> str:
        return PARTS_TIA[self.tipo][self.subtipo]

    @property
    def negado(self) -> bool:
        return self.tipo == "contato" and self.subtipo == "f"

    # ---- XML -------------------------------------------------------------
    @staticmethod
    def _access(uid: int, nome: str) -> ET.Element:
        acesso = ET.Element("Access", Scope="GlobalVariable", UId=str(uid))
        simbolo = ET.SubElement(acesso, "Symbol")
        ET.SubElement(simbolo, "Component", Name=nome)
        return acesso

    def xml_acessos(self) -> list[ET.Element]:
        """<Access> do nome (e da memória de borda, se houver)."""
        acessos = [self._access(self.uid_nome, self.nome)]
        if self.tem_borda:
            acessos.append(self._access(self.uid_memoria, self.nome_memoria))
        return acessos

    def xml_part(self) -> ET.Element:
        part = ET.Element("Part", Name=self.nome_part, UId=str(self.uid_part))
        if self.negado:
            ET.SubElement(part, "Negated", Name="operand")
        return part


@dataclass
class Cardinalidade:
    """Part 'O' que junta `quantidade` ramos que terminam no mesmo nó."""

    no: int
    quantidade: int
    uid_part: Optional[int] = None

    porta_entrada = "in"  # mesma interface do Elemento (duck typing)

    def xml_part(self) -> ET.Element:
        part = ET.Element("Part", Name="O", UId=str(self.uid_part))
        valor = ET.SubElement(part, "TemplateValue", Name="Card", Type="Cardinality")
        valor.text = str(self.quantidade)
        return part