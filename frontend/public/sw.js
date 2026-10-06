// Service Worker mínimo: guarda en caché la "carcasa" de la app para que abra sin conexión.
// Las llamadas a /api nunca se cachean (son datos de salud del usuario).
const CACHE = 'informeclaro-v1'

self.addEventListener('install', (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(['/', '/favicon.svg', '/manifest.webmanifest'])))
  self.skipWaiting()
})

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys().then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
  )
  self.clients.claim()
})

self.addEventListener('fetch', (e) => {
  const url = new URL(e.request.url)
  if (e.request.method !== 'GET' || url.pathname.startsWith('/api')) return
  e.respondWith(
    fetch(e.request)
      .then((resp) => {
        if (resp.ok && url.origin === location.origin) {
          const copia = resp.clone()
          caches.open(CACHE).then((c) => c.put(e.request, copia))
        }
        return resp
      })
      .catch(() => caches.match(e.request).then((r) => r || caches.match('/')))
  )
})
