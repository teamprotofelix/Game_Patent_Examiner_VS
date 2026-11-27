from pathlib import Path
p=Path(__file__).resolve().parents[1]
g=p/'js/engine/Game.js';s=g.read_text()
s=s.replace("this.weapons={[this.character.weapon]:1};","this.weapons={[this.character.weapon]:1};this.props=[];this.scanCD=0;this.scanTimer=0;this.scanPulse=0;")
s=s.replace("for(let i=0;i<10;i++)this.spawnRandom();this.ui.toast", "for(let i=0;i<10;i++)this.spawnRandom();for(let i=0;i<15;i++)this.spawnProp();this.ui.toast")
s=s.replace("p.ultCD=Math.max(0,p.ultCD-dt);p.regenTimer+=dt", "p.ultCD=Math.max(0,p.ultCD-dt);this.scanCD=Math.max(0,this.scanCD-dt);this.scanTimer=Math.max(0,this.scanTimer-dt);this.scanPulse=Math.max(0,this.scanPulse-dt);p.regenTimer+=dt")
s=s.replace("this.updateEnemies(dt);this.updateProjectiles(dt);this.updateAreas(dt);this.updateWeapons(dt);this.updatePickups(dt);this.updateEffects(dt);", "this.updateEnemies(dt);this.updateProjectiles(dt);this.updateAreas(dt);this.updateWeapons(dt);this.updatePickups(dt);this.updateProps(dt);this.updateEffects(dt);")
s=s.replace("e.animT+=dt;e.life+=dt;", "e.animT+=dt;e.life+=dt;e.facing=(p.x<e.x?-1:1);")
s=s.replace("let value=Math.round(raw*(crit?1.7:1));", "let value=Math.round(raw*(crit?1.7:1)*(this.scanTimer>0?1.28:1));")
s=s.replace(" updateEffects(dt){", """ spawnProp(){if(this.props.length>24)return;const types=['crystal','crystal','archive','archive','healing','portal','burst'];const kind=types[Math.floor(Math.random()*types.length)],a=rand(0,Math.PI*2),r=rand(240,850);const p=this.player;this.props.push({type:kind,x:clamp(p.x+Math.cos(a)*r,100,3900),y:clamp(p.y+Math.sin(a)*r,100,3900),r:26,ttl:200,seed:rand(0,30)})}
 updateProps(dt){for(let i=this.props.length-1;i>=0;i--){const o=this.props[i];o.ttl-=dt;if(o.ttl<=0){this.props.splice(i,1);this.spawnProp();continue}if(len(o,this.player)>65)continue;this.props.splice(i,1);this.spark(o.x,o.y,o.type==='healing'?'#a5ffc7':'#f9d796',15);this.ring(o.x,o.y,75,'#b5faff',.5);switch(o.type){case'crystal':this.player.xp+=9+this.player.level*2;this.score+=120;this.ui.toast('판단력 결정 획득 · EXP 보너스!');break;case'archive':this.score+=380;this.player.xp+=7;this.ui.toast('선행기술 아카이브 수집 · +380점');break;case'healing':this.player.hp=Math.min(this.player.maxHp,this.player.hp+42);this.ui.toast('회복 데이터 +42 HP');break;case'portal':this.player.x=clamp(this.player.x+rand(-250,250),120,3880);this.player.y=clamp(this.player.y+rand(-250,250),120,3880);this.player.invuln=1;this.ui.toast('데이터 포털 · 순간 이동!');break;case'burst':for(const e of this.enemies){if(!e.dead&&len(e,o)<240)this.damage(e,140,{x:o.x,y:o.y},false,1.7)}this.score+=200;this.ui.toast('심사 판단 폭풍 · 광역 타격!');break}this.audio.sound('upgrade');this.spawnProp();if(this.player.xp>=this.player.need&&this.state==='playing'){this.player.xp-=this.player.need;this.player.level++;this.player.need=Math.round(12+this.player.level*6.5);this.openLevelUp()}}
 }
 scan(){if(this.state!=='playing'||this.scanCD>0)return;this.scanCD=17;this.scanTimer=4.5;this.scanPulse=.58;this.ring(this.player.x,this.player.y,340,'#80fef0',.75);this.audio.sound('laser');this.ui.toast('문헌 스캔! 4.5초간 적이 받는 피해 +28%')}
 updateEffects(dt){""")
