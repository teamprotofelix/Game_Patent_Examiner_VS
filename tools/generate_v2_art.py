#!/usr/bin/env python3
"""v2 art bake: image-generated high-detail transparent character art animated with
frame-specific warps, plus vector-rendered HD enemy/boss frames and world props.
Run only when regenerating art; deployment uses baked .webp files.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter,ImageEnhance
import numpy as np,cv2,math,io,ast,json,random,cairosvg
ROOT=Path(__file__).resolve().parents[1]
A=ROOT/'assets'; (A/'portraits').mkdir(exist_ok=True);(A/'props').mkdir(exist_ok=True)
random.seed(48)
manifest=json.loads((A/'atlas.json').read_text())
SOURCE=ROOT/'assets/source/character_lineup.webp'
if not SOURCE.exists():
 # retain original v1 sprites if the optional creation-time reference isn't available
 print('No imagegen source: keeping existing character art'); SOURCE=None
states={'idle':6,'run':8,'attack':6,'dash':6,'hit':4,'skill':8,'victory':6,'death':6}
SZ=384
if SOURCE:
 source=Image.open(SOURCE).convert('RGBA')
 names=['marie','searcher','alchemist']
 for j,name in enumerate(names):
  box=(j*724,0,(j+1)*724,724)
  image=source.crop(box)
  # remove near-transparent edge glow, avoiding checkerboard/halo artifacts
  ar=np.asarray(image).copy(); alpha=ar[:,:,3];ar[:,:,3]=np.where(alpha<5,0,alpha)
  image=Image.fromarray(ar,'RGBA')
  bb=image.getbbox() or (0,0,724,724)
  image=image.crop(bb)
  m=max(image.size)
  bg=Image.new('RGBA',(m,m));bg.alpha_composite(image,((m-image.width)//2,(m-image.height)//2))
  # Portraits remain substantially sharper than tiny in-game thumbnails.
  portrait=bg.resize((680,680),Image.Resampling.LANCZOS)
  portrait.save(A/'portraits'/f'{name}.webp','WEBP',quality=93,method=5)
  base=bg.resize((SZ-46,SZ-46),Image.Resampling.LANCZOS)
  pad=Image.new('RGBA',(SZ,SZ));pad.alpha_composite(base,((SZ-base.width)//2,(SZ-base.height)//2))
  base=np.asarray(pad).copy()
  y,x=np.mgrid[0:SZ,0:SZ].astype('float32')
  frames=[]
  for state,n in states.items():
   for k in range(n):
    phase=(2*math.pi*k/n)
    head=np.maximum(0,1-y/(SZ*.48))
    legs=np.clip((y-SZ*.52)/(SZ*.48),0,1)
    right=np.clip((x-SZ*.42)/(SZ*.45),0,1)
    left=np.clip((SZ*.55-x)/(SZ*.5),0,1)
    torso=np.exp(-((y-SZ*.50)/(SZ*.34))**2)
    dx=np.zeros_like(x);dy=np.zeros_like(y)
    if state=='idle':
     dy+=2.5*math.sin(phase)*torso;dx+=3.4*math.sin(phase+.6)*head
    elif state=='run':
     dy+=6*math.sin(phase*2)*torso
     dx+=9*math.sin(phase)*legs*(left-right)
     dx+=5*math.cos(phase)*head
     dy+=4*math.sin(phase+.5)*legs
    elif state=='attack':
     dx+=22*math.sin(phase)*right*torso
     dy+=12*math.cos(phase)*right*torso
     dx-=4*math.sin(phase)*left
    elif state=='dash':
     dx+=22+5*math.sin(phase)
     dy-=5*math.sin(phase)*torso
    elif state=='hit':
     dx+=9*math.sin(phase)*torso;dy+=3*math.cos(phase)*torso
    elif state=='skill':
     dx+=7*math.sin(phase)*head;dy+=5*math.sin(phase)*torso
    elif state=='victory':
     dy-=6+5*math.sin(phase)
     dx+=7*math.sin(phase)*head
    elif state=='death':
     dy+=6*math.sin(phase)
    warped=cv2.remap(base,(x-dx).astype('float32'),(y-dy).astype('float32'),interpolation=cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT,borderValue=(0,0,0,0))
    frame=Image.fromarray(warped,'RGBA')
    if state=='dash':
     ghost=frame.copy();aa=ghost.getchannel('A').point(lambda a:int(a*.20));ghost.putalpha(aa)
     layer=Image.new('RGBA',(SZ,SZ));layer.alpha_composite(ghost,(-20,0));layer.alpha_composite(frame);frame=layer
    if state=='hit' and k==1:
     flash=Image.new('RGBA',(SZ,SZ),'white');alpha=frame.getchannel('A').point(lambda a:int(a*.23));flash.putalpha(alpha);frame=Image.alpha_composite(frame,flash)
    draw=ImageDraw.Draw(frame,'RGBA')
    if state=='attack':
     a=phase*.65
     b=(245+25*math.sin(phase),178+30*math.cos(phase))
     draw.arc((b[0]-92,b[1]-92,b[0]+92,b[1]+92),-45+k*4,80+k*4,fill=(102,243,255,190),width=8)
    if state=='skill':
     r=120+10*math.sin(phase)
     draw.ellipse((SZ/2-r,SZ/2-r,SZ/2+r,SZ/2+r),outline=(178,112,255,150),width=5)
    if state=='victory' and k%2==0:
     draw.line((110,95,120,78),fill=(255,233,150,200),width=4)
    if state=='death':
     frame=frame.rotate(-min(80,k*16),resample=Image.Resampling.BICUBIC,expand=False,center=(SZ//2,SZ//2))
    # Keep every state inside its atlas cell, including rotated death poses.
    inset=frame.resize((344,344),Image.Resampling.LANCZOS)
    safe=Image.new('RGBA',(SZ,SZ));safe.alpha_composite(inset,(20,20));frames.append(safe)
  cols=8;rows=math.ceil(len(frames)/cols)
  sheet=Image.new('RGBA',(SZ*cols,SZ*rows))
  for i,frame in enumerate(frames):sheet.alpha_composite(frame,((i%cols)*SZ,(i//cols)*SZ))
  sheet.save(A/'characters'/f'{name}.webp','WEBP',quality=87,method=5)
  pos=0;anim={}
  for state,n in states.items():
   anim[state]={'start':pos,'count':n,'fps':14 if state=='run' else 11 if state in ('attack','dash') else 8};pos+=n
  manifest['characters'][name]={'file':f'assets/characters/{name}.webp','size':SZ,'columns':cols,'frames':len(frames),'animations':anim}
  # Also upgrade existing UI art with the same detailed portrait
  portrait.resize((420,420),Image.Resampling.LANCZOS).save(A/'ui'/f'{name}.webp','WEBP',quality=90,method=4)
  print('HD character',name,len(frames),'frames',flush=True)
# Load previous vector helper methods without rerunning the original asset generator.
tree=ast.parse((ROOT/'tools/generate_assets.py').read_text(encoding='utf8'))
subset=ast.Module(body=[node for node in tree.body if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)) and node.name in ['shell','rgba','enemy_svg']],type_ignores=[])
ns={'math':math,'Image':Image,'io':io,'cairosvg':cairosvg}
exec(compile(subset,'<v1-vector-functions>','exec'),ns)
enemy_svg=ns['enemy_svg'];rgba=ns['rgba'];shell=ns['shell']
old=[('slime','slime','#76c9fe'),('ghost','ghost','#c5b6ff'),('bat','bat','#a174f8'),('phantom','ghost','#5b69a9'),('golem','golem','#a7a0a9'),('mage','mage','#aa5bea'),('skeleton','skull','#e0dfd6'),('glitch','glitch','#60e3c4'),('document','book','#e9c4a2'),('gear','gear','#edaf60'),('elite_oracle','mage','#ff718e'),('elite_guard','golem','#f4a24c'),('elite_librarian','book','#f4e5a0'),('elite_wraith','ghost','#e35bea')]
extra=[('audit_spider','#59f7ce'),('timeout_wisp','#8cd9fc'),('citation_mimic','#ffe394'),('syntax_serpent','#ff81cb'),('elite_archivist','#e8b9ff'),('elite_reactor','#ff985f')]
SIZE=256
STATES={'move':6,'attack':5,'hit':4,'death':6}
def custom_svg(name,color,state,k,n):
 phase=k/n*math.tau
 bob=math.sin(phase)*5
 core=f'''<circle cx="120" cy="119" r="55" fill="#172546" stroke="{color}" stroke-width="11"/><circle cx="120" cy="119" r="38" fill="{color}" fill-opacity=".22"/><path d="M96 111 Q108 100 115 118 L109 131 L94 121 Z M131 119 Q145 100 158 112 L146 130 L132 130 Z" fill="#ff7b94"/><circle cx="105" cy="115" r="4" fill="#fff"/><circle cx="144" cy="115" r="4" fill="#fff"/>'''
 if name=='audit_spider':
  body=''.join(f'<path d="M{120+(-1 if q%2 else 1)*32} {110+q*7} Q {36 if q%2 else 210} {15+q*45} {22 if q%2 else 218} {40+q*37}" stroke="{color}" stroke-width="12" fill="none" stroke-linecap="round"/>' for q in range(4))+core+'<path d="M112 76 L120 48 L132 75" fill="none" stroke="#e9ffff" stroke-width="8"/>'
 elif name=='timeout_wisp':
  body=f'<path d="M51 165 Q30 95 78 64 Q115 18 171 62 Q206 115 194 169 L157 149 L132 202 L108 159 L69 202Z" fill="{color}" stroke="#32658e" stroke-width="8"/>'+core+'<path d="M114 76 L129 119 L103 140" stroke="#f6fbff" stroke-width="8" fill="none"/>'
 elif name=='citation_mimic':
  body=f'<path d="M52 67 L127 82 L192 63 L192 184 L124 203 L50 182Z" fill="#f0d6a1" stroke="{color}" stroke-width="9"/><path d="M124 87 L124 202 M68 98 L106 104 M68 124 L106 130 M145 107 L178 100" stroke="#776085" stroke-width="6"/>'+core+'<path d="M88 160 L112 174 L144 158" fill="none" stroke="#a04872" stroke-width="6"/>'
 elif name=='syntax_serpent':
  body=f'<path d="M80 58 Q202 21 196 111 Q190 156 118 150 Q75 160 109 201" stroke="{color}" stroke-width="29" fill="none" stroke-linecap="round"/><path d="M80 60 Q202 25 194 109" stroke="#ffecfc" stroke-width="7" fill="none"/>'+core+'<path d="M134 156 Q119 187 108 204" stroke="#f8c2ee" stroke-width="7" fill="none"/>'
 elif name=='elite_archivist':
  body=f'<path d="M66 59 L171 59 L200 199 L43 198Z" fill="#3a246c" stroke="{color}" stroke-width="9"/><path d="M73 67 L118 11 L170 68Z" fill="#1c1d54" stroke="#ffd397" stroke-width="8"/>'+core+'<rect x="165" y="118" width="60" height="80" rx="8" fill="#d9b7ff" stroke="#5b4d8c" stroke-width="8"/>'
 else:
  body=''.join(f'<rect x="93" y="22" width="54" height="50" rx="15" fill="{color}" stroke="#73455b" stroke-width="6" transform="rotate({i*45} 120 120)"/>' for i in range(8))+core+'<circle cx="122" cy="120" r="29" fill="#ee7546" stroke="#ffeeaa" stroke-width="8"/>'
 if state=='attack':body+=f'<circle cx="120" cy="120" r="105" fill="none" stroke="{color}" stroke-width="5" stroke-dasharray="14 8"/>'
 if state=='hit':body+='<path d="M32 24 L59 50 M50 20 L35 58" stroke="#fffbc4" stroke-width="9"/>'
 if state=='death':body+='<path d="M40 35 L62 54 M61 32 L42 61" stroke="#ffffff" stroke-width="8"/>'
 svg=shell(f'<g transform="translate(0 {bob:.1f}) rotate({math.sin(phase)*4:.1f} 120 120)">{body}</g>')
 return svg
all_enemies=old+extra
for j,(name,*rest) in enumerate(all_enemies):
 color=rest[-1];style=rest[0] if len(rest)==2 else None
 frames=[]
 for state,n in STATES.items():
  for k in range(n):
   svg=enemy_svg(name,style,color,state,k,n) if style else custom_svg(name,color,state,k,n)
   frame=rgba(svg,SIZE)
   frames.append(frame)
 cols=6; sheet=Image.new('RGBA',(SIZE*cols,SIZE*math.ceil(len(frames)/cols)))
 for i,frame in enumerate(frames):sheet.alpha_composite(frame,((i%cols)*SIZE,(i//cols)*SIZE))
 sheet.save(A/'enemies'/f'{name}.webp','WEBP',quality=90,method=3)
 manifest['enemies'][name]={'file':f'assets/enemies/{name}.webp','size':SIZE,'columns':cols,'frames':len(frames),'animations':{'move':{'start':0,'count':6,'fps':10},'attack':{'start':6,'count':5,'fps':11},'hit':{'start':11,'count':4,'fps':8},'death':{'start':15,'count':6,'fps':9}}}
 frames[0].resize((360,360),Image.Resampling.LANCZOS).save(A/'ui'/f'{name}.webp','WEBP',quality=88,method=3)
 print('HD enemy',name,flush=True)
for name,style,color in [('shadow','ghost','#9242ef'),('giant','golem','#faaf56'),('chimera','glitch','#cf61d6')]:
 sz=544; states={'move':8,'attack':8,'hit':4,'death':8};frames=[]
 for st,n in states.items():
  for k in range(n):
   im=rgba(enemy_svg(name,style,color,st,k,n,True),sz)
   draw=ImageDraw.Draw(im,'RGBA')
   a=k/n*math.tau
   # Elaborate, non-flat rune halo/crest over procedural boss shape
   cx=cy=sz//2;rad=195
   for i in range(12):
    t=i*math.tau/12+a*.18
    x=cx+rad*math.cos(t);y=cy+rad*math.sin(t)
    draw.line((cx+175*math.cos(t),cy+175*math.sin(t),x,y),fill=(255,196,116,165),width=4)
   draw.arc((cx-rad,cy-rad,cx+rad,cy+rad),0,360,fill=(255,189,112,170),width=4)
   frames.append(im)
 cols=4; sheet=Image.new('RGBA',(sz*cols,sz*math.ceil(len(frames)/cols)))
 for i,f in enumerate(frames):sheet.alpha_composite(f,((i%cols)*sz,(i//cols)*sz))
 sheet.save(A/'bosses'/f'{name}.webp','WEBP',quality=88,method=3)
 manifest['bosses'][name]={'file':f'assets/bosses/{name}.webp','size':sz,'columns':cols,'frames':len(frames),'animations':{st:{'start':sum(list(states.values())[:i]),'count':n,'fps':11 if st=='attack' else 8} for i,(st,n) in enumerate(states.items())}}
 frames[0].resize((420,420),Image.Resampling.LANCZOS).save(A/'ui'/f'{name}.webp','WEBP',quality=90,method=3)
 print('HD boss',name,flush=True)
# world prop silhouettes, 6 unique interactive objects; alpha WebP 384px
for name,col in [('crystal','#65eafd'),('portal','#b08bff'),('archive','#f7d5a7'),('healing','#7bffb5'),('burst','#ffb0a0'),('warning','#ff587e')]:
 if name=='crystal':
  body=f'<path d="M120 17 L179 89 L155 205 L120 229 L85 205 L62 89Z" fill="{col}" stroke="#f0ffff" stroke-width="9"/><path d="M120 18 L120 228 M65 90 L178 90 M120 18 L178 90 L120 145 L65 90" stroke="#d5f7ff" stroke-width="5" fill="none"/>'
 elif name=='portal':body=f'<ellipse cx="120" cy="120" rx="89" ry="102" fill="none" stroke="{col}" stroke-width="21"/><ellipse cx="120" cy="120" rx="64" ry="79" fill="#5c3fbd" fill-opacity=".45" stroke="#f0d8ff" stroke-width="8"/><path d="M35 120 L202 120 M120 25 L120 216" stroke="#bffaff" stroke-width="6" opacity=".6"/>'
 elif name=='archive':body=f'<path d="M44 60 L118 35 L198 65 L197 199 L120 225 L44 192Z" fill="#556b99" stroke="{col}" stroke-width="11"/><path d="M120 35 L120 225 M62 93 L102 107 M63 127 L100 139 M139 105 L178 95" fill="none" stroke="{col}" stroke-width="9"/><circle cx="120" cy="145" r="17" fill="#84f7ff"/>'
 elif name=='healing':body=f'<path d="M120 207 Q36 164 41 100 Q43 36 95 45 Q112 45 120 66 Q146 30 180 50 Q229 81 191 143Z" fill="{col}" stroke="#eafff1" stroke-width="10"/><path d="M120 84 L120 156 M87 120 L155 120" stroke="#246c66" stroke-width="18"/>'
 elif name=='burst':body=f'<path d="M121 15 L151 82 L222 68 L174 125 L219 184 L146 174 L112 226 L91 163 L20 177 L66 125 L25 67 L102 82Z" fill="{col}" stroke="#fff7c9" stroke-width="9"/>'
 else:body=f'<path d="M120 28 L212 210 L28 210Z" fill="#b11e56" stroke="{col}" stroke-width="11"/><path d="M119 92 L120 157" stroke="#fff" stroke-width="15"/><circle cx="120" cy="185" r="10" fill="#fff"/>'
 im=rgba(shell(f'<circle cx="120" cy="120" r="103" fill="{col}" fill-opacity=".06"/>{body}'),384)
 im.save(A/'props'/f'{name}.webp','WEBP',quality=94,method=4)
print('HD props completed',flush=True)
(A/'atlas.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8')
