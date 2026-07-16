"""
Modelo de dados central do Gerador de Cards de Formatura PROGRAD/UFSM.
"""
import csv
import io
from dataclasses import dataclass, field
from typing import List


@dataclass
class Formando:
    nome: str = ""
    curso: str = ""


@dataclass
class MembroMesa:
    nome: str = ""
    cargo: str = ""


@dataclass
class Homenageado:
    nome: str = ""
    titulo: str = ""


@dataclass
class DadosCerimonia:
    texto_fixo: str = "ColaÃ§Ãµes de Grau UFSM"
    ano: str = "2025"
    semestre: str = "2"
    formandos: List[Formando] = field(default_factory=list)
    mesa: List[MembroMesa] = field(default_factory=list)
    homenageados: List[Homenageado] = field(default_factory=list)

    @property
    def texto_evento(self) -> str:
        return f"{self.texto_fixo} {self.ano}/{self.semestre}"

    def total_cards(self) -> int:
        return len(self.formandos) + len(self.mesa) + len(self.homenageados)

    def get_card(self, index: int):
        """Retorna o card na posiÃ§Ã£o global (Formandos â†’ Mesa â†’ Homenageados)."""
        total_formandos = len(self.formandos)
        total_mesa = len(self.mesa)

        if index < total_formandos:
            f = self.formandos[index]
            return {
                "tipo": "formando",
                "numero": index + 1,
                "numero_str": f"{index + 1:02d}",
                "nome": f.nome,
                "subtitulo": f.curso,
                "rodape": self.texto_evento,
            }
        index -= total_formandos

        if index < total_mesa:
            m = self.mesa[index]
            return {
                "tipo": "mesa",
                "numero": index + 1,
                "numero_str": f"MESA - {index + 1}",
                "nome": m.nome,
                "subtitulo": m.cargo,
                "rodape": self.texto_evento,
            }
        index -= total_mesa

        h = self.homenageados[index]
        return {
            "tipo": "homenageado",
            "numero": index + 1,
            "numero_str": str(index + 1),
            "nome": h.nome,
            "subtitulo": h.titulo,
            "rodape": self.texto_evento,
        }


# â”€â”€ Helpers CSV â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def _detect_delimiter(text: str) -> str:
    first_line = text.split('\n', 1)[0]
    if ';' in first_line:
        return ';'
    if '\t' in first_line:
        return '\t'
    return ','


def parse_csv_formandos(text: str) -> List[Formando]:
    delim = _detect_delimiter(text)
    reader = csv.DictReader(io.StringIO(text), delimiter=delim)
    result = []
    for row in reader:
        nome = ""
        curso = ""
        for k, v in row.items():
            if not k or not v:
                continue
            k_clean = str(k).strip().lower()
            if not nome and ("nome" in k_clean or "formando" in k_clean or "aluno" in k_clean):
                nome = str(v).strip()
            elif not curso and ("curso" in k_clean or "gradua" in k_clean):
                curso = str(v).strip()
        
        if not nome or not curso:
            vals = [str(v).strip() for v in row.values() if v is not None and str(v).strip()]
            if not nome and len(vals) >= 1:
                nome = vals[0]
            if not curso and len(vals) >= 2:
                curso = vals[1] if vals[0] == nome else vals[0]
                
        if nome:
            result.append(Formando(nome=nome, curso=curso))
    return result


def parse_csv_mesa(text: str) -> List[MembroMesa]:
    delim = _detect_delimiter(text)
    reader = csv.DictReader(io.StringIO(text), delimiter=delim)
    result = []
    for row in reader:
        nome = ""
        cargo = ""
        for k, v in row.items():
            if not k or not v:
                continue
            k_clean = str(k).strip().lower()
            if not nome and ("nome" in k_clean or "membro" in k_clean):
                nome = str(v).strip()
            elif not cargo and ("cargo" in k_clean or "fun" in k_clean or "tÃ­t" in k_clean or "tit" in k_clean):
                cargo = str(v).strip()
                
        if not nome or not cargo:
            vals = [str(v).strip() for v in row.values() if v is not None and str(v).strip()]
            if not nome and len(vals) >= 1:
                nome = vals[0]
            if not cargo and len(vals) >= 2:
                cargo = vals[1] if vals[0] == nome else vals[0]
                
        if nome:
            result.append(MembroMesa(nome=nome, cargo=cargo))
    return result


def parse_csv_homenageados(text: str) -> List[Homenageado]:
    delim = _detect_delimiter(text)
    reader = csv.DictReader(io.StringIO(text), delimiter=delim)
    result = []
    for row in reader:
        nome = ""
        titulo = ""
        for k, v in row.items():
            if not k or not v:
                continue
            k_clean = str(k).strip().lower()
            if not nome and ("nome" in k_clean or "homenageado" in k_clean):
                nome = str(v).strip()
            elif not titulo and ("tit" in k_clean or "tÃ­t" in k_clean or "cargo" in k_clean or "turma" in k_clean):
                titulo = str(v).strip()
                
        if not nome or not titulo:
            vals = [str(v).strip() for v in row.values() if v is not None and str(v).strip()]
            if not nome and len(vals) >= 1:
                nome = vals[0]
            if not titulo and len(vals) >= 2:
                titulo = vals[1] if vals[0] == nome else vals[0]
                
        if nome:
            result.append(Homenageado(nome=nome, titulo=titulo))
    return result


def export_csv_formandos(formandos: List[Formando]) -> str:
    out = io.StringIO()
    w = csv.writer(out, delimiter=';')
    w.writerow(["Nome", "Curso"])
    for f in formandos:
        w.writerow([f.nome, f.curso])
    return out.getvalue()


def export_csv_mesa(mesa: List[MembroMesa]) -> str:
    out = io.StringIO()
    w = csv.writer(out, delimiter=';')
    w.writerow(["Nome", "Cargo"])
    for m in mesa:
        w.writerow([m.nome, m.cargo])
    return out.getvalue()


def export_csv_homenageados(homenageados: List[Homenageado]) -> str:
    out = io.StringIO()
    w = csv.writer(out, delimiter=';')
    w.writerow(["Nome", "Titulo"])
    for h in homenageados:
        w.writerow([h.nome, h.titulo])
    return out.getvalue()
