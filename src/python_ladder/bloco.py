from __future__ import annotations
import itertools
from pathlib import Path
from typing import Iterable, Union
from xml.sax.saxutils import escape
from ._xml_comum import _cabecalho_documento
from .rede import Rede

class _GeradorIds:
    """IDs hexadecimais sequenciais (0, 1, ..., 9, A, B...) usados nos atributos ID=""."""

    def __init__(self):
        self._contador = itertools.count()

    def __call__(self) -> str:
        return f"{next(self._contador):X}"


def _texto_multilingue(composicao: str, novo_id: _GeradorIds, recuo: int) -> str:
    id_texto, id_item = novo_id(), novo_id()
    linhas = [
        f'<MultilingualText ID="{id_texto}" CompositionName="{composicao}">',
        '  <ObjectList>',
        f'    <MultilingualTextItem ID="{id_item}" CompositionName="Items">',
        '      <AttributeList>',
        '        <Culture>en-US</Culture>',
        '        <Text />',
        '      </AttributeList>',
        '    </MultilingualTextItem>',
        '  </ObjectList>',
        '</MultilingualText>',
    ]
    return "".join(" " * recuo + linha + "\n" for linha in linhas)


class BlocoFC:
    """Um bloco FC em LAD com uma ou mais redes (networks)."""

    def __init__(self, nome: str, redes: list[Rede], variaveis_temp: Iterable[str] = ("cont2",)):
        # 'cont2' vem do bloco de exemplo original; passe variaveis_temp=() para não declarar nada.
        self.nome = nome
        self.redes = list(redes)
        self.variaveis_temp = tuple(variaveis_temp)

    def _secao_temp(self) -> str:
        if not self.variaveis_temp:
            return '  <Section Name="Temp" />\n'
        membros = "".join(
            f'    <Member Name="{escape(v)}" Datatype="Bool" />\n' for v in self.variaveis_temp
        )
        return f'  <Section Name="Temp">\n{membros}  </Section>\n'

    def _abrir_fc(self, novo_id: _GeradorIds) -> str:
        id_fc = novo_id()
        comentario = _texto_multilingue("Comment", novo_id, recuo=6)
        return (
            f'  <SW.Blocks.FC ID="{id_fc}">\n'
            '    <AttributeList>\n'
            '      <Interface><Sections xmlns="http://www.siemens.com/automation/Openness/SW/Interface/v5">\n'
            '  <Section Name="Input" />\n'
            '  <Section Name="Output" />\n'
            '  <Section Name="InOut" />\n'
            f'{self._secao_temp()}'
            '  <Section Name="Constant" />\n'
            '  <Section Name="Return">\n'
            '    <Member Name="Ret_Val" Datatype="Void" />\n'
            '  </Section>\n'
            '</Sections></Interface>\n'
            '      <MemoryLayout>Optimized</MemoryLayout>\n'
            f'      <Name>{escape(self.nome)}</Name>\n'
            '      <Number>1</Number>\n'
            '      <ProgrammingLanguage>LAD</ProgrammingLanguage>\n'
            '      <SetENOAutomatically>false</SetENOAutomatically>\n'
            '    </AttributeList>\n'
            '    <ObjectList>\n'
            f'{comentario}'
        )

    @staticmethod
    def _compile_unit(rede: Rede, novo_id: _GeradorIds) -> str:
        id_unidade = novo_id()
        comentario = _texto_multilingue("Comment", novo_id, recuo=10)
        titulo = _texto_multilingue("Title", novo_id, recuo=10)
        return (
            f'      <SW.Blocks.CompileUnit ID="{id_unidade}" CompositionName="CompileUnits">\n'
            '        <AttributeList>\n'
            '          <NetworkSource><FlgNet xmlns="http://www.siemens.com/automation/Openness/SW/NetworkSource/FlgNet/v4">\n'
            f'{rede.xml()}\n'
            '</FlgNet></NetworkSource>\n'
            '          <ProgrammingLanguage>LAD</ProgrammingLanguage>\n'
            '        </AttributeList>\n'
            '        <ObjectList>\n'
            f'{comentario}{titulo}'
            '        </ObjectList>\n'
            '      </SW.Blocks.CompileUnit>\n'
        )

    @staticmethod
    def _fechar_fc(novo_id: _GeradorIds) -> str:
        titulo = _texto_multilingue("Title", novo_id, recuo=6)
        return (
            f'{titulo}'
            '    </ObjectList>\n'
            '  </SW.Blocks.FC>\n'
            '</Document>'
        )

    def xml(self) -> str:
        novo_id = _GeradorIds()
        partes = [_cabecalho_documento(), self._abrir_fc(novo_id)]
        partes += [self._compile_unit(rede, novo_id) for rede in self.redes]
        partes.append(self._fechar_fc(novo_id))
        return "".join(partes)

    def salvar(self, pasta: Union[str, Path] = ".") -> Path:
        caminho = Path(pasta) / f"{self.nome}.xml"
        caminho.write_text(self.xml(), encoding="utf-8")
        return caminho