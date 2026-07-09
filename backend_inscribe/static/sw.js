const CACHE_NAME = 'inscribe-system-v1';
const urlsToCache = [
  '/',
  '/menu',
  '/inicio',
  '/static/logo.png',
  'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css'
];

// Instalar el Service Worker y guardar en caché los archivos básicos
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        return cache.addAll(urlsToCache);
      })
  );
});

// Interceptar las peticiones (Sirve desde la caché si no hay internet)
self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => {
        // Devuelve el archivo en caché si existe, si no, hace la petición a la red
        return response || fetch(event.request);
      })
  );
});