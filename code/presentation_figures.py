"""Plot saved scientific results for slides; no model or test execution."""
from pathlib import Path
import json,hashlib
import requests
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable
from matplotlib.ticker import MaxNLocator, FormatStrFormatter

ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'data/processed/nine_crop'; O=ROOT/'figures/presentation';O.mkdir(exist_ok=True)
BASE=ROOT/'data/work/presentation/ne_110m_admin_0_countries.geojson'
URL='https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_admin_0_countries.geojson'
if not BASE.exists():
 r=requests.get(URL,timeout=60);r.raise_for_status();BASE.write_bytes(r.content)
world=json.loads(BASE.read_text(encoding='utf-8'))
plt.rcParams.update({'figure.facecolor':'white','axes.facecolor':'white','savefig.facecolor':'white','text.color':'#17251E','axes.labelcolor':'#17251E','xtick.color':'#44534B','ytick.color':'#17251E','axes.edgecolor':'#52625A','font.family':'DejaVu Sans','font.size':15,'axes.spines.top':False,'axes.spines.right':False})
def save(fig,name):
 fig.savefig(O/(name+'.png'),dpi=190,bbox_inches='tight',pad_inches=.14)
 plt.close(fig)

co=pd.read_csv(P/'index_components.csv');fc=pd.read_csv(P/'future_components.csv');cr=pd.read_csv(P/'future_crop.csv')
codes={'United States of America':'USA','Russian Federation':'RUS','China, mainland':'CHN','India':'IND','Egypt':'EGY','Brazil':'BRA'}
labels={'USA':(-105,39,'USA'),'RUS':(82,60,'Russia'),'CHN':(104,34,'China'),'IND':(79,21,'India'),'EGY':(29,27,'Egypt'),'BRA':(-52,-13,'Brazil')}
w=co[co.crop=='wheat'];fw=fc[fc.crop=='wheat']
fig,axs=plt.subplots(1,2,figsize=(16,6.8));fig.subplots_adjust(wspace=.08,bottom=.19,top=.88)
for ax,col,frame,title,cmap in [(axs[0],'F4_hazard_paired',w,'Present wheat vulnerability','YlGnBu'),(axs[1],'dF4_abs',fw,'Projected change in wheat vulnerability','YlOrRd')]:
 values={codes[r.country]:getattr(r,col) for r in frame.itertuples()};norm=Normalize(0,max(values.values()));cm=plt.get_cmap(cmap)
 for f in world['features']:
  props=f['properties'];code=props.get('ADM0_A3');g=f['geometry']
  if not g or props.get('ADMIN')=='Antarctica':continue
  polys=[g['coordinates']] if g['type']=='Polygon' else g['coordinates'] if g['type']=='MultiPolygon' else []
  for poly in polys:
   pts=np.array(poly[0]);ax.add_patch(Polygon(pts,facecolor=cm(norm(values[code])) if code in values else '#E8ECE9',edgecolor='#65756C' if code in values else '#A0ABA4',linewidth=.4))
 for code,(x,y,name) in labels.items():
  val=values[code];label=name+'\n'+(f'{val:.3f}' if col=='F4_hazard_paired' else f'+{val:.3f}')
  ax.text(x,y,label,fontsize=10,ha='center',va='center',color='#17251E',bbox={'facecolor':'white','alpha':.77,'edgecolor':'none','pad':1.8})
 ax.set(xlim=(-174,180),ylim=(-56,83));ax.set_aspect('equal');ax.axis('off');ax.set_title(title,fontsize=20,pad=18)
 cb=fig.colorbar(ScalarMappable(norm=norm,cmap=cm),ax=ax,orientation='horizontal',fraction=.055,pad=.09,shrink=.85)
 cb.set_label('F4, observed climate 2001–2024' if col=='F4_hazard_paired' else 'Change in F4: 1971–2000 to 2041–2060',fontsize=13);cb.ax.tick_params(labelsize=12)
 if col=='dF4_abs':
  cb.locator=MaxNLocator(nbins=4);cb.formatter=FormatStrFormatter('%.3f');cb.update_ticks()
fig.text(.5,.045,'Six modelled wheat countries only; grey = not evaluated for wheat',ha='center',color='#53645A',fontsize=14)
save(fig,'wheat_maps')

