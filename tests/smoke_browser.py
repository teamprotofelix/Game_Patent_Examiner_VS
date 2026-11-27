from playwright.sync_api import sync_playwright
from urllib.parse import urlparse
import pathlib,re,base64,json,sys,time
base=pathlib.Path(__file__).resolve().parents[1]
files=['data/characters.js','data/weapons.js','data/enemies.js','data/stages.js','data/patent-cases.js','js/systems/SaveSystem.js','js/engine/Audio.js','js/engine/Input.js','js/engine/Renderer.js','js/engine/Game.js','js/ui/Menus.js','js/main.js']
code='\n'.join(re.sub(r'^import .*?;\s*$','',re.sub(r'\bexport\s+','', (base/p).read_text()),flags=re.M) for p in files).replace('loadAssets();','/* loadAssets skipped in internal headless smoke harness */').replace("window.addEventListener('load',()=>navigator.serviceWorker.register", "window.addEventListener('load',()=>navigator.serviceWorker.register")
html=(base/'index.html').read_text();html=re.sub(r'<link rel="stylesheet"[^>]*>','',html);html=re.sub(r'<script type="module"[^>]*></script>','',html);html=html.replace('</head>',f'<style>{(base/"css/main.css").read_text()}\n{(base/"css/ui.css").read_text()}</style></head>')
# Browser won't load relative paths from about:blank; assets are injected for test via data URIs.
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-web-security','--disable-dev-shm-usage'])
 page=b.new_page(viewport={'width':1280,'height':720},device_scale_factor=1)
 errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.set_content(html,wait_until='domcontentloaded',timeout=12000)
 page.add_script_tag(content=code)
 # sprite images injected as data uri, exactly same WebP bytes as release
 atlas=json.loads((base/'assets/atlas.json').read_text()); inject={}
 for g in ['characters','enemies','bosses']:
  for ent in atlas[g].values():
   f=base/ent['file']; inject[ent['file']]='data:image/webp;base64,'+base64.b64encode(f.read_bytes()).decode('ascii')
 for s in ['stage1','stage2','stage3']:
  f=base/f'assets/backgrounds/{s}.webp';inject['assets/backgrounds/'+s+'.webp']='data:image/webp;base64,'+base64.b64encode(f.read_bytes()).decode('ascii')
 page.evaluate('manifest=>{window.__GAME_TEST__.assets.atlas=manifest}',atlas)
 # add data images one by one
 for src,data in inject.items():
  page.evaluate('({src,data})=>{let i=new Image();i.src=data;window.__GAME_TEST__.assets.images[src]=i}',{'src':src,'data':data})
 page.wait_for_timeout(1200)
 print('headless page loaded');print('errors',errors)
 print('initial',page.evaluate('window.__GAME_TEST__.game.state'))
 page.locator('#go-character').click();page.wait_for_timeout(250)
 print('select',page.locator('#screen-select').is_visible());page.locator('#start-game').click();page.wait_for_timeout(3000)
 print('state',page.evaluate('window.__GAME_TEST__.game.state'))
 print('enemies',page.evaluate('window.__GAME_TEST__.game.enemies.length'))
 print('time',page.locator('#time-text').inner_text())
 page.screenshot(path=str(base/'tests'/'smoke-screenshot.png'))
 page.keyboard.press('Space');page.keyboard.press('KeyQ');page.wait_for_timeout(350)
 print('dash',page.evaluate('window.__GAME_TEST__.game.player.dashCD'))
 page.evaluate('window.__GAME_TEST__.game.openLevelUp()')
 print('levelup',page.locator('#modal-level').is_visible(),page.locator('#level-cards button').count())
 page.locator('#level-cards button').first.click()
 print('after upgrade',page.evaluate('window.__GAME_TEST__.game.state'))
 # manually trigger first boss and verify telegraph
 page.evaluate('window.__GAME_TEST__.game.introduceBoss(0)')
 print('bossintro',page.locator('#modal-boss').is_visible());page.wait_for_timeout(3000)
 print('boss state',page.evaluate('window.__GAME_TEST__.game.state'))
 print('errors',errors)
 # Verify all three boss outcomes and optional patent cases without waiting 10 minutes.
 page.evaluate('''()=>{const g=window.__GAME_TEST__.game;g.state='playing';if(g.boss)g.damage(g.boss,g.boss.hp+1000,g.player,true)}''')
 print('boss1 reward state',page.evaluate('window.__GAME_TEST__.game.state'))
 if page.locator('#modal-event').is_visible():
  page.locator('#case-options button').first.click();page.locator('#case-continue').click()
 page.evaluate('''()=>{const g=window.__GAME_TEST__.game;g.introduceBoss(1);g.state='playing';g.damage(g.boss,g.boss.hp+1000,g.player,true)}''')
 if page.locator('#modal-event').is_visible():
  page.locator('#case-options button').nth(1).click();page.locator('#case-continue').click()
 page.evaluate('''()=>{const g=window.__GAME_TEST__.game;g.introduceBoss(2);g.state='playing';g.damage(g.boss,g.boss.hp+1000,g.player,true)}''')
 print('after boss3',page.evaluate('({state:window.__GAME_TEST__.game.state,bosses:window.__GAME_TEST__.game.bossesDefeated,score:window.__GAME_TEST__.game.score})'))
 print('result visible',page.locator('#modal-result').is_visible())
 print('errors after final',errors)
 page.locator('#home').click();page.locator('#go-character').click()
 page.locator('.char-card').nth(1).click();page.locator('#start-game').click()
 print('selected searcher',page.evaluate('window.__GAME_TEST__.game.character.id'))
 page.set_viewport_size({'width':390,'height':840})
 page.wait_for_timeout(350)
 print('mobile hud and dash',page.locator('#hud').is_visible(),page.locator('#dash-btn').bounding_box())
 print('errors mobile',errors)
 b.close()
