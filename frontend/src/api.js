// En producción VITE_API_URL apunta al backend desplegado (Render / Railway).
const BASE = import.meta.env.VITE_API_URL ?? ''

async function pedir(ruta, opciones) {
  let resp
  try {
    resp = await fetch(`${BASE}/api${ruta}`, opciones)
  } catch {
    throw new Error('No se pudo conectar con el servidor. ¿Está encendido el backend?')
  }
  if (resp.status === 204) return null
  const datos = await resp.json().catch(() => ({}))
  if (!resp.ok) throw new Error(datos.detail ?? `Error ${resp.status}`)
  return datos
}

export const api = {
  salud: () => pedir('/salud'),
  subirInforme: (archivo) => {
    const form = new FormData()
    form.append('archivo', archivo)
    return pedir('/informes', { method: 'POST', body: form })
  },
  listarInformes: () => pedir('/informes'),
  verInforme: (id) => pedir(`/informes/${id}`),
  eliminarInforme: (id) => pedir(`/informes/${id}`, { method: 'DELETE' }),
}
