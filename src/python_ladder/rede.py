from __future__ import annotations
import heapq, itertools
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict, deque
from dataclasses import replace
from typing import Iterable, Union
from .constantes import NO_BARRAMENTO
from .elementos import Elemento, Cardinalidade

class Rede:
    UID_INICIAL = 21

    def __init__(self, elementos: Iterable[Union[Elemento, list]]):
        # Copia os elementos para não alterar o que o usuário passou
        self.elementos: list[Elemento] = [
            replace(e) if isinstance(e, Elemento) else Elemento.de_lista(e)
            for e in elementos
        ]
        if not self.elementos:
            raise ValueError("Uma rede precisa de pelo menos um elemento.")

        self._numerar_ocorrencias()
        ordenados = self._ordenar_topologicamente()
        self.itens: list[Union[Elemento, Cardinalidade]] = self._inserir_cardinalidades(ordenados)
        self._cardinalidades = {i.no: i for i in self.itens if isinstance(i, Cardinalidade)}
        self._proximo_uid = self._atribuir_uids()

    @property
    def ordenados(self) -> list[Elemento]:
        """Só os elementos, na ordem final (sem as cardinalidades)."""
        return [i for i in self.itens if isinstance(i, Elemento)]

    # ---- pré-processamento ----------------------------------------------
    def _numerar_ocorrencias(self) -> None:
        vistos = Counter()
        for el in self.elementos:
            chave = (el.nome, el.tipo, el.subtipo)
            el.ocorrencia = vistos[chave]
            vistos[chave] += 1

    def _ordenar_topologicamente(self) -> list[Elemento]:
        """A -> B se a saída de A é a entrada de B. Desempata pela 'linha virtual' e
        depois pela ordem em que o usuário escreveu."""
        n = len(self.elementos)

        saidas_por_no = defaultdict(list)
        for i, el in enumerate(self.elementos):
            saidas_por_no[el.no_out].append(i)

        predecessores = {i: set() for i in range(n)}
        sucessores = {i: set() for i in range(n)}
        for i, el in enumerate(self.elementos):
            for p in saidas_por_no.get(el.no_in, ()):
                predecessores[i].add(p)
                sucessores[p].add(i)

        # Linha virtual: cada raiz abre uma linha; os demais herdam a menor linha dos predecessores
        raizes = [i for i in range(n) if not predecessores[i]]
        linha = {r: k for k, r in enumerate(raizes)}
        grau = {i: len(predecessores[i]) for i in range(n)}
        fila = deque(raizes)
        while fila:
            atual = fila.popleft()
            for s in sorted(sucessores[atual]):
                linha[s] = min(linha.get(s, linha[atual]), linha[atual])
                grau[s] -= 1
                if grau[s] == 0:
                    fila.append(s)

        # Ordenação topológica (Kahn) priorizando (linha, ordem original)
        grau = {i: len(predecessores[i]) for i in range(n)}
        prontos = [(linha[i], i) for i in raizes]
        heapq.heapify(prontos)
        ordem = []
        while prontos:
            _, atual = heapq.heappop(prontos)
            ordem.append(self.elementos[atual])
            for s in sucessores[atual]:
                grau[s] -= 1
                if grau[s] == 0:
                    heapq.heappush(prontos, (linha[s], s))

        if len(ordem) != n:
            raise ValueError(
                "Há um ciclo (ou nó sem origem) nas ligações; confira os nós de entrada/saída."
            )
        return ordem

    def _inserir_cardinalidades(self, ordenados: list[Elemento]) -> list[Union[Elemento, Cardinalidade]]:
        """Depois do último elemento que termina num nó com vários ramos, entra um 'O'."""
        total = Counter(el.no_out for el in ordenados)
        vistos = Counter()
        itens = []
        for el in ordenados:
            itens.append(el)
            vistos[el.no_out] += 1
            if total[el.no_out] > 1 and vistos[el.no_out] == total[el.no_out]:
                itens.append(Cardinalidade(no=el.no_out, quantidade=total[el.no_out]))
        return itens

    def _atribuir_uids(self) -> int:
        """UIDs dos nomes (Access) vêm primeiro; os dos Parts começam logo depois."""
        uid_nome = self.UID_INICIAL
        uid_part = self.UID_INICIAL + sum(2 if e.tem_borda else 1 for e in self.ordenados)

        for item in self.itens:
            if isinstance(item, Cardinalidade):
                item.uid_part = uid_part
            else:
                item.uid_nome = uid_nome
                uid_nome += 1
                if item.tem_borda:
                    item.uid_memoria = uid_nome
                    uid_nome += 1
                item.uid_part = uid_part
            uid_part += 1
        return uid_part  # primeiro UID livre (usado pelos fios)

    # ---- XML: <Parts> -----------------------------------------------------
    def xml_parts(self) -> str:
        parts = ET.Element("Parts")
        for el in self.ordenados:
            parts.extend(el.xml_acessos())
        for item in self.itens:
            parts.append(item.xml_part())
        ET.indent(parts, space="  ")
        return ET.tostring(parts, encoding="unicode")

    # ---- XML: <Wires> -----------------------------------------------------
    @staticmethod
    def _fio(uid: int, *conexoes: ET.Element) -> ET.Element:
        fio = ET.Element("Wire", UId=str(uid))
        fio.extend(conexoes)
        return fio

    @staticmethod
    def _name_con(uid: int, nome: str) -> ET.Element:
        return ET.Element("NameCon", UId=str(uid), Name=nome)

    @staticmethod
    def _ident_con(uid: int) -> ET.Element:
        return ET.Element("IdentCon", UId=str(uid))

    def _fio_barramento(self, uid: int) -> ET.Element:
        ligados = [e for e in self.ordenados if e.no_in == NO_BARRAMENTO]
        return self._fio(
            uid,
            ET.Element("Powerrail"),
            *(self._name_con(e.uid_part, e.porta_entrada) for e in ligados),
        )

    def _fios_de_operando(self, el: Elemento, uids) -> list[ET.Element]:
        """Liga o nome (e a memória de borda) ao Part do elemento."""
        fios = []
        if el.tem_borda:
            fios.append(self._fio(next(uids),
                                  self._ident_con(el.uid_memoria),
                                  self._name_con(el.uid_part, "bit")))
        fios.append(self._fio(next(uids),
                              self._ident_con(el.uid_nome),
                              self._name_con(el.uid_part, "operand")))
        return fios

    def _fio_saida(self, origem, destinos: list[Elemento], uids) -> list[ET.Element]:
        """Um fio saindo de `origem` e chegando em todos os `destinos` (série ou divergência)."""
        if not destinos:
            return []
        return [self._fio(next(uids),
                          self._name_con(origem.uid_part, "out"),
                          *(self._name_con(d.uid_part, d.porta_entrada) for d in destinos))]

    def _fios_de_ligacao(self, uids) -> list[ET.Element]:
        fios = []
        for item in self.ordenados:
            convergentes = [e for e in self.ordenados if e.no_out == item.no_out]
            seguintes = [e for e in self.ordenados if e.no_in == item.no_out]

            if len(convergentes) > 1:
                # Paralelo: só o 1º do grupo cuida das ligações (ramos -> 'O' -> seguintes)
                if item is not convergentes[0]:
                    continue
                card = self._cardinalidades[item.no_out]
                for n, ramo in enumerate(convergentes, start=1):
                    fios.append(self._fio(next(uids),
                                          self._name_con(ramo.uid_part, "out"),
                                          self._name_con(card.uid_part, f"in{n}")))
                origem = card
            else:
                origem = item

            fios.extend(self._fio_saida(origem, seguintes, uids))
        return fios

    def xml_wires(self) -> str:
        uids = itertools.count(self._proximo_uid)  # gerador novo a cada chamada
        wires = ET.Element("Wires")
        wires.append(self._fio_barramento(next(uids)))
        for el in self.ordenados:
            wires.extend(self._fios_de_operando(el, uids))
        wires.extend(self._fios_de_ligacao(uids))
        ET.indent(wires, space="  ")
        return ET.tostring(wires, encoding="unicode")

    def xml(self) -> str:
        return self.xml_parts() + "\n" + self.xml_wires()