import { useEffect, useState } from 'react'
import { api } from './api'
import SubirInforme from './components/SubirInforme'
import ResultadoInforme from './components/ResultadoInforme'
import Historial from './components/Historial'

export default function App() {
  const [vista, setVista] = useState('subir') // 'subir' | 'resultado' | 'historial'
  const [informe, setInforme] = useState(null)
  const [motor, setMotor] = useState(null)

  useEffect(() => {
    api.salud().then((s) => setMotor(s.motor)).catch(() => setMotor(null))
  }, [])

  const mostrarInforme = (datos) => {
    setInforme(datos)
    setVista('resultado')
  }

  return (
    <div className="app">
      <header className="barra">
        <div className="barra__marca">
          <img src="/favicon.svg" alt="" width="32" height="32" />
          <span>InformeClaro</span>
        </div>
        <nav className="barra__nav">
          <button className={vista !== 'historial' ? 'activo' : ''} onClick={() => setVista('subir')}>
            Nuevo informe
          </button>
          <button className={vista === 'historial' ? 'activo' : ''} onClick={() => setVista('historial')}>
            Mi historial
          </button>
        </nav>
      </header>

      <main className="contenido">
        {vista === 'subir' && <SubirInforme onListo={mostrarInforme} motor={motor} />}
        {vista === 'resultado' && informe && (
          <ResultadoInforme informe={informe} onNuevo={() => setVista('subir')} />
        )}
        {vista === 'historial' && <Historial onAbrir={mostrarInforme} />}
      </main>

      <footer className="pie">
        InformeClaro explica tus resultados, pero no diagnostica ni recomienda tratamientos.
        La interpretación clínica corresponde siempre a tu médico.
      </footer>
    </div>
  )
}
