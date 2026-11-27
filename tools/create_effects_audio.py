#!/usr/bin/env python3
"""Procedural original impact WebP and WAV samples (packaged and played in-game)."""
import math,random,io,wave,os
from PIL import Image
import cairosvg
B=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
random.seed(7)
colors=['#56eaff','#9bb7ff','#ed9aff','#f8cb85','#78f4cb','#ff91b7','#c8b0ff','#eafcff']
for i in range(20):
 c=colors[i%len(colors)];angs=8+i%6;n=math.pi*2/angs
 pts=' '.join(f'{120+(92 if k%2==0 else 42)*math.cos(k*n/2):.1f},{120+(92 if k%2==0 else 42)*math.sin(k*n/2):.1f}' for k in range(angs*2))
 adorn=''.join(f'<path d="M120 120 L{120+84*math.cos(k*n):.2f} {120+84*math.sin(k*n):.2f}" stroke="{c}" stroke-width="{2+i%4}" opacity=".7"/>' for k in range(angs))
 svg=f'''<svg xmlns="http://www.w3.org/2000/svg" width="240" height="240"><defs><radialGradient id="g"><stop stop-color="#ffffff" stop-opacity=".9"/><stop offset=".30" stop-color="{c}" stop-opacity=".75"/><stop offset="1" stop-color="{c}" stop-opacity="0"/></radialGradient></defs><circle cx="120" cy="120" r="95" fill="url(#g)"/>{adorn}<polygon points="{pts}" stroke="{c}" stroke-width="6" fill="none" opacity=".86"/><circle cx="120" cy="120" r="{21+i%8*2}" stroke="white" stroke-width="3" fill="none" opacity=".75"/></svg>'''
 data=cairosvg.svg2png(bytestring=svg.encode());im=Image.open(io.BytesIO(data)).convert('RGBA');im.save(f'{B}/assets/effects/fx_{i:02d}.webp','WEBP',quality=90,method=2)
print('20 effects created')
sounds=['blade','laser','chain','shield','drone','markush','hit','critical','xp','level','upgrade','boss','danger','dash','ultimate','death','win','click']
freqs=[610,950,330,170,510,390,160,820,1050,560,700,95,230,400,220,280,680,450]
for j,(name,freq) in enumerate(zip(sounds,freqs)):
 rate=16000;dur=.12+(j%5)*.034;length=int(rate*dur);data=bytearray()
 for n in range(length):
  t=n/rate;env=(1-math.exp(-t*200))*math.exp(-t*(14 if j%3 else 9));v=(math.sin(2*math.pi*freq*t*(1+(j%4)*.19*t))+0.28*math.sin(2*math.pi*freq*2.01*t))*env*.45
  value=max(-32768,min(32767,int(32767*v)));data.extend(value.to_bytes(2,'little',signed=True))
 with wave.open(f'{B}/assets/audio/{name}.wav','wb') as wav:wav.setnchannels(1);wav.setsampwidth(2);wav.setframerate(rate);wav.writeframes(data)
print(len(sounds),'original WAV effects created')