g.write_text(s)
u=p/'js/ui/Menus.js';s=u.read_text()
s=s.replace("$('#ult-btn').onclick=()=>this.game.ultimate();window.addEventListener('keydown',e=>{if(e.code==='KeyQ'&&!e.repeat&&this.game)this.game.ultimate()});", "$('#ult-btn').onclick=()=>this.game.ultimate();$('#scan-btn').onclick=()=>this.game.scan();window.addEventListener('keydown',e=>{if(e.code==='KeyQ'&&!e.repeat&&this.game)this.game.ultimate();if(e.code==='KeyE'&&!e.repeat&&this.game)this.game.scan()});")
s=s.replace("$('#dash-cooldown').textContent=", "$('#scan-cooldown').textContent=g.scanCD>0?Math.ceil(g.scanCD)+'s':'READY';$('#scan-btn').classList.toggle('unavailable',g.scanCD>0);$('#dash-cooldown').textContent=")
s=s.replace("const src=type==='weapon'?icon(e.icon||e.id):pv(e.id);", "const src=type==='weapon'?icon(e.icon||e.id):pv(e.id);")
s=s.replace('`<img src="${pv(char.id)}" alt="${char.name}"><strong>', '`<img src="./assets/portraits/${char.id}.webp" alt="${char.name}"><strong>')
u.write_text(s)
html=p/'index.html';s=html.read_text()
s=s.replace('<button id="dash-btn"', '<button id="scan-btn" class="action action-scan" aria-label="문헌 스캔">SCAN<small id="scan-cooldown">READY</small></button><button id="dash-btn"')
s=s.replace('Q 궁극기 · Esc', 'Q 궁극기 · E 스캔 · Esc')
html.write_text(s)
# Enemies add new 4 regular + 2 elites; never overwrite existing enemy definitions.
en=p/'data/enemies.js';s=en.read_text()
s=s.replace(" {id:'gear',name:'판단누락 톱니',hp:79,speed:116,damage:13,radius:24,xp:2,behavior:'rush'},", """ {id:'gear',name:'판단누락 톱니',hp:79,speed:116,damage:13,radius:24,xp:2,behavior:'rush'},
 {id:'audit_spider',name:'검증누락 거미',hp:64,speed:118,damage:12,radius:25,xp:2,behavior:'weave'},
 {id:'timeout_wisp',name:'심사기한 위스프',hp:45,speed:159,damage:10,radius:20,xp:2,behavior:'rush'},
 {id:'citation_mimic',name:'문헌도용 미믹',hp:93,speed:82,damage:17,radius:28,xp:3,behavior:'ranged'},
 {id:'syntax_serpent',name:'기재흠결 서펀트',hp:72,speed:129,damage:14,radius:24,xp:3,behavior:'teleport'},""")
s=s.replace(" {id:'elite_wraith',name:'보정불일치 망령',hp:510,speed:115,damage:20,radius:37,xp:19,behavior:'teleport'}", """ {id:'elite_wraith',name:'보정불일치 망령',hp:510,speed:115,damage:20,radius:37,xp:19,behavior:'teleport'},
 {id:'elite_archivist',name:'가공문헌 대사서',hp:620,speed:88,damage:24,radius:42,xp:21,behavior:'ranged'},
 {id:'elite_reactor',name:'합성오류 반응체',hp:760,speed:90,damage:28,radius:45,xp:25,behavior:'charge'}""")
