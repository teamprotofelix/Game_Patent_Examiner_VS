#!/usr/bin/env python3
"""Release asset audit: references, dimensions, valid RGBA frames, edge clipping, alpha and size."""
import json,os,sys,glob
from PIL import Image
ROOT=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
atlas=json.load(open(os.path.join(ROOT,'assets','atlas.json'),encoding='utf8'))
errors=[];warnings=[];counts={};total=0
for group in ['characters','enemies','bosses']:
 counts[group]=0
 for name,item in atlas[group].items():
  path=os.path.join(ROOT,item['file']);counts[group]+=1
  if not os.path.isfile(path):errors.append('Missing '+path);continue
  try:im=Image.open(path).convert('RGBA')
  except Exception as exc:errors.append(f'{name}: invalid WebP {exc}');continue
  sz=item['size'];cols=item['columns'];count=item['frames'];rows=(count+cols-1)//cols
  if im.size!=(sz*cols,sz*rows):errors.append(f'{name}: dimensions {im.size}, expected {(sz*cols,sz*rows)}')
  if im.getchannel('A').getextrema()[0]>0:errors.append(f'{name}: background not transparent')
  total+=os.stat(path).st_size
  for i in range(count):
   tile=im.crop(((i%cols)*sz,(i//cols)*sz,(i%cols+1)*sz,(i//cols+1)*sz));alpha=tile.getchannel('A')
   if alpha.getbbox() is None:errors.append(f'{name} frame {i} empty');continue
   edge=sum(1 for v in list(alpha.crop((0,0,sz,2)).getdata())+list(alpha.crop((0,sz-2,sz,sz)).getdata())+list(alpha.crop((0,0,2,sz)).getdata())+list(alpha.crop((sz-2,0,sz,sz)).getdata()) if v>80)
   if edge>7:warnings.append(f'{name}: possible clipping frame {i} ({edge} opaque edge pixels)')
for cat in ['backgrounds','effects','icons','audio','ui','portraits','props','source']:
 count=0
 for path in glob.glob(os.path.join(ROOT,'assets',cat,'*')):
  if os.path.isdir(path):continue
  count+=1;total+=os.stat(path).st_size
  if path.endswith(('.png','.webp')):
   try: im=Image.open(path);im.verify()
   except Exception as e:errors.append(f'invalid image {path}: {e}')
 counts[cat]=count
for name,src in atlas['icons'].items():
 if not os.path.isfile(os.path.join(ROOT,src)):errors.append('icon missing '+src)
for f in ['index.html','manifest.webmanifest','service-worker.js','js/main.js','js/game.bundle.js','data/patent-cases.js']:
 if not os.path.isfile(os.path.join(ROOT,f)):errors.append('core missing '+f)
print('ASSET COUNTS:',counts,'\nTOTAL BYTES:',total,'\nERRORS:',len(errors),'\nWARNINGS:',len(warnings))
for e in errors[:40]:print('ERROR',e)
for w in warnings[:35]:print('WARN',w)
if len(warnings)>35:print('... and',len(warnings)-35,'more warnings')
sys.exit(1 if errors else 0)