order=['wheat','maize','bean','soybean','rapeseed','chickpea','rice','lentil','groundnut']
names={'bean':'Common bean','rapeseed':'Rapeseed-mustard'}
fig,axs=plt.subplots(1,2,figsize=(15,6));fig.subplots_adjust(wspace=.48,bottom=.16)
for ax,wt,title in [(axs[0],'eq','Equal-country weighting'),(axs[1],'pw','Production weighting')]:
 t=cr.set_index('crop').loc[order];y=np.arange(9)
 h=t[f'F4_{wt}_historical_1971_2000'];f=t[f'F4_{wt}_future_2041_2060']
 ax.hlines(y,np.minimum(h,f),np.maximum(h,f),color='#53645A',lw=2)
 ax.scatter(h,y,s=65,facecolor='white',edgecolor='#2479AD',linewidth=2,label='1971–2000',zorder=3)
 ax.scatter(f,y,s=65,color='#C6533C',label='2041–2060',zorder=4)
 ax.set_yticks(y,[names.get(c,c.title())+(' *' if c in ['rice','rapeseed'] else '') for c in order]);ax.invert_yaxis();ax.set_xlabel('F4 (relative score; linear scale)');ax.set_title(title,fontsize=19);ax.grid(axis='x',alpha=.19)
 ax.legend(loc='lower right',facecolor='white',edgecolor='#52625A',labelcolor='#17251E',fontsize=12)
fig.text(.5,.02,'* Rice and rapeseed use unsupported heat-response assumptions in this full-model view',ha='center',fontsize=12,color='#53645A');save(fig,'crop_trajectories')

fig,ax=plt.subplots(figsize=(12,5));t=co.groupby('crop').agg(heat=('E_heat','mean'),water=('E_water','mean'))
# Average paired contributions use the product within each country, not products of averages.
t=co.assign(heat=.5*co.E_heat*co.S_heat*co.In,water=.5*co.E_water*co.S_water*co.In).groupby('crop')[['heat','water']].mean().reindex(order)
y=np.arange(9);ax.barh(y,t.water,color='#2479AD',label='Water contribution');ax.barh(y,t.heat,left=t.water,color='#C6533C',label='Heat contribution');ax.set_yticks(y,[names.get(c,c.title()) for c in order]);ax.invert_yaxis();ax.set_xlabel('Mean contribution to present F4');ax.legend(facecolor='white',edgecolor='none',labelcolor='#17251E',loc='lower right');ax.grid(axis='x',alpha=.15);save(fig,'stress_components')

dv=pd.read_csv(P/'diversity_after_losses.csv')
print('Diversity scenario labels:',dv.scenario.unique().tolist())
fig,ax=plt.subplots(figsize=(11,5.5))
# Use exact existing scenario labels; require one row per country/scenario.
scenarios=[(s, '#2479AD','o','All modelled crops -10%') for s in dv.scenario.unique() if str(s).startswith('B ')]
scenarios += [(s,'#C6533C','s','Future climate, loss-only') for s in dv.scenario.unique() if str(s).startswith('C ')]
if len(scenarios)!=2:raise ValueError('Unexpected saved diversity scenario labels')
for scenario,color,marker,label in scenarios:
 g=dv[(dv.scenario==scenario)&(dv.m49!=1)]
 if 'bound' in g and g.bound.notna().any():g=g[g.bound=='upper']
 if g.m49.duplicated().any():raise ValueError('Ambiguous country rows')
 ax.scatter(g.pct_total_iron,g.d_eff_iron,c=color,marker=marker,s=75,label=label)
 for _,r in g[g.Area.isin(['India','Russian Federation','United States of America','China, mainland'])].iterrows():
  label={'Russian Federation':'Russia','United States of America':'USA','China, mainland':'China'}.get(r.Area,r.Area)
  ax.annotate(label,(r.pct_total_iron,r.d_eff_iron),xytext=(6,6),textcoords='offset points',fontsize=12)
ax.axhline(0,color='#53645A',lw=1);ax.axvline(0,color='#53645A',lw=1);ax.set_xlabel('Change in national iron supply (%)');ax.set_ylabel('Change in effective iron sources');ax.legend(facecolor='white',edgecolor='#52625A',labelcolor='#17251E',fontsize=12,loc='upper right');ax.grid(alpha=.15);save(fig,'diversity_scatter')

