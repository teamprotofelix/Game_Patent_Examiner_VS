#!/usr/bin/env python3
"""Original procedural transparent frame artwork + processing licensed AI-generated scene art.
Uses CairoSVG and Pillow, retains playable release atlases with metadata."""
import math, io, json, os, random, shutil, glob
from PIL import Image, ImageDraw, ImageFilter, ImageOps
import cairosvg
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A=os.path.join(ROOT,'assets')
random.seed(31)
def rgba(svg,sz):
    raw=cairosvg.svg2png(bytestring=svg.encode('utf-8'),output_width=sz,output_height=sz)
    return Image.open(io.BytesIO(raw)).convert('RGBA')
def shell(body,sz=240):
 return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{sz}" height="{sz}" viewBox="0 0 240 240"><defs>
 <linearGradient id="coat" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#ffffff"/><stop offset=".55" stop-color="#e6f6ff"/><stop offset="1" stop-color="#89aaca"/></linearGradient>
 <linearGradient id="face" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#fff7e8"/><stop offset="1" stop-color="#f0b9a3"/></linearGradient>
 <linearGradient id="metal" x1="0" x2="1" y1="0" y2="1"><stop stop-color="#fff8ce"/><stop offset=".48" stop-color="#e7af4d"/><stop offset="1" stop-color="#76538d"/></linearGradient>
 <linearGradient id="energy" x1="0" x2="1"><stop stop-color="#e5ffff"/><stop offset=".45" stop-color="#37eaff"/><stop offset="1" stop-color="#4c76fa"/></linearGradient>
 <linearGradient id="violet" x1="0" x2="1" y1="0" y2="1"><stop stop-color="#efd9ff"/><stop offset=".6" stop-color="#ad6af7"/><stop offset="1" stop-color="#5b37a2"/></linearGradient>
 <radialGradient id="shine"><stop stop-color="#fff" stop-opacity=".75"/><stop offset="1" stop-color="#44e9ff" stop-opacity="0"/></radialGradient>
 </defs>{body}</svg>'''
STATES={'idle':6,'run':8,'attack':6,'dash':6,'hit':4,'skill':8,'victory':6,'death':6}
CHARS=[('marie','#403047','#31dffa','#a871ff'),('searcher','#bccfe7','#50d3ff','#e8be57'),('alchemist','#e8a2dc','#d98aff','#ffc76b')]
def character_svg(kind,st,f,total):
 idx=[c[0] for c in CHARS].index(kind); _,hair,magic,secondary=CHARS[idx]
 phase=f/total*2*math.pi
 idle=math.sin(phase)*2.0
 run=st=='run'; moving=math.sin(phase)*(23 if run else 4)
 tilt= 15 if st=='dash' else (70 if st=='death' else (-9 if st=='hit' else (7*math.sin(phase) if st=='attack' else 0)))
 off= 4*math.sin(phase) if run else idle
 wiggle=9*math.sin(phase)
 sword=kind=='marie'; drone=kind=='searcher'; alch=kind=='alchemist'
 glow=magic
 arm= -55 if st in ['attack','skill','victory'] else (30 if st=='dash' else 9+wiggle*.3)
 if st=='attack':arm=-60+40*math.cos(phase)
 if st=='skill':arm=-45+12*math.sin(phase)
 if st=='victory':arm=-90
 handgear=''
 if sword:
  handgear=f'''<g transform="rotate({-35 if st=='attack' else 12} 170 142)"><path d="M166 138 L196 70 L207 45 L213 83 L176 143 Z" fill="url(#energy)" stroke="{glow}" stroke-width="3"/><path d="M181 118 L207 66" stroke="#ffffff" stroke-width="2"/><path d="M151 147 L188 137" stroke="url(#metal)" stroke-width="8" stroke-linecap="round"/><circle cx="169" cy="141" r="6" fill="#ffffff" stroke="{glow}" stroke-width="3"/></g>'''
 elif drone:
  handgear=f'''<g><path d="M155 135 L195 112 L206 124 L173 155 Z" fill="#23314d" stroke="#e4c675" stroke-width="4"/><path d="M186 118 L216 101" stroke="{glow}" stroke-width="6" stroke-linecap="round"/><circle cx="200" cy="85" r="17" fill="#19335b" stroke="{glow}" stroke-width="4"/><circle cx="200" cy="85" r="8" fill="#c4faff"/><path d="M174 82 L225 82" stroke="#e2e7ff" stroke-width="3"/></g>'''
 else:
  handgear=f'''<g><circle cx="191" cy="116" r="22" fill="none" stroke="{glow}" stroke-width="4" stroke-dasharray="6 3"/><path d="M191 91 L214 130 L168 130 Z" fill="none" stroke="#ffe9a4" stroke-width="3"/><circle cx="191" cy="116" r="10" fill="url(#violet)"/><circle cx="191" cy="116" r="5" fill="#f4c6ff"/></g>'''
 # all limbs have actual varying angles, layered, standard fixed anchor/feet
 eye='#b26fff' if idx==0 else ('#3b9fee' if idx==1 else '#b06abf')
 face_details='''<path d="M95 101 Q104 95 114 101" fill="none" stroke="#594052" stroke-width="3" stroke-linecap="round"/><path d="M127 101 Q135 95 143 102" fill="none" stroke="#594052" stroke-width="3" stroke-linecap="round"/>'''
 body=f'''<ellipse cx="119" cy="222" rx="49" ry="8" fill="#05152d" opacity=".36"/>
 <g transform="translate(0 {off:.2f}) rotate({tilt:.2f} 120 159)">
 <!-- rear hair --> <path d="M73 99 Q51 78 72 45 Q96 10 143 33 Q169 43 170 79 Q184 113 175 169 Q152 152 144 129 Q105 148 70 170 Q83 123 73 99Z" fill="{hair}" stroke="#23233f" stroke-width="3.5"/>
 <path d="M90 51 Q102 33 125 37" fill="none" stroke="#ffffff" stroke-opacity=".4" stroke-width="5"/>
 <!-- rear arms --> <g transform="rotate({-moving*.42:.2f} 100 148)"><path d="M99 143 L63 174" fill="none" stroke="#23385e" stroke-width="20" stroke-linecap="round"/><path d="M100 144 L66 166" stroke="url(#coat)" stroke-width="14" stroke-linecap="round"/><circle cx="63" cy="173" r="8" fill="url(#face)"/></g>
 <!-- legs --> <g transform="rotate({moving:.2f} 111 177)"><path d="M109 172 L106 206" stroke="#1a213a" stroke-width="19" stroke-linecap="round"/><path d="M104 202 L88 218 Q85 222 97 224 L115 220 L116 206" fill="#23395d" stroke="#e9bf70" stroke-width="3"/></g>
 <g transform="rotate({-moving:.2f} 137 174)"><path d="M137 172 L150 204" stroke="#1d2948" stroke-width="19" stroke-linecap="round"/><path d="M146 202 L134 218 Q138 223 161 222 L161 212 L158 201" fill="#243455" stroke="#e9bf70" stroke-width="3"/></g>
 <!-- coat skirt --> <path d="M107 130 Q122 130 145 132 L166 188 Q134 203 91 187Z" fill="url(#coat)" stroke="#2a3c61" stroke-width="4"/><path d="M99 183 L162 187" stroke="{secondary}" stroke-width="5"/>
 <!-- chest --> <path d="M99 124 Q120 114 146 123 L152 169 Q122 181 97 167Z" fill="#e4f5ff" stroke="#35415c" stroke-width="4"/><path d="M106 130 L124 146 L140 129" fill="#22395e" stroke="{secondary}" stroke-width="2"/><path d="M121 140 L128 168" stroke="{glow}" stroke-width="4"/>
 <!-- sleeve & active arm --> <g transform="rotate({arm:.2f} 142 137)"><path d="M142 138 L173 154" fill="none" stroke="#263857" stroke-width="22" stroke-linecap="round"/><path d="M142 138 L168 150" fill="none" stroke="url(#coat)" stroke-width="16" stroke-linecap="round"/><path d="M159 144 L173 154" stroke="{secondary}" stroke-width="5"/><circle cx="174" cy="155" r="8" fill="url(#face)"/>{handgear}</g>
 <!-- neck --> <path d="M117 107 L117 133 L135 133 L136 110" fill="url(#face)" stroke="#634656" stroke-width="2"/>
 <!-- head & ears --> <ellipse cx="120" cy="84" rx="47" ry="47" fill="url(#face)" stroke="#483147" stroke-width="3.5"/><ellipse cx="161" cy="92" rx="7" ry="11" fill="url(#face)"/>
 <!-- hair silhouette --> <path d="M72 91 Q65 60 85 40 Q108 19 139 31 Q169 39 166 89 L154 73 L147 55 Q125 74 92 65 L79 101 Z" fill="{hair}" stroke="#3b2c47" stroke-width="3"/>
 <path d="M82 55 Q111 34 151 45" stroke="#ffffff" stroke-opacity=".32" stroke-width="5" fill="none"/>
 <!-- eyes --> <ellipse cx="112" cy="91" rx="7" ry="11" fill="white"/><ellipse cx="140" cy="90" rx="7" ry="11" fill="white"/><ellipse cx="114" cy="92" rx="4.5" ry="9" fill="{eye}"/><ellipse cx="142" cy="91" rx="4.5" ry="9" fill="{eye}"/><circle cx="116" cy="87" r="2.6" fill="white"/><circle cx="144" cy="86" r="2.6" fill="white"/>
 <path d="M106 79 L119 81 M135 79 L148 78" stroke="#33243c" stroke-width="3" stroke-linecap="round"/><path d="M125 108 Q130 112 136 108" stroke="#aa5773" fill="none" stroke-width="2"/>
 <ellipse cx="98" cy="108" rx="8" ry="3" fill="#ff9ebc" opacity=".42"/><ellipse cx="151" cy="107" rx="8" ry="3" fill="#ff9ebc" opacity=".42"/>
 <!-- badge --> <path d="M112 138 L130 137 L127 156 L115 155Z" fill="#0f4b75" stroke="#e7bf62" stroke-width="2"/><circle cx="122" cy="144" r="4" fill="{glow}"/>
 '''
 if idx==0:
  body+='''<path d="M96 37 L104 27 L117 37" fill="#edc46d" stroke="#704d4c" stroke-width="2"/><path d="M153 52 L165 39 L167 66" fill="#4b77aa" stroke="#deba67" stroke-width="2"/>'''
 if idx==1:
  body+='''<circle cx="129" cy="31" r="16" fill="#1f476a" stroke="#d5ae61" stroke-width="4"/><circle cx="129" cy="31" r="8" fill="#94f7ff"/><path d="M93 92 Q121 99 149 91" stroke="#4b85ae" stroke-width="2" fill="none"/>'''
 if idx==2:
  body+='''<path d="M78 52 Q96 7 136 17 Q169 18 180 53Z" fill="#34244c" stroke="#c99856" stroke-width="5"/><path d="M114 24 L126 4 L136 24" fill="#7746ab" stroke="#e9ca8f" stroke-width="3"/><circle cx="129" cy="25" r="7" fill="#eb9cf8"/>'''
 if st=='skill':body+=f'<circle cx="121" cy="148" r="68" fill="none" stroke="{glow}" stroke-width="4" opacity=".75" stroke-dasharray="19 12"/><circle cx="122" cy="146" r="83" fill="none" stroke="{secondary}" stroke-width="2" opacity=".5"/>'
 if st=='dash':body+=f'<path d="M34 166 L74 142 M24 189 L78 173" stroke="{glow}" stroke-width="6" opacity=".7" stroke-linecap="round"/>'
 if st=='attack':body+=f'<path d="M192 60 Q231 130 196 186" stroke="{glow}" stroke-width="8" fill="none" opacity=".74"/>'
 if st=='hit':body+='<path d="M62 42 L74 54 M72 39 L59 58" stroke="#ff727a" stroke-width="6"/>'
 if st=='victory':body+=f'<path d="M55 50 l-4 -12 M65 43 l10 -12 M175 40 l8 -12" stroke="{secondary}" stroke-width="5"/>'
 body+='</g>'
 return shell(f'<g transform="translate(120 172) scale(.77) translate(-120 -172)">{body}</g>')
def _animmeta(states):
 d={};i=0
 for s,n in states.items(): d[s]={'start':i,'count':n,'fps':12 if s=='run' else (11 if s in ('attack','dash') else 8)};i+=n
 return d
def atlas(frames,size,columns,out,states):
 rows=math.ceil(len(frames)/columns)
 sheet=Image.new('RGBA',(size*columns,size*rows))
 info={};pos=0
 for st,cnt in states.items():
  info[st]={'start':pos,'count':cnt,'fps':12 if st=='run' else (11 if st in ('attack','dash') else 8)}
  pos+=cnt
 for j,im in enumerate(frames):sheet.alpha_composite(im,((j%columns)*size,(j//columns)*size))
 sheet.save(out,'WEBP',quality=78,method=2)
 return {'file':os.path.relpath(out,ROOT).replace('\\','/'),'size':size,'columns':columns,'frames':len(frames),'animations':info}
manifest={'characters':{},'enemies':{},'bosses':{},'icons':{}}
for kind,*_ in CHARS:
 path=f'{A}/characters/{kind}.webp'
 if os.path.exists(path):
  print('reuse character',kind,flush=True); manifest['characters'][kind]= {'file':os.path.relpath(path,ROOT).replace('\\','/'),'size':240,'columns':8,'frames':sum(STATES.values()),'animations':_animmeta(STATES)};continue
 frames=[rgba(character_svg(kind,s,f,n),240) for s,n in STATES.items() for f in range(n)]
 manifest['characters'][kind]=atlas(frames,240,8,path,STATES)
 print('character',kind,len(frames),flush=True)
ENEMIES=[('slime','slime','#76c9fe'),('ghost','ghost','#c5b6ff'),('bat','bat','#a174f8'),('phantom','ghost','#5b69a9'),('golem','golem','#a7a0a9'),('mage','mage','#aa5bea'),('skeleton','skull','#e0dfd6'),('glitch','glitch','#60e3c4'),('document','book','#e9c4a2'),('gear','gear','#edaf60'),('elite_oracle','mage','#ff718e'),('elite_guard','golem','#f4a24c'),('elite_librarian','book','#f4e5a0'),('elite_wraith','ghost','#e35bea')]
def enemy_svg(name,style,color,st,f,n,boss=False):
 phase=f/n*2*math.pi
 bob=math.sin(phase)*5
 angry=(st in ('attack','cast'))
 fade=.5 if st=='death' else 1
 scale=.85+(.09 if angry else (0.06*math.sin(phase)))
 if style=='slime':
  shape=f'''<path d="M55 177 Q34 163 51 118 Q65 86 85 87 Q93 50 126 64 Q168 55 182 105 Q210 119 193 164 Q190 186 161 189 L82 190 Q66 189 55 177Z" fill="{color}" stroke="#2a416f" stroke-width="6"/><path d="M74 115 Q95 90 124 97" fill="none" stroke="#fff" stroke-opacity=".6" stroke-width="9"/>'''
 elif style=='ghost':
  shape=f'''<path d="M48 172 Q32 91 84 66 Q124 43 165 70 Q206 98 193 178 L170 160 L146 189 L119 163 L87 192 L65 157Z" fill="{color}" stroke="#443369" stroke-width="7"/><path d="M64 124 Q61 73 116 67" fill="none" stroke="#fff" stroke-opacity=".5" stroke-width="9"/>'''
 elif style=='bat':
  flap=int(10*math.sin(phase))
  shape=f'''<path d="M114 118 Q74 {48+flap} 25 71 L41 99 L21 123 L69 125 L73 149 L110 144 Q160 {53+flap} 213 76 L199 100 L219 123 L173 134 L159 150Z" fill="{color}" stroke="#342253" stroke-width="7"/><path d="M108 101 L122 68 L140 97Z" fill="#40355a"/><ellipse cx="124" cy="134" rx="31" ry="39" fill="#353458" stroke="{color}" stroke-width="6"/>'''
 elif style=='golem':
  shape=f'''<path d="M80 77 L104 54 L142 64 L166 82 L175 142 L157 181 L94 190 L69 143Z" fill="{color}" stroke="#49435e" stroke-width="10"/><path d="M77 106 L34 118 L48 162 L79 148 M168 108 L211 120 L200 165 L168 148" fill="{color}" stroke="#49435e" stroke-width="11"/><path d="M103 60 L121 117 L109 160 M160 104 L122 117 L141 181" stroke="#fff4c9" stroke-width="4" fill="none"/>'''
 elif style=='mage':
  shape=f'''<path d="M83 97 Q121 67 163 98 L176 181 L61 182Z" fill="{color}" stroke="#362551" stroke-width="8"/><path d="M63 111 L115 24 L181 114Z" fill="#393155" stroke="{color}" stroke-width="7"/><path d="M46 117 L194 117" stroke="#2c2747" stroke-width="12"/><path d="M116 49 L127 70 L145 73 L132 88" fill="none" stroke="#fff3bc" stroke-width="5"/>'''
 elif style=='skull':
  shape=f'''<path d="M71 96 Q65 47 120 43 Q174 45 175 103 L155 147 L157 177 L92 178 L91 144Z" fill="{color}" stroke="#51566a" stroke-width="8"/><path d="M102 143 L100 169 M118 146 L118 169 M137 144 L137 170" stroke="#525a6a" stroke-width="6"/>'''
 elif style=='glitch':
  shape=f'''<path d="M61 75 L124 45 L190 85 L186 173 L128 198 L55 159Z" fill="{color}" stroke="#233f4c" stroke-width="7"/><path d="M49 102 L172 94 M79 141 L214 135 M55 169 L158 160" stroke="#e96fea" stroke-width="7"/><path d="M81 62 L145 191" stroke="#153b48" stroke-width="7"/>'''
 elif style=='book':
  shape=f'''<path d="M55 70 L127 85 L192 65 L192 182 L127 191 L53 178Z" fill="{color}" stroke="#604855" stroke-width="8"/><path d="M128 86 L127 190" stroke="#6c5e73" stroke-width="6"/><path d="M71 103 L112 112 M71 126 L110 135 M145 114 L178 107 M145 137 L182 131" stroke="#836678" stroke-width="4"/>'''
 else:
  teeth=''.join(f'<rect x="{x}" y="{y}" width="24" height="42" rx="5" fill="{color}" stroke="#66506d" stroke-width="5" transform="rotate({i*45} 120 120)"/>' for i,(x,y) in enumerate([(108,24)]*8))
  shape=f'''{teeth}<circle cx="120" cy="120" r="62" fill="{color}" stroke="#67526a" stroke-width="8"/><circle cx="120" cy="120" r="29" fill="#343653" stroke="#ffd698" stroke-width="7"/>'''
 eyes=f'''<path d="M81 115 Q97 102 110 120 L106 136 L84 131Z" fill="#231a3e"/><path d="M131 120 Q147 103 162 115 L157 132 L136 136Z" fill="#231a3e"/><circle cx="99" cy="122" r="7" fill="#ff627d"/><circle cx="146" cy="122" r="7" fill="#ff627d"/>'''
 sparkle=f'''<circle cx="89" cy="120" r="3" fill="#fff"/><circle cx="137" cy="119" r="3" fill="#fff"/>'''
 if st=='hit':sparkle+='<path d="M53 49 l-12 -18 M53 49 l14 -19" stroke="#fff58b" stroke-width="8"/>'
 if st=='death':sparkle+='<path d="M63 94 l30 -16 M90 79 l-26 18" stroke="#f8fcff" stroke-width="6"/>'
 magic= f'<circle cx="122" cy="123" r="105" stroke="{color}" fill="none" stroke-dasharray="16 9" stroke-width="4" opacity=".7"/>' if angry else ''
 return shell(f'<g opacity="{fade}" transform="translate(120 {120+bob:.1f}) scale({scale:.2f}) translate(-120 -120)">{shape}{eyes}{sparkle}{magic}</g>')
for name,style,col in ENEMIES:
 states={'move':6,'attack':4,'hit':3,'death':6}
 path=f'{A}/enemies/{name}.webp'
 if os.path.exists(path):
  print('reuse enemy',name,flush=True);manifest['enemies'][name]={'file':os.path.relpath(path,ROOT).replace('\\','/'),'size':192,'columns':6,'frames':sum(states.values()),'animations':_animmeta(states)};continue
 frames=[rgba(enemy_svg(name,style,col,st,f,n),192) for st,n in states.items() for f in range(n)]
 manifest['enemies'][name]=atlas(frames,192,6,path,states)
 print('enemy',name,flush=True)
BOSSES=[('shadow','ghost','#9242ef'),('giant','golem','#faaf56'),('chimera','glitch','#cf61d6')]
for name,style,col in BOSSES:
 states={'move':8,'attack':8,'hit':4,'death':8}
 frames=[]
 for st,n in states.items():
  for f in range(n):
   im=rgba(enemy_svg(name,style,col,st,f,n,True),400)
   # further detailing and crown
   d=ImageDraw.Draw(im)
   # aura/edge crest, free of artificial solid backgrounds
   pts=[(200+int(133*math.cos(i*math.pi/6)),200+int(133*math.sin(i*math.pi/6))) for i in range(12)]
   d.line(pts+[pts[0]],fill=(255,190,110,160) if name!='shadow' else (173,106,255,170),width=4,joint='curve')
   frames.append(im)
 path=f'{A}/bosses/{name}.webp';manifest['bosses'][name]=atlas(frames,400,4,path,states)
 print('boss',name,flush=True)
# Generated splash and backdrop artwork. The original image-gen compositions are documented in README.
sources={
 'title':'a_dynamic_high_detail_anime_style_game_key_art_il.png',
 'stage1':'a_dynamic_highly_detailed_anime_style_sci_fi_fant.png',
 'stage2':'a_highly_detailed_cinematic_anime_style_fantasy_s.png',
 'stage3':'a_highly_detailed_cinematic_anime_style_sci_fi_fa.png',
 'boss_shadow':'a_dynamic_highly_detailed_anime_style_sci_fi_fant.png',
 'boss_giant':'a_highly_detailed_cinematic_anime_style_fantasy_s.png',
 'boss_chimera':'a_highly_detailed_cinematic_anime_style_sci_fi_fa.png',
 'ending':'a_high_detail_anime_game_promotional_collage_scree.png'}
for dest,source in sources.items():
 src='/mnt/data/'+source
 if not os.path.exists(src):continue
 im=Image.open(src).convert('RGB')
 if dest.startswith('stage'):
  im=Image.blend(im,Image.new('RGB',im.size,(10,17,42)),.52).filter(ImageFilter.GaussianBlur(1.0))
  # background intended as distant environmental imagery under highly legible play layer
 else: im=im
 im.save(f'{A}/backgrounds/{dest}.webp','WEBP',quality=83,method=2)
# Animated particle glyphs and skill icons as transparent WebP, all generated with art, not emoji.
weapons=[('blade','#43eaff','sword'),('laser','#49a9ff','beam'),('chain','#ffba54','chain'),('shield','#67f6ef','shield'),('drone','#9d9dff','drone'),('markush','#ed86ff','molecule'),('dash','#b8cafa','arrow'),('ultimate','#ffc76a','sun'),('heart','#ff799a','heart'),('xp','#83fafa','diamond'),('crit','#ffe3a2','burst'),('speed','#c9ff9f','arrow'),('power','#ffb27a','sun'),('range','#a7baff','beam'),('projectile','#fb99cd','burst'),('heal','#9cffc8','heart'),('coins','#ffe6a4','sun'),('boss','#b58aff','shield')]
def icon_svg(c,typ):
 paths={
 'sword':'<path d="M60 154 L145 49 L169 38 L161 69 L84 163 Z"/><path d="M47 151 L91 177 M62 167 L52 194"/>',
 'beam':'<path d="M30 124 L197 58 L139 120 L204 143 L48 173 L115 126Z"/>',
 'chain':'<ellipse cx="76" cy="115" rx="45" ry="21" transform="rotate(-30 76 115)"/><ellipse cx="150" cy="115" rx="45" ry="21" transform="rotate(-30 150 115)"/>',
 'shield':'<path d="M120 27 L190 60 L178 158 L120 203 L61 157 L49 60 Z"/>',
 'drone':'<circle cx="120" cy="120" r="45"/><circle cx="120" cy="120" r="17"/><path d="M32 62 L95 95 M208 62 L145 95 M32 182 L95 146 M208 182 L145 146"/>',
 'molecule':'<circle cx="120" cy="120" r="16"/><circle cx="55" cy="74" r="18"/><circle cx="185" cy="79" r="18"/><circle cx="175" cy="176" r="18"/><circle cx="63" cy="180" r="18"/><path d="M108 110 L69 86 M133 110 L170 92 M135 137 L163 162 M107 133 L79 167"/>',
 'diamond':'<path d="M120 18 L205 117 L120 217 L35 117 Z"/>',
 'heart':'<path d="M120 202 Q22 139 30 84 Q35 22 92 43 Q111 53 120 72 Q139 34 176 42 Q224 54 208 108 Q188 158 120 202Z"/>',
 'sun':'<circle cx="120" cy="120" r="43"/><path d="M120 12 L120 61 M120 180 L120 226 M12 120 L63 120 M177 120 L230 120 M40 40 L79 80 M160 160 L202 202 M200 40 L162 80 M80 161 L39 201"/>',
 'arrow':'<path d="M37 128 L157 128 L125 79 L211 123 L125 172 L157 144 L37 144Z"/>',
 'burst':'<path d="M122 13 L146 86 L220 57 L183 115 L223 164 L149 158 L117 228 L97 162 L29 187 L65 118 L26 60 L102 87Z"/>'}
 return shell(f'''<circle cx="120" cy="120" r="97" fill="#111b41" stroke="{c}" stroke-width="7" opacity=".90"/><circle cx="120" cy="120" r="83" fill="none" stroke="#fff" stroke-opacity=".16" stroke-width="2"/><g fill="none" stroke="{c}" stroke-width="13" stroke-linejoin="round" stroke-linecap="round">{paths[typ]}</g><circle cx="73" cy="65" r="13" fill="#ffffff" opacity=".21"/>''')
for name,col,typ in weapons:
 path=f'{A}/icons/{name}.webp';rgba(icon_svg(col,typ),240).save(path,'WEBP',quality=90,method=2)
 manifest['icons'][name]=os.path.relpath(path,ROOT).replace('\\','/')
# PWA icons using title art cropped and bordered for clarity.
title=Image.open(f'{A}/backgrounds/title.webp').convert('RGB');w,h=title.size
for n in (192,512):
 side=min(w,h); sub=title.crop(((w-side)//2,0,(w+side)//2,side)).resize((n,n),Image.Resampling.LANCZOS)
 mask=Image.new('L',(n,n),0);dd=ImageDraw.Draw(mask);dd.rounded_rectangle((0,0,n-1,n-1),radius=n//6,fill=255)
 out=Image.new('RGBA',(n,n));out.paste(sub,(0,0),mask)
 out.save(f'{A}/icons/pwa-{n}.png',optimize=True)
with open(f'{A}/atlas.json','w',encoding='utf8') as f:json.dump(manifest,f,ensure_ascii=False,indent=2)
print('DONE',sum(len(v) for v in manifest.values()),flush=True)
