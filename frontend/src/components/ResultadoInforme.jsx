import { useState } from 'react'

const ETIQUETAS = {
  normal: 'Dentro del rango',
  alto: 'Por encima del rango',
  bajo: 'Por debajo del rango',
  sin_rango: 'Sin rango',
}

const num = (s) => parseFloat(String(s).replace(',', '.'))

// Barra visual: dónde cae el valor respecto al rango de referencia.
function BarraRango({ valor, rango }) {
  const v = num(valor)
  let min, max
  const entre = rango.match(/^([\d.,]+)\s*[-–]\s*([\d.,]+)$/)
  const menor = rango.match(/^[<≤]=?\s*([\d.,]+)$/)
  const mayor = rango.match(/^[>≥]=?\s*([\d.,]+)$/)
  if (entre) [min, max] = [num(entre[1]), num(entre[2])]
  else if (menor) [min, max] = [0, num(menor[1])]
  else if (mayor) [min, max] = [num(mayor[1]), num(mayor[1]) * 2]
  if (Number.isNaN(v) || min === undefined || max <= min) return null

  const margen = (max - min) * 0.5
  const inicio = Math.max(0, min - margen)
  const fin = max + margen
  const pos = (x) => Math.min(100, Math.max(0, ((x - inicio) / (fin - inicio)) * 100))

  return (
    <div className="barra-rango" aria-hidden="true">
      <div className="barra-rango__normal" style={{ left: `${pos(min)}%`, width: `${pos(max) - pos(min)}%` }} />
      <div className="barra-rango__punto" style={{ left: `${pos(v)}%` }} />
    </div>
  )
}

export default function ResultadoInforme({ informe, onNuevo }) {
  const [filtro, setFiltro] = useState('todos')
  const [copiado, setCopiado] = useState(false)

  const fuera = informe.valores.filter((v) => v.estado === 'alto' || v.estado === 'bajo')
  const visibles = filtro === 'fuera' ? fuera : informe.valores

  const copiarPreguntas = async () => {
    const texto = informe.preguntas.map((p, i) => `${i + 1}. ${p.texto_pregunta}`).join('\n')
    await navigator.clipboard.writeText(texto)
    setCopiado(true)
    setTimeout(() => setCopiado(false), 2000)
  }

  return (
    <section className="resultado">
      <div className="resultado__cabecera">
        <div>
          <h1>{informe.nombre_archivo}</h1>
          <p className="tenue">
            {new Date(informe.fecha_carga).toLocaleString('es-CO', { dateStyle: 'long', timeStyle: 'short' })}
            {' · '}motor: <code>{informe.motor}</code>
          </p>
        </div>
        <button className="boton boton--secundario" onClick={onNuevo}>Subir otro informe</button>
      </div>

      <p className="alerta alerta--aviso">{informe.aviso}</p>

      <div className="tarjeta resumen">
        <h2>Resumen</h2>
        <p>{informe.resumen}</p>
        <div className="cifras">
          <div><strong>{informe.valores.length}</strong><span>valores</span></div>
          <div><strong>{informe.valores.length - fuera.length}</strong><span>dentro del rango</span></div>
          <div className={fuera.length ? 'cifras--atencion' : ''}>
            <strong>{fuera.length}</strong><span>para conversar con tu médico</span>
          </div>
        </div>
      </div>

      <div className="layout-resultado">
        <div>
          <div className="filtros">
            <h2>Tus valores</h2>
            <div className="segmentado">
              <button className={filtro === 'todos' ? 'activo' : ''} onClick={() => setFiltro('todos')}>Todos</button>
              <button className={filtro === 'fuera' ? 'activo' : ''} onClick={() => setFiltro('fuera')}>
                Fuera de rango ({fuera.length})
              </button>
            </div>
          </div>

          <ul className="valores">
            {visibles.map((v) => (
              <li key={v.id} className={`tarjeta valor valor--${v.estado}`}>
                <div className="valor__fila">
                  <h3>{v.nombre_valor}</h3>
                  <span className={`etiqueta etiqueta--${v.estado}`}>{ETIQUETAS[v.estado]}</span>
                </div>
                <p className="valor__dato">
                  <strong>{v.valor}</strong> {v.unidad}
                  {v.rango_referencia && <span className="tenue"> · referencia {v.rango_referencia}</span>}
                </p>
                {v.rango_referencia && <BarraRango valor={v.valor} rango={v.rango_referencia} />}
                <p>{v.explicacion_ia}</p>
              </li>
            ))}
          </ul>
        </div>

        <aside className="tarjeta preguntas">
          <h2>Preguntas para tu próxima consulta</h2>
          <ol>
            {informe.preguntas.map((p) => <li key={p.id}>{p.texto_pregunta}</li>)}
          </ol>
          <button className="boton boton--secundario" onClick={copiarPreguntas}>
            {copiado ? '¡Copiadas!' : 'Copiar preguntas'}
          </button>
        </aside>
      </div>
    </section>
  )
}