en.write_text(s)
r=p/'js/engine/Renderer.js';s=r.read_text()
s=s.replace('this.ctx.imageSmoothingEnabled=true}', "this.ctx.imageSmoothingEnabled=true;this.ctx.imageSmoothingQuality='high'}")
s=s.replace("if(!img||!entry)return;", "if(!img||!entry){this.fallback(group,id,x,y,size,opacity);return;}")
s=s.replace(" drawBackground(g){", """ fallback(group,id,x,y,size,opacity=1){const c=this.ctx;c.save();c.globalAlpha=opacity;c.translate(x,y);c.shadowBlur=12;c.shadowColor=group==='enemies'?'#bb85ff':'#62eaff';c.fillStyle=group==='enemies'?'#4c336d':group==='bosses'?'#6e2f6d':'#1d658a';c.strokeStyle='#e0f7ff';c.lineWidth=3;c.beginPath();c.arc(0,-size*.27,size*.26,0,Math.PI*2);c.fill();c.stroke();c.font=`bold ${Math.floor(size*.25)}px system-ui`;c.fillStyle='white';c.textAlign='center';c.fillText('✦',0,-size*.2);c.restore()}
 drawBackground(g){""")
s=s.replace(" // telegraph warnings stay visible above terrain and below entities", """ // Interactive WebP field props: proximity collection, scan bonuses and rewards.
 for(const o of g.props||[]){if(!visible(o,100))continue;const art=this.assets.images?.[`assets/props/${o.type}.webp`];const x=sx(o.x),y=sy(o.y)+Math.sin(g.elapsed*2.7+o.seed)*5;const sz=o.type==='portal'?90:57;c.save();c.translate(x,y);c.shadowColor=o.type==='healing'?'#8cffb6':'#80daff';c.shadowBlur=17;c.globalAlpha=Math.min(1,o.ttl/3);if(art)c.drawImage(art,-sz/2,-sz*.83,sz,sz);else{c.fillStyle='#6fe8ff';c.beginPath();c.arc(0,0,15,0,6.28);c.fill()}c.restore()}
 // telegraph warnings stay visible above terrain and below entities""")
s=s.replace("x,y,e.boss?e.radius*3.7:e.radius*3.65,e.animT,e.vx<0", "x,y,e.boss?e.radius*3.7:e.radius*3.65,e.animT,e.facing<0")
s=s.replace("this.drawSprite('characters',p.character.id,p.anim,x,y,124,", "this.drawSprite('characters',p.character.id,p.anim,x,y,148,")
s=s.replace(" // slim world-space player aim ring", """ if(g.scanTimer>0){c.save();c.translate(w/2,h/2);c.strokeStyle='#70f7e7ad';c.lineWidth=2;c.setLineDash([6,13]);c.beginPath();c.arc(0,0,75+6*Math.sin(g.elapsed*8),0,6.283);c.stroke();c.restore()}
 // slim world-space player aim ring""")
r.write_text(s)
css=p/'css/ui.css';s=css.read_text();s+='\n/* v2: high-resolution portraits & tactile scan ability */\n.char-card img{height:150px;width:100%;max-width:190px;object-fit:contain;transition:transform .18s ease,filter .18s ease;filter:drop-shadow(0 14px 15px #050e24b0)}.char-card:hover img,.char-card.selected img{transform:scale(1.07) translateY(-3px);filter:drop-shadow(0 9px 16px #3de3fa88)}.char-card{min-height:246px}.action-scan{border-color:#95e9c6;background:radial-gradient(circle at 25% 20%,#68d6b3,#166d7c 52%,#17324f);min-width:65px;min-height:65px}.char-card img{pointer-events:none}@media(max-width:760px){.char-card{min-height:185px}.char-card img{height:105px;max-width:100%}.action-scan{min-width:54px;min-height:54px;font-size:11px}}@media(max-width:390px){#action-buttons{gap:4px;right:5px}.action-scan{min-width:48px;min-height:48px}.action-ult{width:62px;height:62px}}\n'
css.write_text(s)
