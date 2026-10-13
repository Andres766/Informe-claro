"""Genera informes de laboratorio ficticios para probar la app.

Uso:  python scripts/generar_pdf_ejemplo.py
Crea en samples/ un PDF por cada informe de INFORMES (datos inventados, no corresponden a ninguna persona).
"""
from pathlib import Path

from fpdf import FPDF

VALORES_1 = [
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

# Segundo informe: usa coma decimal (formato común en Colombia) y otros exámenes.
VALORES_2 = [
    ("PERFIL LIPÍDICO", [
        ("Colesterol total", "182", "mg/dL", "< 200"),
        ("Colesterol HDL", "36", "mg/dL", "> 40"),
        ("Colesterol LDL", "108", "mg/dL", "< 130"),
        ("Triglicéridos", "212", "mg/dL", "< 150"),
    ]),
    ("QUÍMICA SANGUÍNEA", [
        ("Glucosa en ayunas", "94", "mg/dL", "70 - 100"),
        ("Hemoglobina glicosilada", "5,4", "%", "4,0 - 5,6"),
        ("Creatinina", "1,3", "mg/dL", "0,7 - 1,2"),
        ("Nitrógeno ureico", "15", "mg/dL", "7 - 20"),
        ("Transaminasa ALT", "28", "U/L", "7 - 56"),
        ("Transaminasa AST", "24", "U/L", "10 - 40"),
    ]),
    ("VITAMINAS", [
        ("Vitamina D", "18", "ng/mL", "30 - 100"),
        ("Vitamina B12", "420", "pg/mL", "200 - 900"),
    ]),
]

INFORMES = [
    ("informe_ejemplo.pdf", "María Fernanda Ruiz", "1085123456", "2026-09-20", VALORES_1),
    ("informe_ejemplo_2.pdf", "Carlos Andrés Benavides", "1004567891", "2026-10-02", VALORES_2),
]


def generar(archivo, paciente, documento, fecha, valores):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 15)
    pdf.cell(0, 9, "LABORATORIO CLÍNICO DEMO S.A.S.", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", size=9)
    pdf.cell(0, 5, "Pasto, Nariño - Documento de prueba con datos ficticios", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)
    for linea in [f"Paciente: {paciente}", f"Documento: {documento}", f"Fecha de toma: {fecha}"]:
        pdf.cell(0, 5, linea, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    for seccion, filas in valores:
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

    destino = Path(__file__).resolve().parent.parent / "samples" / archivo
    destino.parent.mkdir(exist_ok=True)
    pdf.output(str(destino))
    print(f"PDF generado en {destino}")


def main():
    for informe in INFORMES:
        generar(*informe)


if __name__ == "__main__":
    main()
