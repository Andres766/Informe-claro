# InformeClaro

Traductor de resultados de laboratorio a lenguaje sencillo.
El paciente sube el PDF de su examen; la app extrae cada valor, lo explica comparándolo con el
rango de referencia y genera preguntas para la próxima consulta. **Nunca diagnostica ni
recomienda tratamiento**: la decisión clínica es 100 % del médico.

Proyecto final individual — Programación Orientada a la Web, Ingeniería de Software, UCC Pasto.

---

## Cómo ejecutarlo

Requisitos: Python 3.11+ y Node 20+.

```bash
# 1. Backend (FastAPI) — http://localhost:8000  (documentación: /docs)
cd backend
python -m venv .venv
.venv\Scripts\activate          # Linux/Mac: source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env          # opcional: poner ANTHROPIC_API_KEY
uvicorn app.main:app --reload

# 2. Frontend (React + Vite) — http://localhost:5173
cd frontend
npm install
npm run dev
```

- Sin `ANTHROPIC_API_KEY` la app funciona en **modo demo**: extrae los valores con reglas
  (regex) y genera explicaciones con plantillas. Con la key usa Claude.
- PDF de prueba con datos ficticios: `backend/samples/informe_ejemplo.pdf`
  (se regenera con `python scripts/generar_pdf_ejemplo.py`).
- Pruebas del backend: `cd backend && pytest` (15 pruebas).

---

## Arquitectura implementada

```
React SPA (PWA) ──► FastAPI (orquestador) ──► Servicio de parsing PDF (pdfplumber)
                          │                ──► Orquestador de prompt ──► API LLM (Claude)
                          └──► Base de datos (SQLite en desarrollo / PostgreSQL en producción)
```

| Capa | Archivo(s) |
|---|---|
| Presentación | `frontend/src/` — `SubirInforme`, `ResultadoInforme`, `Historial`; `public/sw.js` (Service Worker) |
| Aplicación / API | `backend/app/main.py` — `POST/GET/DELETE /api/informes`, `GET /api/salud` |
| Servicio de parsing | `backend/app/services/pdf_parser.py` — extracción, anonimización, clasificación por rango |
| Orquestador de prompt | `backend/app/services/prompt_orchestrator.py` — prompt con guardrails, llamada al LLM, filtro de salida |
| Datos | `backend/app/models.py` — `Usuario`, `InformeCargado`, `ValorExamen`, `PreguntaSugerida` |

### Flujo de `POST /api/informes`

1. El navegador envía el PDF (multipart).
2. `pdfplumber` extrae el texto **en memoria**; el PDF nunca se escribe a disco ni se guarda.
3. Se ocultan los datos personales (nombre, documento, correo, números largos) y se arma el prompt.
4. Se llama a Claude con **salida estructurada** (esquema Pydantic): valores, explicaciones y preguntas.
5. El backend calcula el estado de cada valor (normal / alto / bajo) y aplica el filtro de guardrails.
6. Se guarda en la base de datos y se devuelve al frontend con el aviso médico.

### Guardrails clínicos (en tres capas)

1. **Prompt de sistema**: define qué SÍ hace (explicar, comparar con el rango, sugerir preguntas)
   y qué NO hace (diagnosticar, interpretar causas, recomendar tratamientos, generar alarma).
2. **Decisión determinista**: si un valor está fuera de rango lo decide el código comparando
   números, no el LLM, para que sea siempre verificable.
3. **Filtro de salida**: si la explicación contiene frases de diagnóstico ("usted tiene…"),
   de tratamiento ("tome el medicamento…") o alarmistas ("grave", "urgente"), se reemplaza por
   un texto seguro que remite al médico.

---

## Estado del avance

**Hecho**
- [x] Backend FastAPI con los 6 pasos del flujo de datos, de punta a punta.
- [x] Modelo de datos del diagrama ER con SQLAlchemy (listo para PostgreSQL con `DATABASE_URL`).
- [x] Parsing de PDF con pdfplumber + anonimización antes de enviar al LLM.
- [x] Prompt con guardrails clínicos + salida estructurada con Claude.
- [x] Modo demo / respaldo por reglas si no hay API key o la API falla.
- [x] Frontend React: carga con arrastrar y soltar, resultados con barra de rango, filtro de
      valores fuera de rango, preguntas copiables, historial con eliminación.
- [x] PWA básica: manifest + Service Worker (la carcasa abre sin conexión; los datos de salud no se cachean).
- [x] 15 pruebas automáticas (clasificación, anonimización, guardrails, flujo completo de la API).

**Pendiente (siguientes entregas)**
- [ ] Autenticación con JWT (hoy todo se asocia a un usuario demo) y acceso restringido al propio historial.
- [ ] Probar el prompt con informes reales de distintos laboratorios y ajustar los guardrails.
- [ ] Soporte a PDF escaneados (OCR).
- [ ] Cifrado en reposo de las explicaciones en la base de datos.
- [ ] Despliegue: frontend en Vercel, backend en Render, base de datos en Neon/Supabase.
