// En producción VITE_API_URL apunta al backend desplegado (Render / Railway).
const BASE = import.meta.env.VITE_API_URL ?? ''
const CLAVE_TOKEN = 'informeclaro_token'

// --- Sesión (token JWT guardado en el navegador) ---------------------------

function leerToken() {
  try {
    return localStorage.getItem(CLAVE_TOKEN)
  } catch {
    return null
  }
}

function guardarToken(token) {
  try {
    if (token) localStorage.setItem(CLAVE_TOKEN, token)
    else localStorage.removeItem(CLAVE_TOKEN)
  } catch {
    // almacenamiento bloqueado (modo privado): la sesión dura solo mientras la pestaña esté abierta
  }
}

let tokenEnMemoria = leerToken()
let alExpirar = () => {}

export const sesion = {
  activa: () => Boolean(tokenEnMemoria),
  iniciar: (token) => {
    tokenEnMemoria = token
    guardarToken(token)
  },
  cerrar: () => {
    tokenEnMemoria = null
    guardarToken(null)
  },
  // La app registra aquí qué hacer cuando el backend responde 401 (token vencido o inválido).
  alExpirar: (fn) => { alExpirar = fn },
}

// --- Peticiones ------------------------------------------------------------

async function pedir(ruta, { auth = true, ...opciones } = {}) {
  const headers = { ...opciones.headers }
  if (auth && tokenEnMemoria) headers.Authorization = `Bearer ${tokenEnMemoria}`

  let resp
  try {
    resp = await fetch(`${BASE}/api${ruta}`, { ...opciones, headers })
  } catch {
    throw new Error('No se pudo conectar con el servidor. ¿Está encendido el backend?')
  }
  if (resp.status === 204) return null
  const datos = await resp.json().catch(() => ({}))
  if (resp.status === 401 && auth) {
    sesion.cerrar()
    alExpirar()
  }
  if (!resp.ok) throw new Error(mensajeDeError(datos, resp.status))
  return datos
}

// FastAPI devuelve `detail` como texto o, en errores de validación, como lista.
function mensajeDeError(datos, status) {
  if (typeof datos.detail === 'string') return datos.detail
  if (Array.isArray(datos.detail)) {
    const campo = datos.detail[0]?.loc?.at(-1)
    if (campo === 'email') return 'Escribe un correo electrónico válido.'
    if (campo === 'password') return 'La contraseña debe tener al menos 8 caracteres.'
    if (campo === 'nombre') return 'Escribe tu nombre.'
  }
  return `Error ${status}`
}

const json = (cuerpo) => ({
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(cuerpo),
})

export const api = {
  salud: () => pedir('/salud', { auth: false }),
  registro: (datos) => pedir('/auth/registro', { auth: false, ...json(datos) }),
  login: (datos) => pedir('/auth/login', { auth: false, ...json(datos) }),
  yo: () => pedir('/auth/yo'),
  subirInforme: (archivo) => {
    const form = new FormData()
    form.append('archivo', archivo)
    return pedir('/informes', { method: 'POST', body: form })
  },
  listarInformes: () => pedir('/informes'),
  verInforme: (id) => pedir(`/informes/${id}`),
  eliminarInforme: (id) => pedir(`/informes/${id}`, { method: 'DELETE' }),
}