fig,ax=plt.subplots(figsize=(11,6));m=co.groupby('crop')[[f'sh_{n}' for n in ['kcal','protein','fat','zinc','iron']]].mean().reindex(order)*100
im=ax.imshow(m,cmap='YlGnBu',vmin=0,vmax=m.max().max(),aspect='auto');ax.set_yticks(range(9),[names.get(c,c.title()) for c in order]);ax.set_xticks(range(5),['Energy','Protein','Fat','Zinc','Iron']);ax.tick_params(length=0)
for i in range(9):
 for j in range(5):ax.text(j,i,f'{m.iloc[i,j]:.1f}',ha='center',va='center',color='white' if m.iloc[i,j]>18 else '#111111',fontsize=14)
cb=fig.colorbar(im,ax=ax,pad=.025);cb.set_label('Mean share of national nutrient supply (%)');save(fig,'nutrient_profiles')
(O/'PROVENANCE.md').write_text(f'''# Presentation figure provenance

Figures are plot-only views of saved nine-crop CSV results; no scientific pipeline or tests were run.
The wheat maps colour only the six modelled wheat countries. Present scores use 2001-2024; projected differences use 1971-2000 to 2041-2060. Grey is unmodelled, not zero risk. Country fill represents national aggregates, not local crop-area estimates. Boundaries are for visual context.

Basemap: Natural Earth 1:110m admin-0 countries, public domain. Retrieved 18 November 2026.
Source: {URL}
SHA256: {hashlib.sha256(BASE.read_bytes()).hexdigest()}
License: https://www.naturalearthdata.com/about/terms-of-use/

Trajectory: future_crop.csv. Stress components and nutrient profiles: index_components.csv (equal mean over each crop's own panel). Diversity: diversity_after_losses.csv, upper pass-through, scenarios B/C, historical-reference future, fixed FBS categories. Panel means are not world population-weighted means.
''',encoding='utf-8')
# Metric teaching plots use the same saved values as the results. These are
# descriptive panel means, not new hazard estimates or illustrative fake data.
metric_order=['wheat','rice','maize','chickpea','lentil','bean','soybean','groundnut','rapeseed']
metric_names=['Wheat','Rice*','Maize','Chickpea','Lentil','Common bean','Soybean','Groundnut','Rapeseed*']
means=co.groupby('crop').mean(numeric_only=True).reindex(metric_order)
for field,name,label,color in [
 ('E_heat','heat_exposure','Mean normalised heat exposure', '#C6533C'),
 ('E_water','water_exposure','Mean normalised water exposure', '#2479AD'),
 ('I','importance_profile','Mean five-nutrient share (%)', '#AD7D16')]:
 fig,ax=plt.subplots(figsize=(10,5.0))
 values=means[field].to_numpy()*(100 if field=='I' else 1)
 plot_labels=metric_names if field=='E_heat' else [v.replace('*','') for v in metric_names]
 ax.barh(plot_labels,values,color=color,height=.65)
 ax.invert_yaxis();ax.set_xlabel(label,fontsize=17);ax.tick_params(labelsize=16)
 xmax=max(values)*1.22;ax.set_xlim(0,xmax)
 for i,v in enumerate(values):
  ax.text(v+xmax*.012,i,f'{v:.1f}' if field=='I' else f'{v:.3f}',va='center',fontsize=14)
 ax.grid(axis='x',alpha=.15);ax.set_axisbelow(True)
 save(fig,name)
fig,axs=plt.subplots(1,2,figsize=(12,5.0),sharey=True)
for ax,col,title,color in zip(axs,['S_heat','S_water'],['Heat response','Water response'],['#C6533C','#2479AD']):
 values=means[col].to_numpy()
 ax.barh(metric_names,values,color=color,height=.65);ax.set_xlim(0,1.19)
 ax.set_title(title,fontsize=19);ax.set_xlabel('Normalised sensitivity',fontsize=16)
 ax.tick_params(labelsize=15);ax.grid(axis='x',alpha=.15);ax.set_axisbelow(True)
 for i,v in enumerate(values):ax.text(v+.025,i,f'{v:.2f}',va='center',fontsize=13)
axs[0].invert_yaxis();fig.subplots_adjust(wspace=.15)
save(fig,'sensitivity_profile')
with (O/'PROVENANCE.md').open('a',encoding='utf-8') as f:
 f.write('\nMetric teaching graphs: heat_exposure, water_exposure, importance_profile and sensitivity_profile read E_heat, E_water, I, S_heat and S_water from saved index_components.csv. They show equal country means within each crop panel. Sensitivity is literature/proxy only, not the earlier blended empirical method. Stars identify rice/rapeseed unsupported heat-response assumptions; additional transfer limitations remain for other crops.\n')
print('Nine figures written from saved results, including four metric teaching graphs.')
