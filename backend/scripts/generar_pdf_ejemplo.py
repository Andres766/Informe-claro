"""Genera un informe de laboratorio ficticio para probar la app.

Uso:  python scripts/generar_pdf_ejemplo.py
Crea samples/informe_ejemplo.pdf (datos inventados, no corresponden a ninguna persona).
"""
from pathlib import Path

from fpdf import FPDF

VALORES = [
    ("QUÍMICA SANGUÍNEA", [
        ("Glucosa en ayunas", "112", "mg/dL", "70 - 100"),
        ("Colesterol total", "215", "mg/dL", "< 200"),
        ("Colesterol HDL", "48", "mg/dL", "> 40"),
        ("Colesterol LDL", "138", "mg/dL", "< 130"),
        ("Triglicéridos", "145", "mg/dL", "< 150"),
        ("Creatinina", "0.9", "mg/dL", "0.6 - 1.2"),
        ("Ácido úrico", "5.1", "mg/dL", "3.5 - 7.2"),
    ]),
    ("HEMOGRAMA", [
        ("Hemoglobina", "11.8", "g/dL", "12.0 - 16.0"),
        ("Hematocrito", "36.5", "%", "36 - 46"),
        ("Leucocitos", "7.2", "10^3/uL", "4.5 - 11.0"),
        ("Plaquetas", "250", "10^3/uL", "150 - 450"),
    ]),
    ("HORMONAS", [
        ("TSH", "2.4", "uUI/mL", "0.4 - 4.0"),
    ]),
]


def main():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 15)
    pdf.cell(0, 9, "LABORATORIO CLÍNICO DEMO S.A.S.", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", size=9)
    pdf.cell(0, 5, "Pasto, Nariño - Documento de prueba con datos ficticios", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)
    for linea in ["Paciente: María Fernanda Ruiz", "Documento: 1085123456", "Fecha de toma: 2026-09-20"]:
        pdf.cell(0, 5, linea, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    for seccion, filas in VALORES:
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(0, 7, seccion, new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", size=10)
        for nombre, valor, unidad, rango in filas:
            pdf.cell(70, 6, nombre)
            pdf.cell(25, 6, valor)
            pdf.cell(30, 6, unidad)
            pdf.cell(0, 6, rango, new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)

    pdf.ln(4)
    pdf.set_font("Helvetica", "I", 8)
    pdf.multi_cell(0, 4, "Los rangos de referencia corresponden a adultos. "
                         "Bacteriólogo responsable: firma digital.")

    destino = Path(__file__).resolve().parent.parent / "samples" / "informe_ejemplo.pdf"
    destino.parent.mkdir(exist_ok=True)
    pdf.output(str(destino))
    print(f"PDF generado en {destino}")


if __name__ == "__main__":
    main()
