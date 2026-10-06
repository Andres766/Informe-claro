import { useRef, useState } from 'react'
import { api } from '../api'

const PASOS = ['Leyendo el PDF…', 'Extrayendo los valores…', 'Preparando la explicación…']

export default function SubirInforme({ onListo, motor }) {
  const [archivo, setArchivo] = useState(null)
  const [arrastrando, setArrastrando] = useState(false)
  const [cargando, setCargando] = useState(false)
  const [paso, setPaso] = useState(0)
  const [error, setError] = useState('')
  const input = useRef(null)

  const elegir = (f) => {
    setError('')
    if (!f) return
    if (f.type !== 'application/pdf' && !f.name.toLowerCase().endsWith('.pdf')) {
      setError('Selecciona un archivo PDF.')
      return
    }
    setArchivo(f)
  }

  const enviar = async () => {
    setCargando(true)
    setError('')
    setPaso(0)
    const timer = setInterval(() => setPaso((p) => Math.min(p + 1, PASOS.length - 1)), 1500)
    try {
      onListo(await api.subirInforme(archivo))
    } catch (e) {
      setError(e.message)
    } finally {
      clearInterval(timer)
      setCargando(false)
    }
  }

  return (
    <section className="subir">
      <h1>Entiende tus resultados de laboratorio</h1>
      <p className="subir__intro">
        Sube el PDF de tu examen y te explicamos cada valor en palabras sencillas, junto con
        preguntas para llevar a tu próxima consulta.
      </p>

      <div
        className={`zona ${arrastrando ? 'zona--activa' : ''} ${archivo ? 'zona--lista' : ''}`}
        onClick={() => !cargando && input.current.click()}
        onDragOver={(e) => { e.preventDefault(); setArrastrando(true) }}
        onDragLeave={() => setArrastrando(false)}
        onDrop={(e) => { e.preventDefault(); setArrastrando(false); elegir(e.dataTransfer.files[0]) }}
        role="button"
        tabIndex={0}
        onKeyDown={(e) => e.key === 'Enter' && input.current.click()}
      >
        <input ref={input} type="file" accept="application/pdf,.pdf" hidden
          onChange={(e) => elegir(e.target.files[0])} />
        <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6"
          strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
          <path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z" /><path d="M14 3v5h5" />
          <path d="M12 17v-6" /><path d="m9 14 3-3 3 3" />
        </svg>
        {archivo
          ? <p><strong>{archivo.name}</strong><br /><small>{(archivo.size / 1024).toFixed(0)} KB · haz clic para cambiarlo</small></p>
          : <p><strong>Arrastra tu PDF aquí</strong><br /><small>o haz clic para buscarlo</small></p>}
      </div>

      {error && <p className="alerta alerta--error">{error}</p>}

      <button className="boton" disabled={!archivo || cargando} onClick={enviar}>
        {cargando ? PASOS[paso] : 'Explicar mi informe'}
      </button>

      <ul className="garantias">
        <li>No guardamos tu PDF: solo los valores y su explicación.</li>
        <li>Tus datos personales se ocultan antes de procesar el texto.</li>
        <li>No es un diagnóstico: la decisión clínica es de tu médico.</li>
      </ul>

      {motor && <p className="motor">Motor de interpretación: <code>{motor}</code></p>}
    </section>
  )
}
