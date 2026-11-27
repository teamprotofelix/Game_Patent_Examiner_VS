#!/usr/bin/env python3
"""Headless Chromium logic/UI smoke; this environment blocks localhost and file://
 navigation by administrator policy, so test uses actual release classic-script
 bytes injected in a document (not a mocked/reimplemented engine).
"""
import pathlib,re,base64,sys,json
from playwright.sync_api import sync_playwright
p=pathlib.Path(__file__).resolve().parents[1]
html=(p/'index.html').read_text()
html=re.sub(r'<link rel="stylesheet"[^>]*>','',html)
html=html.replace('</head>',f'<style>{(p/"css/main.css").read_text()}\n{(p/"css/ui.css").read_text()}</style></head>')
html=html.replace('<script defer src="./js/game.bundle.js"></script>','')
bundle=(p/'js/game.bundle.js').read_text(encoding='utf8')
with sync_playwright() as engine:
 browser=engine.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
 page=browser.new_page(viewport={'width':1280,'height':720},device_scale_factor=1)
 errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.set_content(html,wait_until='domcontentloaded')
 page.add_script_tag(content=bundle)
 assert page.locator('#loaded-count').inner_text().startswith('✓ 출격'), 'start stuck'
 assert page.evaluate('typeof window.__GAME_TEST__')=='object', 'bundle not loaded'
 print('boot status:',page.locator('#loaded-count').inner_text())
 # Inject a few real assets for drawing validation. All other entities use nonblocking fallback.
 for source in ['assets/characters/marie.webp','assets/enemies/slime.webp','assets/enemies/ghost.webp','assets/bosses/shadow.webp','assets/backgrounds/stage1.webp','assets/props/crystal.webp']:
  content=base64.b64encode((p/source).read_bytes()).decode('ascii')
  page.evaluate('''({path,data})=>{const im=new Image();im.src='data:image/webp;base64,'+data;window.__GAME_TEST__.assets.images[path]=im}''', {'path':source,'data':content})
 page.wait_for_timeout(900)
 page.locator('#go-character').click()
 assert page.locator('#screen-select').is_visible()
 page.locator('#start-game').click()
 page.wait_for_timeout(800)
 assert page.evaluate('window.__GAME_TEST__.game.state')=='playing', 'start failed'
 assert page.locator('#hud').is_visible(), 'HUD not visible'
 print('spawn:',page.evaluate('({enemies:__GAME_TEST__.game.enemies.length, props:__GAME_TEST__.game.props.length, hp:__GAME_TEST__.game.player.hp})'))
 page.screenshot(path=str(p/'tests'/'v2-battle.png'))
 # Dash, ultimate, new scan.
 page.keyboard.press('Space');page.keyboard.press('KeyQ');page.keyboard.press('KeyE')
 page.wait_for_timeout(150)
 assert page.evaluate('__GAME_TEST__.game.scanCD')>0, 'scan missing'
 print('scan cooldown:',page.evaluate('__GAME_TEST__.game.scanCD'))
 page.evaluate('''()=>{const g=__GAME_TEST__.game;g.props=[{x:g.player.x,y:g.player.y,type:'archive',ttl:100,seed:0}];g.updateProps(.01)}''')
 print('after prop:',page.evaluate('({score:__GAME_TEST__.game.score,props:__GAME_TEST__.game.props.length})'))
 if page.locator('#modal-level').is_visible(): page.locator('#level-cards button').first.click()
 page.evaluate('window.__GAME_TEST__.game.openLevelUp()')
 assert page.locator('#level-cards button').count()==3, 'level cards failed'
 page.locator('#level-cards button').first.click()
 assert page.evaluate('__GAME_TEST__.game.state')=='playing'
 # Boss 1 2 3 immediate defeat simulates the full victory flow
 for i in range(3):
  page.evaluate('''i=>{const g=__GAME_TEST__.game;g.state='playing';g.introduceBoss(i);g.state='playing';g.damage(g.boss,g.boss.hp+1000,g.player,true)}''',i)
  if page.locator('#modal-event').is_visible():
   page.locator('#case-options button').first.click()
   page.locator('#case-continue').click()
 assert page.evaluate('__GAME_TEST__.game.bossesDefeated')==3
 assert page.locator('#modal-result').is_visible(), 'victory missing'
 print('victory:',page.evaluate('({state:__GAME_TEST__.game.state,bosses:__GAME_TEST__.game.bossesDefeated,score:__GAME_TEST__.game.score})'))
 page.locator('#home').click();page.locator('#go-character').click();page.locator('.char-card').nth(2).click();page.locator('#start-game').click()
 assert page.evaluate('__GAME_TEST__.game.character.id')=='alchemist'
 page.set_viewport_size({'width':390,'height':840});page.wait_for_timeout(170)
 assert page.locator('#scan-btn').bounding_box()['x']>=0
 print('mobile scan:',page.locator('#scan-btn').bounding_box())
 print('browser errors:',errors)
 assert not errors,errors
 browser.close()
print('PASS: core UI + v2 mechanics + victory + mobile DOM checks')
