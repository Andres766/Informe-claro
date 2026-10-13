import { useEffect, useState } from 'react'
import { api, sesion } from './api'
import Acceso from './components/Acceso'
import SubirInforme from './components/SubirInforme'
import ResultadoInforme from './components/ResultadoInforme'
import Historial from './components/Historial'

export default function App() {
  // undefined = comprobando la sesión guardada; null = sin sesión
  const [usuario, setUsuario] = useState(sesion.activa() ? undefined : null)
  const [avisoAcceso, setAvisoAcceso] = useState('')
  const [vista, setVista] = useState('subir') // 'subir' | 'resultado' | 'historial'
  const [informe, setInforme] = useState(null)
  const [motor, setMotor] = useState(null)

  useEffect(() => {
    api.salud().then((s) => setMotor(s.motor)).catch(() => setMotor(null))

    sesion.alExpirar(() => {
      setUsuario(null)
      setAvisoAcceso('Tu sesión expiró. Vuelve a iniciar sesión.')
    })

    if (sesion.activa()) {
      api.yo()
        .then(setUsuario)
        .catch((e) => {
          setUsuario(null)
          if (sesion.activa()) setAvisoAcceso(e.message) // error de red, no de sesión
        })
    }
  }, [])

  const ingresar = (u) => {
    setAvisoAcceso('')
    setVista('subir')
    setInforme(null)
    setUsuario(u)
  }

  const salir = () => {
    sesion.cerrar()
    setUsuario(null)
    setAvisoAcceso('')
    setInforme(null)
  }

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
        {usuario && (
          <nav className="barra__nav">
            <button className={vista !== 'historial' ? 'activo' : ''} onClick={() => setVista('subir')}>
              Nuevo informe
            </button>
            <button className={vista === 'historial' ? 'activo' : ''} onClick={() => setVista('historial')}>
              Mi historial
            </button>
            <span className="barra__usuario" title={usuario.email}>{usuario.nombre.split(' ')[0]}</span>
            <button onClick={salir}>Salir</button>
          </nav>
        )}
      </header>

      <main className="contenido">
        {usuario === undefined && <p className="tenue cargando">Conectando con el servidor…</p>}
        {usuario === null && <Acceso onIngreso={ingresar} aviso={avisoAcceso} />}
        {usuario && vista === 'subir' && <SubirInforme onListo={mostrarInforme} motor={motor} />}
        {usuario && vista === 'resultado' && informe && (
          <ResultadoInforme informe={informe} onNuevo={() => setVista('subir')} />
        )}
        {usuario && vista === 'historial' && <Historial onAbrir={mostrarInforme} />}
      </main>

      <footer className="pie">
        InformeClaro explica tus resultados, pero no diagnostica ni recomienda tratamientos.
        La interpretación clínica corresponde siempre a tu médico.
      </footer>
    </div>
  )
}
