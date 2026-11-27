#!/usr/bin/env python3
"""Deterministic ES modules -> file:// compatible classic JS build.
No dependency: keeps full modular sources but deploys one ordinary script.
"""
import json,re,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
modules=['data/characters.js','data/weapons.js','data/enemies.js','data/stages.js','data/patent-cases.js','js/systems/SaveSystem.js','js/engine/Audio.js','js/engine/Input.js','js/engine/Renderer.js','js/engine/Game.js','js/ui/Menus.js','js/main.js']
source=["/* PATENT EXAMINER: REJECTION LEGION v2.0 · original source in /js + /data */","(()=>{ 'use strict';",'const __GAME_ATLAS__ = '+json.dumps(json.loads((ROOT/'assets/atlas.json').read_text(encoding='utf8')),ensure_ascii=False,separators=(',',':'))+';', 'globalThis.__GAME_ATLAS__=__GAME_ATLAS__;']
for name in modules:
 code=(ROOT/name).read_text(encoding='utf8')
 code=re.sub(r'^\s*import\s+.+?\s+from\s+[\'\"].+?[\'\"];?\s*$', '', code,flags=re.M)
 code=re.sub(r'\bexport\s+(?=(?:const|function|class|let|async)\b)', '', code)
 source.append('// FILE: '+name+'\n'+code)
source.append('})();')
result='\n'.join(source)
path=ROOT/'js/game.bundle.js';path.write_text(result,encoding='utf8')
print('Wrote',path,len(result),'bytes')
