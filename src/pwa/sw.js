const V='fw-v3';
self.addEventListener('install',e=>{self.skipWaiting()});
self.addEventListener('activate',e=>{e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k!==V).map(k=>caches.delete(k)))).then(()=>self.clients.claim()))});
self.addEventListener('fetch',e=>{
  const r=e.request;if(r.method!=='GET'||new URL(r.url).origin!==location.origin)return;
  e.respondWith(caches.open(V).then(c=>fetch(r).then(n=>{if(n.ok)c.put(r,n.clone());return n}).catch(()=>c.match(r).then(m=>m||c.match('/')))));
});
