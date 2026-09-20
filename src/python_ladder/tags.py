from __future__ import annotations
from pathlib import Path
from typing import Iterable, Union
from xml.sax.saxutils import escape
from ._xml_comum import _cabecalho_documento
from .elementos import Elemento

def _enderecos_memoria():
    byte = bit = 0
    while True:
        yield f"%M{byte}.{bit}"
        bit += 1
        if bit > 7:
            bit, byte = 0, byte + 1


class TabelaTags:
    NOME_ARQUIVO = "Default tag table.xml"

    def __init__(self, elementos: Iterable[Elemento], nome: str = "Default tag table python"):
        self.nome = nome
        self.tags = self._coletar_nomes(elementos)

    @staticmethod
    def _coletar_nomes(elementos: Iterable[Elemento]) -> list[str]:
        nomes: dict[str, None] = {}  # dict como "conjunto ordenado"
        for el in elementos:
            nomes.setdefault(el.nome)
            if el.tem_borda:
                nomes.setdefault(el.nome_memoria)
        return list(nomes)

    @staticmethod
    def _xml_tag(indice: int, nome: str, endereco: str) -> str:
        id_tag, id_comentario, id_item = (f"{1 + 3 * indice + k:X}" for k in range(3))
        return f"""
      <SW.Tags.PlcTag ID="{id_tag}" CompositionName="Tags">
        <AttributeList>
          <DataTypeName>Bool</DataTypeName>
          <LogicalAddress>{endereco}</LogicalAddress>
          <Name>{escape(nome)}</Name>
        </AttributeList>
        <ObjectList>
          <MultilingualText ID="{id_comentario}" CompositionName="Comment">
            <ObjectList>
              <MultilingualTextItem ID="{id_item}" CompositionName="Items">
                <AttributeList>
                  <Culture>en-US</Culture>
                  <Text />
                </AttributeList>
              </MultilingualTextItem>
            </ObjectList>
          </MultilingualText>
        </ObjectList>
      </SW.Tags.PlcTag>"""

    def xml(self) -> str:
        enderecos = _enderecos_memoria()
        corpo = "".join(
            self._xml_tag(i, nome, next(enderecos)) for i, nome in enumerate(self.tags)
        )
        return (
            _cabecalho_documento()
            + f'  <SW.Tags.PlcTagTable ID="0">\n'
            f'    <AttributeList>\n      <Name>{escape(self.nome)}</Name>\n    </AttributeList>\n'
            f'    <ObjectList>{corpo}\n    </ObjectList>\n'
            f'  </SW.Tags.PlcTagTable>\n</Document>'
        )

    def salvar(self, pasta: Union[str, Path] = ".") -> Path:
        caminho = Path(pasta) / self.NOME_ARQUIVO
        caminho.write_text(self.xml(), encoding="utf-8")
        return caminho

    