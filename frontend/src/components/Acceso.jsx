import { useState } from 'react'
import { api, sesion } from '../api'

export default function Acceso({ onIngreso, aviso }) {
  const [modo, setModo] = useState('login') // 'login' | 'registro'
  const [datos, setDatos] = useState({ nombre: '', email: '', password: '' })
  const [error, setError] = useState('')
  const [enviando, setEnviando] = useState(false)

  const esRegistro = modo === 'registro'

  const cambiar = (e) => setDatos({ ...datos, [e.target.name]: e.target.value })

  const cambiarModo = () => {
    setModo(esRegistro ? 'login' : 'registro')
    setError('')
  }

  const enviar = async (e) => {
    e.preventDefault()
    setError('')
    setEnviando(true)
    try {
      const { access_token, usuario } = esRegistro
        ? await api.registro(datos)
        : await api.login({ email: datos.email, password: datos.password })
      sesion.iniciar(access_token)
      onIngreso(usuario)
    } catch (err) {
      setError(err.message)
    } finally {
      setEnviando(false)
    }
  }

  return (
    <section className="acceso">
      <div className="acceso__intro">
        <h1>Entiende tus resultados de laboratorio</h1>
        <p>
          Sube el PDF de tu examen y te explicamos cada valor en palabras sencillas, junto con
          preguntas para llevar a tu próxima consulta.
        </p>
        <ul className="garantias">
          <li>Tu historial es privado: solo tú puedes verlo.</li>
          <li>No guardamos tu PDF: solo los valores y su explicación.</li>
          <li>No es un diagnóstico: la decisión clínica es de tu médico.</li>
        </ul>
      </div>

      <form className="tarjeta acceso__form" onSubmit={enviar} noValidate>
        <h2>{esRegistro ? 'Crea tu cuenta' : 'Inicia sesión'}</h2>
        {aviso && !error && <p className="alerta alerta--aviso">{aviso}</p>}

        {esRegistro && (
          <label>
            Nombre
            <input name="nombre" value={datos.nombre} onChange={cambiar} autoComplete="name" required />
          </label>
        )}
        <label>
          Correo electrónico
          <input name="email" type="email" value={datos.email} onChange={cambiar} autoComplete="email" required />
        </label>
        <label>
          Contraseña
          <input name="password" type="password" value={datos.password} onChange={cambiar} required
            minLength={esRegistro ? 8 : undefined}
            autoComplete={esRegistro ? 'new-password' : 'current-password'} />
          {esRegistro && <small>Mínimo 8 caracteres.</small>}
        </label>

        {error && <p className="alerta alerta--error">{error}</p>}

        <button className="boton" disabled={enviando}>
          {enviando ? 'Un momento…' : esRegistro ? 'Crear cuenta' : 'Entrar'}
        </button>

        <p className="acceso__cambio">
          {esRegistro ? '¿Ya tienes cuenta?' : '¿Aún no tienes cuenta?'}{' '}
          <button type="button" className="enlace" onClick={cambiarModo}>
            {esRegistro ? 'Inicia sesión' : 'Regístrate'}
          </button>
        </p>
      </form>
    </section>
  )
}
