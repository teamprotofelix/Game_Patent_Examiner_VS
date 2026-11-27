#!/usr/bin/env python3
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
ver='patent-rejection-legion-v2.0.0'
core=['./','./index.html','./js/game.bundle.js','./css/main.css','./css/ui.css','./manifest.webmanifest']
allassets=['./'+str(f.relative_to(ROOT)).replace('\\','/') for f in (ROOT/'assets').rglob('*') if f.is_file()]
js=f'''/* v2: installation cannot fail because of one optional art file; shell first. */
const CACHE={json.dumps(ver)};
const CORE={json.dumps(core,ensure_ascii=False)};
const ART={json.dumps(allassets,ensure_ascii=False)};
self.addEventListener('install',event=>event.waitUntil((async()=>{{
 const cache=await caches.open(CACHE);
 await Promise.all(CORE.map(async path=>{{try{{await cache.add(path)}}catch(e){{console.warn('shell fetch failed',path,e)}}}}));
 await self.skipWaiting();
}})()));
self.addEventListener('activate',event=>event.waitUntil((async()=>{{
 const keys=await caches.keys();await Promise.all(keys.filter(k=>k.startsWith('patent-rejection-legion-')&&k!==CACHE).map(k=>caches.delete(k)));
 const cache=await caches.open(CACHE);
 // Best effort, per-file cache in background: no all-or-nothing failure.
 await Promise.all(ART.map(async path=>{{try{{const r=await fetch(path);if(r.ok)await cache.put(path,r)}}catch(_){{}}}}));
 await self.clients.claim();
}})()));
self.addEventListener('fetch',event=>{{
 const request=event.request;const url=new URL(request.url);
 if(request.method!=='GET'||url.origin!==location.origin)return;
 event.respondWith((async()=>{{
  const cache=await caches.open(CACHE);
  if(request.mode==='navigate'){{try{{const r=await fetch(request);if(r.ok){{await cache.put('./index.html',r.clone());return r}}}}catch(_){{}}return await cache.match('./index.html')||Response.error()}}
  const cached=await cache.match(request);
  if(cached)return cached;
  try{{const response=await fetch(request);if(response.ok)cache.put(request,response.clone()).catch(()=>{{}});return response}}catch(_){{return Response.error()}}
 }})());
}});
'''
(ROOT/'service-worker.js').write_text(js,encoding='utf8')
print('Service worker v2 written',len(allassets),'art files')
