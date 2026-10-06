import { useEffect, useState } from 'react'
import { api } from '../api'

export default function Historial({ onAbrir }) {
  const [informes, setInformes] = useState(null)
  const [error, setError] = useState('')

  const cargar = () => api.listarInformes().then(setInformes).catch((e) => setError(e.message))

  useEffect(() => { cargar() }, [])

  const abrir = async (id) => {
    try {
      onAbrir(await api.verInforme(id))
    } catch (e) {
      setError(e.message)
    }
  }

  const eliminar = async (id) => {
    if (!confirm('¿Eliminar este informe de tu historial?')) return
    try {
      await api.eliminarInforme(id)
      cargar()
    } catch (e) {
      setError(e.message)
    }
  }

  return (
    <section>
      <h1>Mi historial</h1>
      {error && <p className="alerta alerta--error">{error}</p>}
      {informes === null && !error && <p className="tenue">Cargando…</p>}
      {informes?.length === 0 && <p className="tenue">Aún no has subido ningún informe.</p>}

      <ul className="historial">
        {informes?.map((i) => (
          <li key={i.id} className="tarjeta historial__item">
            <button className="historial__abrir" onClick={() => abrir(i.id)}>
              <strong>{i.nombre_archivo}</strong>
              <span className="tenue">
                {new Date(i.fecha_carga).toLocaleDateString('es-CO', { dateStyle: 'medium' })}
                {' · '}{i.total_valores} valores
              </span>
            </button>
            {i.fuera_de_rango > 0
              ? <span className="etiqueta etiqueta--alto">{i.fuera_de_rango} fuera de rango</span>
              : <span className="etiqueta etiqueta--normal">Todo en rango</span>}
            <button className="icono" aria-label="Eliminar" title="Eliminar" onClick={() => eliminar(i.id)}>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"
                strokeLinecap="round" strokeLinejoin="round"><path d="M3 6h18" /><path d="M8 6V4h8v2" />
                <path d="M19 6l-1 14H6L5 6" /></svg>
            </button>
          </li>
        ))}
      </ul>
    </section>
  )
}
