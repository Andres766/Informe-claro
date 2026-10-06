import os
from pathlib import Path

# Base de datos temporal y modo demo (sin API key) para las pruebas.
os.environ["DATABASE_URL"] = "sqlite:///./test_informeclaro.db"
os.environ["ANTHROPIC_API_KEY"] = ""

import pytest
from fastapi.testclient import TestClient

from app.database import engine
from app.main import app
from app.services.pdf_parser import anonimizar, clasificar
from app.services.prompt_orchestrator import aplicar_guardrails

PDF_EJEMPLO = Path(__file__).resolve().parent.parent / "samples" / "informe_ejemplo.pdf"


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c
    engine.dispose()
    Path("test_informeclaro.db").unlink(missing_ok=True)


@pytest.mark.parametrize("valor,rango,esperado", [
    ("112", "70 - 100", "alto"),
    ("65", "70 - 100", "bajo"),
    ("85", "70 - 100", "normal"),
    ("215", "< 200", "alto"),
    ("48", "> 40", "normal"),
    ("0,9", "0,6 - 1,2", "normal"),
    ("positivo", "negativo", "sin_rango"),
])
def test_clasificar(valor, rango, esperado):
    assert clasificar(valor, rango) == esperado


def test_anonimizar_oculta_datos_personales():
    texto = anonimizar("Paciente: Juan Pérez\nCorreo juan@mail.com\nGlucosa 90 mg/dL 70 - 100\nID 1085123456")
    assert "Juan" not in texto and "juan@mail.com" not in texto and "1085123456" not in texto
    assert "Glucosa 90 mg/dL 70 - 100" in texto


@pytest.mark.parametrize("texto", [
    "Usted tiene diabetes.",
    "Te recomiendo tomar metformina.",
    "Tome el medicamento cada 8 horas.",
    "Este valor es peligroso.",
])
def test_guardrails_bloquean_diagnosticos_y_tratamientos(texto):
    assert aplicar_guardrails(texto) != texto


def test_guardrails_dejan_pasar_explicaciones_neutrales():
    texto = "Este examen mide el azúcar en la sangre. Tu resultado está por encima del rango de referencia."
    assert aplicar_guardrails(texto) == texto


def test_flujo_completo(client):
    with PDF_EJEMPLO.open("rb") as f:
        r = client.post("/api/informes", files={"archivo": ("informe_ejemplo.pdf", f, "application/pdf")})
    assert r.status_code == 201, r.text
    informe = r.json()
    assert len(informe["valores"]) == 12
    estados = {v["nombre_valor"]: v["estado"] for v in informe["valores"]}
    assert estados["Glucosa en ayunas"] == "alto"
    assert estados["Hemoglobina"] == "bajo"
    assert informe["preguntas"] and "médico" in informe["aviso"]

    historial = client.get("/api/informes").json()
    assert historial[0]["id"] == informe["id"] and historial[0]["fuera_de_rango"] == 4

    assert client.get(f"/api/informes/{informe['id']}").status_code == 200
    assert client.delete(f"/api/informes/{informe['id']}").status_code == 204
    assert client.get(f"/api/informes/{informe['id']}").status_code == 404


def test_rechaza_archivos_que_no_son_pdf(client):
    r = client.post("/api/informes", files={"archivo": ("notas.txt", b"hola", "text/plain")})
    assert r.status_code == 415
