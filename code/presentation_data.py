"""Prepare presentation assets from saved CSVs. Does not run the scientific pipeline."""
from pathlib import Path
import json
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'data/processed/nine_crop'
OUT=ROOT/'data/work/presentation'
OUT.mkdir(parents=True,exist_ok=True)
data={}
for name in ['index_crop','future_crop','future_group','index_components','co2_nutrient_results','diversity_after_losses','future_yield_reference_periods']:
    data[name]=pd.read_csv(P/(name+'.csv')).fillna('').to_dict('records')
(OUT/'data.json').write_text(json.dumps(data),encoding='utf-8')
formulae={
 'index':r'$F4_{c,k}=\frac{1}{2}(E_{h,c,k}S_{h,c}+E_{w,c,k}S_{w,c})\,\widetilde I_{c,k}$',
 'importance':r'$I_{c,k}=\frac{1}{5}\sum_{n=1}^{5}\frac{N_{c,k,n}}{N_{k,n}},\qquad \widetilde I=I/I_{\max}$',
 'supply':r'$N^{\prime}_{n}=\sum_i N_{i,n}(1-f_i)(1+q_{i,n})$',
 'diversity':r'$H_n=-\sum_i p_{i,n}\ln p_{i,n},\qquad N_{\mathrm{eff},n}=e^{H_n}$',
 'adequacy':r'$\mathrm{MAR}=\frac{1}{5}\sum_{n=1}^{5}\min\left(1,\frac{N_n}{R_n}\right)$',
 'hazard':r'$H_h=\langle\max(0,T_{\mathrm{eff}}-T_{\mathrm{crit}})\rangle,\quad H_w=\langle r_{\mathrm{rainfed}}\max(0,1-P/ET_c)\rangle$'
}
formulae.update({
 'heat':r'$H_h=\langle\max(0,T_{\mathrm{eff}}-T_{\mathrm{crit}})\rangle,\qquad E_h=H_h/H_{h,\mathrm{ref}}$',
 'water':r'$H_w=\left\langle\frac{\sum_j R_j\max(0,1-P_j/ET_{c,j})}{\sum_j A_j}\right\rangle,\quad E_w=H_w/H_{w,\mathrm{ref}}$',
 'sensitivity':r'$S_h=s_h/\max(s_h),\qquad S_w=K_y/\max(K_y)$',
 'pass_through':r'$f_i=\ell_i\,\mathrm{clip}(SSR_i,0,1),\qquad N^{\prime}_n=\sum_i N_{i,n}(1-f_i)(1+q_{i,n})$'
})
for name,expr in formulae.items():
 fig=plt.figure(figsize=(13,1.25),facecolor='#FFFFFF')
 fig.text(.02,.45,expr,fontsize=26,color='#17251E',va='center')
 fig.savefig(OUT/(name+'.png'),dpi=180,bbox_inches='tight',pad_inches=.12)
 plt.close(fig)
print('Presentation assets prepared from saved outputs only.')
