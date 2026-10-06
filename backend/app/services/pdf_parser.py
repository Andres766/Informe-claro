"""Servicio de Parsing de PDF.

1. Extrae el texto del PDF con pdfplumber (en memoria: el archivo nunca se escribe a disco).
2. Anonimiza datos personales antes de que el texto salga hacia la API del LLM.
3. Ofrece un extractor por reglas (regex) que sirve como modo demo y como respaldo.
"""
import io
import re
from dataclasses import dataclass

import pdfplumber


class PDFInvalidoError(ValueError):
    pass


def extraer_texto(contenido: bytes) -> str:
    try:
        with pdfplumber.open(io.BytesIO(contenido)) as pdf:
            paginas = [p.extract_text() or "" for p in pdf.pages]
    except Exception as exc:  # pdfplumber lanza varios tipos según el daño del archivo
        raise PDFInvalidoError("No se pudo leer el PDF. ¿Es un archivo válido?") from exc

    texto = "\n".join(paginas).strip()
    if not texto:
        raise PDFInvalidoError(
            "El PDF no contiene texto seleccionable (posiblemente es una imagen escaneada)."
        )
    return texto


_PATRONES_PII = [
    # "Paciente: Nombre Apellido" / "Nombre: ..." -> se oculta el valor de la línea
    (re.compile(r"(?im)^(\s*(paciente|nombre|documento|c\.?c\.?|identificaci[oó]n|direcci[oó]n|tel[eé]fono)\s*:).*$"), r"\1 [OCULTO]"),
    # Números largos (cédulas, teléfonos, historias clínicas)
    (re.compile(r"\b\d{6,}\b"), "[OCULTO]"),
    (re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+"), "[OCULTO]"),
]


def anonimizar(texto: str) -> str:
    for patron, reemplazo in _PATRONES_PII:
        texto = patron.sub(reemplazo, texto)
    return texto


# --- Extracción por reglas -------------------------------------------------

_NUM = r"\d+(?:[.,]\d+)?"
_LINEA_VALOR = re.compile(
    rf"^(?P<nombre>[A-Za-zÁÉÍÓÚÜáéíóúüñÑ][A-Za-zÁÉÍÓÚÜáéíóúüñÑ().,%/ -]*?)\s+"
    rf"(?P<valor>{_NUM})\s+"
    rf"(?P<unidad>\S+)\s+"
    rf"(?P<rango>(?:[<>≤≥]=?\s*{_NUM})|(?:{_NUM}\s*[-–]\s*{_NUM}))\s*$"
)


@dataclass
class ValorExtraido:
    nombre_valor: str
    valor: str
    unidad: str
    rango_referencia: str


def extraer_valores_por_reglas(texto: str) -> list[ValorExtraido]:
    valores = []
    for linea in texto.splitlines():
        m = _LINEA_VALOR.match(linea.strip())
        if m:
            valores.append(
                ValorExtraido(
                    nombre_valor=m["nombre"].strip(" .-"),
                    valor=m["valor"],
                    unidad=m["unidad"],
                    rango_referencia=m["rango"].strip(),
                )
            )
    return valores


def _a_float(s: str) -> float:
    return float(s.replace(",", "."))


def clasificar(valor: str, rango: str) -> str:
    """Compara un valor contra su rango de referencia de forma determinista.

    Devuelve "normal", "alto", "bajo" o "sin_rango". Esta decisión la toma el código,
    no el LLM, para que la marca de "fuera de rango" sea siempre verificable.
    """
    try:
        v = _a_float(re.search(_NUM, valor).group())
    except (AttributeError, ValueError):
        return "sin_rango"

    rango = rango.strip()
    if m := re.fullmatch(rf"({_NUM})\s*[-–]\s*({_NUM})", rango):
        bajo, alto = _a_float(m[1]), _a_float(m[2])
        return "bajo" if v < bajo else "alto" if v > alto else "normal"
    if m := re.fullmatch(rf"(<|≤|<=)\s*({_NUM})", rango):
        limite = _a_float(m[2])
        return "normal" if (v < limite if m[1] == "<" else v <= limite) else "alto"
    if m := re.fullmatch(rf"(>|≥|>=)\s*({_NUM})", rango):
        limite = _a_float(m[2])
        return "normal" if (v > limite if m[1] == ">" else v >= limite) else "bajo"
    return "sin_rango"
