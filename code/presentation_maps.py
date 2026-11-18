"""Geographical views of saved panel coverage and national India results."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'figures/presentation'
world=json.loads((ROOT/'data/work/presentation/ne_110m_admin_0_countries.geojson').read_text(encoding='utf-8'))
co=pd.read_csv(ROOT/'data/processed/nine_crop/index_components.csv')
counts=co.groupby('m49').crop.nunique().to_dict()
plt.rcParams.update({'figure.facecolor':'white','axes.facecolor':'white','savefig.facecolor':'white','text.color':'#17251E','axes.labelcolor':'#17251E','xtick.color':'#44534B','ytick.color':'#44534B','font.family':'DejaVu Sans','font.size':16})

def draw(ax,coverage=False):
    for f in world['features']:
        p=f['properties'];g=f['geometry']
        if not g or p['ADMIN']=='Antarctica':continue
        try: code=int(p['ISO_N3_EH'])
        except (TypeError,ValueError):code=-1
        if p.get('ADM0_A3')=='FRA':code=250
        value=counts.get(code)
        fill=plt.get_cmap('YlGnBu')(Normalize(1,9)(value)) if coverage and value else '#E8ECE9'
        if not coverage and p.get('ADM0_A3')=='IND':fill='#2479AD'
        polys=[g['coordinates']] if g['type']=='Polygon' else g['coordinates'] if g['type']=='MultiPolygon' else []
        for poly in polys:
            ax.add_patch(Polygon(np.asarray(poly[0]),facecolor=fill,edgecolor='#697C72' if value else '#A0ABA4',linewidth=.55))
    ax.set_aspect('equal');ax.axis('off')

fig,ax=plt.subplots(figsize=(13,6.8));draw(ax,True)
ax.set(xlim=(-174,180),ylim=(-56,83))
for x,y,t in [(-105,39,'USA'),(-106,60,'Canada'),(-52,-13,'Brazil'),(80,61,'Russia'),(105,35,'China'),(77,22,'India'),(134,-25,'Australia'),(17,-29,'S. Africa')]:
    ax.text(x,y,t,fontsize=13,ha='center',color='#17251E',bbox={'facecolor':'white','alpha':.75,'edgecolor':'none','pad':2})
cb=fig.colorbar(ScalarMappable(norm=Normalize(1,9),cmap='YlGnBu'),ax=ax,orientation='horizontal',fraction=.05,pad=.025,shrink=.8,ticks=[1,3,5,7,9])
cb.set_label('Number of crops evaluated in each country',color='#17251E');cb.ax.tick_params(colors='#17251E')
fig.savefig(OUT/'world_coverage.png',dpi=190,bbox_inches='tight',pad_inches=.1);plt.close(fig)

fig,ax=plt.subplots(figsize=(6,6.5));draw(ax)
ax.set(xlim=(66,99),ylim=(5,38))
ax.text(79,22,'INDIA',ha='center',color='black',fontsize=26,weight='bold')
fig.savefig(OUT/'india_national.png',dpi=190,bbox_inches='tight',pad_inches=.1);plt.close(fig)
with (OUT/'PROVENANCE.md').open('a',encoding='utf-8') as f:
    f.write('\nWorld overview map: number of unique modelled crops per country in saved index_components.csv (59 pairs, 20 countries), using Natural Earth ISO numeric identifiers. Coverage is not vulnerability. India map: geographic locator for national results only, with no state/district estimates. Same Natural Earth basemap and provenance as above. Built by code/presentation_maps.py without rerunning scientific calculations.\n')
print('World coverage and India locator maps saved.')
