"""Explicit palette calculations, in addition to rendered axe checks."""
import json
from pathlib import Path

def luminance(hex):
 rgb=[int(hex[i:i+2],16)/255 for i in (1,3,5)]
 linear=[x/12.92 if x<=.04045 else ((x+.055)/1.055)**2.4 for x in rgb]
 return sum(a*b for a,b in zip(linear,[.2126,.7152,.0722]))
def ratio(a,b):
 x,y=sorted([luminance(a),luminance(b)])
 return round((y+.05)/(x+.05),2)
pairs=[('orange button dark text','#111113','#FF7A1A',4.5),('orange button white text (avoid)','#FFFFFF','#FF7A1A',4.5),('secondary on card','#A1A1AA','#171719',4.5),('gain on dark','#22C55E','#0A0A0B',4.5),('loss on dark','#FF7373','#0A0A0B',4.5),('gain on tinted tile','#79E9AA','#1A4938',4.5),('loss on tinted tile','#FFB0B0','#612F2F',4.5),('focus on card','#FF7A1A','#171719',3)]
rows=[dict(pair=n,foreground=a,background=b,ratio=ratio(a,b),target=t,passes=ratio(a,b)>=t,used=n!='orange button white text (avoid)') for n,a,b,t in pairs]
Path('tests/contrast-results.json').write_text(json.dumps(rows,indent=2)+'\n')
assert all(r['passes'] for r in rows if r['used'])
print('\n'.join(f"{r['pair']}: {r['ratio']}:1 {'PASS' if r['passes'] else 'DO NOT USE'}" for r in rows))
