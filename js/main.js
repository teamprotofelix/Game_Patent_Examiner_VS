import {GameAudio} from './engine/Audio.js';
import {Renderer} from './engine/Renderer.js';
import {Input} from './engine/Input.js';
import {Game} from './engine/Game.js';
import {GameUI} from './ui/Menus.js';
import {loadSave,recordRun} from './systems/SaveSystem.js';
/** v2: artwork metadata is bundled at build time. No fetch(), ES-module or server required. */
const assets={atlas:globalThis.__GAME_ATLAS__||{characters:{},enemies:{},bosses:{}},images:{},failed:[]};
const status=document.getElementById('loaded-count');
const save=loadSave();const audio=new GameAudio();audio.music=save.settings.music;audio.sfx=save.settings.sfx;
const ui=new GameUI(save,audio);const renderer=new Renderer(document.getElementById('game'),assets);const game=new Game(renderer,audio,ui,save);ui.setGame(game);
const dash=document.getElementById('dash-btn');game.input=new Input(renderer.canvas,dash,()=>game.pause());game.onFinish=(g,won)=>recordRun(save,g,won);
const srcPath=s=>'./'+s.replace(/^\.\//,'');
const mobileTier=window.innerWidth<790||!!window.matchMedia?.('(pointer:coarse)')?.matches||(navigator.deviceMemory&&navigator.deviceMemory<=4);
const inflight=new Set();let started=0,finished=0;
assets.ensure=(path)=>{
 if(!path||assets.images[path]||inflight.has(path)||assets.failed.includes(path))return;
 inflight.add(path);started++;
 const img=new Image();img.decoding='async';
 img.onload=()=>{assets.images[path]=img;inflight.delete(path);finished++;if(finished%5===0||finished===started)status.textContent=`✓ 출격 가능 · 이미지 ${finished}/${started} 준비됨`};
 img.onerror=()=>{assets.failed.push(path);inflight.delete(path);finished++;console.warn('누락된 그림은 대체 렌더링합니다:',path);if(finished===started)status.textContent=`✓ 출격 가능 · 그림 ${assets.failed.length}개 대체 렌더링`};
 img.src=srcPath(path);
};
function loadAssets(){
 const paths=new Set();
 if(mobileTier){
  for(const id of ['marie','searcher','alchemist'])paths.add(`assets/portraits/${id}.webp`);
  paths.add(assets.atlas.characters?.marie?.file);
  for(const id of ['slime','ghost','bat','phantom'])paths.add(assets.atlas.enemies?.[id]?.file);
  for(const id of ['stage1','stage2','stage3'])paths.add(`assets/backgrounds/${id}.webp`);
  for(const id of ['crystal','portal','archive','healing','burst'])paths.add(`assets/props/${id}.webp`);
  // Remaining frames stream on demand on small/mobile devices, reducing GPU memory.
 }else{
  for(const group of ['characters','enemies','bosses'])for(const obj of Object.values(assets.atlas[group]||{}))paths.add(obj.file);
  for(let i=0;i<20;i++)paths.add(`assets/effects/fx_${String(i).padStart(2,'0')}.webp`);
  for(const stage of ['stage1','stage2','stage3'])paths.add(`assets/backgrounds/${stage}.webp`);
  for(const id of ['marie','searcher','alchemist'])paths.add(`assets/portraits/${id}.webp`);
  for(const id of ['crystal','portal','archive','healing','burst','warning'])paths.add(`assets/props/${id}.webp`);
 }
 status.textContent='✓ 출격 준비 완료 · 그림은 자동 로딩';
 for(const path of paths)assets.ensure(path);
}
loadAssets();
try{if('serviceWorker'in navigator&&(location.protocol==='https:'||location.hostname==='localhost'||location.hostname==='127.0.0.1'))window.addEventListener('load',()=>navigator.serviceWorker.register('./service-worker.js',{scope:'./',updateViaCache:'none'}).catch(e=>console.warn('PWA 미지원',e)))}catch(_e){}
window.__GAME_TEST__={game,ui,assets,ready:()=>true};
