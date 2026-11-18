"""Map official observed state statistics, separately from model results."""
from pathlib import Path
import json
import unicodedata
import hashlib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable

ROOT=Path(__file__).resolve().parents[1]
W=ROOT/'data/work/presentation'
G=W/'india_states_verified.geojson'
if not G.exists() or G.stat().st_size<1000:
    import requests
    url='https://media.githubusercontent.com/media/wmgeolab/geoBoundaries/9469f09/releaseData/gbOpen/IND/ADM1/geoBoundaries-IND-ADM1_simplified.geojson'
    r=requests.get(url,timeout=50);r.raise_for_status();r.json();G.write_bytes(r.content)
assert hashlib.sha256(G.read_bytes()).hexdigest()=='4c63fe43294a391e8f2de4e9f86f3edb60f8688275b9fee90c61fb2aa0c26061','Incomplete or changed pinned boundary file'
geo=json.loads(G.read_text(encoding='utf-8'))
df=pd.read_csv(ROOT/'data/external/india_state_wheat_2023_24.csv').set_index('state')
plt.rcParams.update({'figure.facecolor':'white','axes.facecolor':'white','savefig.facecolor':'white','text.color':'#17251E','axes.labelcolor':'#17251E','xtick.color':'#44534B','ytick.color':'#44534B','font.family':'DejaVu Sans','font.size':15})
fig,axs=plt.subplots(1,2,figsize=(15,6.1))
fig.subplots_adjust(wspace=.06,bottom=.19,top=.91)
matched=set()
for ax,col,cmap,title,limit in zip(axs,['share_national_production_pct','wheat_area_irrigated_pct'],['YlOrRd','YlGnBu'],['Share of India\'s wheat production','Wheat area under irrigation'],[35,100]):
    norm=Normalize(0,limit);cm=plt.get_cmap(cmap)
    for f in geo['features']:
        name=unicodedata.normalize('NFKD',f['properties']['shapeName']).encode('ascii','ignore').decode()
        name={'Uttaranchal':'Uttarakhand','Orissa':'Odisha'}.get(name,name)
        value=df.loc[name,col] if name in df.index else None
        if value is not None:matched.add(name)
        g=f['geometry'];polys=[g['coordinates']] if g['type']=='Polygon' else g['coordinates']
        for poly in polys:
            ax.add_patch(Polygon(np.array(poly[0]),facecolor=cm(norm(value)) if value is not None else '#E8ECE9',edgecolor='#91A298',linewidth=.7))
    ax.set(xlim=(67,98),ylim=(6,37));ax.set_aspect('equal');ax.axis('off');ax.set_title(title,fontsize=20)
    labels=[(80.7,27.1,'Uttar Pradesh','UP'),(78.5,23.2,'Madhya Pradesh','MP'),(75.1,31.0,'Punjab','Punjab')] if col.startswith('share') else [(77.1,31.5,'Himachal Pradesh','HP'),(73.8,26.1,'Rajasthan','Rajasthan'),(80.5,27.0,'Uttar Pradesh','UP')]
    for x,y,state,short in labels:
        ax.text(x,y,f'{short}\n{df.loc[state,col]:.1f}%',ha='center',va='center',fontsize=12,color='#17251E',bbox={'facecolor':'white','alpha':.83,'edgecolor':'none','pad':2})
    cb=fig.colorbar(ScalarMappable(norm=norm,cmap=cmap),ax=ax,orientation='horizontal',fraction=.045,pad=.015,shrink=.82)
    cb.set_label('National production share (%)' if col.startswith('share') else 'Share of state wheat area (%)',fontsize=14,color='#17251E')
    cb.ax.tick_params(colors='#17251E',labelsize=12)
assert matched==set(df.index),set(df.index)-matched
fig.text(.5,.035,'Observed 2023-24 statistics. Grey: outside the ten-state table, not zero production. Boundary reference: 2011.',ha='center',fontsize=13,color='#53645A')
fig.savefig(ROOT/'figures/presentation/india_wheat_states.png',dpi=190,bbox_inches='tight',pad_inches=.1)
plt.close(fig)
with (ROOT/'figures/presentation/PROVENANCE.md').open('a',encoding='utf-8') as f:
    f.write('\nIndia state wheat maps: official Agricultural Statistics at a Glance 2024-25, Table 2.5(b), printed p54; 2023-24 production and irrigation columns, ten listed states. Contextual observed data, not state model outputs. geoBoundaries IND ADM1 (2011 metadata reference), CC BY 2.5 IN, pinned commit 9469f09. Boundary SHA256: 4c63fe43294a391e8f2de4e9f86f3edb60f8688275b9fee90c61fb2aa0c26061. Details: docs/evidence/INDIA_STATE_MAP_SOURCES.md.\n')
print('Ten-state wheat map written. Top-three share:',df.iloc[:3].share_national_production_pct.sum())
