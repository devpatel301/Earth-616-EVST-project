// Results-focused 20-minute presentation. Reads saved results only.
import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
// Resolve the bundled implementation without installing dependencies.
const runtime='C:/Users/user/.cache/codex-runtimes/codex-primary-runtime/dependencies';
const {Presentation,PresentationFile}=await import(pathToFileURL(runtime+'/node/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs').href).catch(async()=>await import(pathToFileURL(runtime+'/node/node_modules/@oai/artifact-tool/dist/index.js').href));
const root=path.resolve(import.meta.dirname,'..'), tmp=path.join(root,'data/work/presentation'), out=path.join(root,'output/presentation');
const d=JSON.parse(await fs.readFile(path.join(tmp,'data.json'),'utf8'));
const mathAssets={};
for(const name of ['index','importance','supply','diversity','adequacy','hazard','heat','water','sensitivity','pass_through']) mathAssets[name]=new Uint8Array(await fs.readFile(path.join(tmp,name+'.png')));
const figureAssets={};
for(const name of ['wheat_maps','crop_trajectories','stress_components','diversity_scatter','nutrient_profiles','heat_exposure','water_exposure','importance_profile','sensitivity_profile','world_coverage','india_national','india_wheat_states']) figureAssets[name]=new Uint8Array(await fs.readFile(path.join(root,'figures/presentation',name+'.png')));
const ornaments={};
for(const name of ['rings','dots','vertical_dots','waves','dot_grid','pluses']) ornaments[name]=new Uint8Array(await fs.readFile(path.join(root,'figures/presentation/theme',name+'.png')));
const P=Presentation.create({slideSize:{width:1280,height:720}});
const C={bg:'#000000',green:'#F2F5F3',gold:'#DDDDDD',orange:'#C4C4C4',blue:'#E3E3E3',muted:'#BDBDBD',line:'#444444'};
const timings=[20,35,35,40,60,60,65,50,45,40,60,60,45,60,50,45,60,40,40,65,45,60,55,35,30];
const notes=[];
function text(s,t,x,y,w,h,size=28,color=C.green,bold=false){let q=s.shapes.add({geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});q.text=t;q.text.style={fontFamily:'Arial',fontSize:size,color,bold};q.text.insets=0;return q;}
const headings=[
 ['ENVIRONMENTAL SCIENCE','CLIMATE AND NUTRITION'],['THE PROBLEM','NUTRITION AT RISK'],['STUDY SCOPE','WORLD COVERAGE'],['METHOD','THE FRAMEWORK'],['EXPOSURE','HEAT STRESS'],['EXPOSURE','WATER STRESS'],['CROP RESPONSE','SENSITIVITY'],['DEPENDENCE','NUTRITIONAL IMPORTANCE'],['MODEL','THE VULNERABILITY INDEX'],['METHOD','FROM YIELD TO NUTRIENTS'],['CROP OVERVIEW','CEREALS LEAD'],['FUTURE OVERVIEW','CHANGING VULNERABILITY'],['DRIVERS','WATER NOW, HEAT LATER'],['NUTRIENT OVERVIEW','WHAT EACH CROP SUPPLIES'],['NATIONAL SUPPLY','QUANTITY AND QUALITY'],['REQUIREMENTS','NUTRIENT ADEQUACY'],['GEOGRAPHY','WHEAT VULNERABILITY'],['STATE CONTEXT',"INDIA'S WHEAT BELT"],['NUTRIENT QUALITY','THE CO2 EFFECT'],['INDIA','QUANTITY + QUALITY LOSSES'],['DIVERSITY','FOOD-SOURCE DIVERSITY'],['FINDING','THE DIVERSITY PARADOX'],['EXTERNAL EVIDENCE','LITERATURE COMPARISON'],['INTERPRETATION','LIMITS OF THE MODEL'],['KEY','TAKEAWAYS'],['BACKUP','CLIMATE REFERENCE PERIODS'],['BACKUP','INDIA: TWO BASELINES'],['BACKUP','WHY STUDIES DISAGREE'],['SOURCES','SELECTED REFERENCES']];
function ornament(s,name,x,y,w,h){s.images.add({blob:ornaments[name],contentType:'image/png',position:{left:x,top:y,width:w,height:h},fit:'contain',alt:'Geometric ornament reused from the supplied theme'});}
function slide(title,source,note,backup=false){let s=P.slides.add();s.background.fill=C.bg;let n=P.slides.items.length;
 if(n!==1){const [kicker,main]=headings[n-1];text(s,kicker,65,33,1030,30,21,C.green,true);let h=text(s,main,62,65,1070,78,50,'#8F8F8F',true);h.text.style={fontFamily:'Arial Black',fontSize:50,color:'#8F8F8F',bold:true};ornament(s,n%3===0?'dot_grid':n%3===1?'dots':'pluses',1145,35,72,54);}
 s.speakerNotes.text=`${backup?'Backup / questions':`Target time: ${timings[n-1]} seconds`}\n\n${note}\n\nSources: ${source}\nTheme: The_Big_Longs_16_slides.pdf, supplied by user. Rebuilt editable typography/panels; original ornaments reused. Arial Black and Arial approximate its outlined Type3 lettering.`;
 notes.push({slide:n,title,seconds:backup?0:timings[n-1],notes:note,source});return s;}
function panel(s,x,y,w,h){return s.shapes.add({geometry:'roundRect',position:{left:x,top:y,width:w,height:h},fill:'#FFFFFF',line:{fill:'none',width:0},borderRadius:12});}
function lines(s,items,x=65,y=180,w=1110,size=29,gap=98){let n=P.slides.items.length;
 if([2,19,24,25].includes(n)){
  items.forEach((v,i)=>{let xx=x,yy=y+i*gap,ww=w,hh=gap-16,fs=Math.min(size,30);
   if(n===24){xx=65+(i%2)*590;yy=185+Math.floor(i/2)*215;ww=560;hh=180;fs=27;}
   panel(s,xx,yy,ww,hh);panel(s,xx+ww/2-24,yy-12,48,28);text(s,String(i+1).padStart(2,'0'),xx+ww/2-15,yy-10,42,25,17,'#111111',true);text(s,v.replace(/^\d\s+/,''),xx+25,yy+18,ww-50,hh-28,fs,'#222222',n===25);
  });return;
 }
 items.forEach((v,i)=>text(s,v,x,y+i*gap,w,gap-10,size));}

function formula(s,name,y=160,h=100){s.images.add({blob:mathAssets[name],contentType:'image/png',position:{left:60,top:y,width:1155,height:h},fit:'contain',alt:name+' equation'});}
function figure(s,name,x=55,y=155,w=1170,h=495){s.images.add({blob:figureAssets[name],contentType:'image/png',position:{left:x,top:y,width:w,height:h},fit:'contain',alt:name.replaceAll('_',' ')+'; source: saved project results'});}
function chart(s,cats,series,{x=55,y=165,w=1160,h=425,horizontal=false,max,fmt='0.00',legend=false,categoryLabels='nextTo'}={}){series=series.map(r=>({...r,fill:({[C.blue]:'#2479AD',[C.orange]:'#C6533C',[C.gold]:'#AD7D16',[C.green]:'#334A3E'})[r.fill]||r.fill}));return s.charts.add('bar',{position:{left:x,top:y,width:w,height:h},categories:cats,series,barOptions:{direction:horizontal?'bar':'column',grouping:'clustered',gapWidth:65},hasLegend:legend,legend:{position:'bottom',textStyle:{typeface:'Arial',fontSize:19,fill:'#17251E'}},xAxis:{tickLabelPosition:categoryLabels,textStyle:{typeface:'Arial',fontSize:19,fill:'#17251E'},line:{fill:'#CBD3CD',width:1}},yAxis:{min:series.every(s=>s.values.every(v=>v>=0))?0:undefined,max,numberFormatCode:fmt,textStyle:{typeface:'Arial',fontSize:18,fill:'#44534B'},majorGridlines:{fill:'#CBD3CD',width:1}},dataLabels:{showValue:true,position:'outEnd',textStyle:{typeface:'Arial',fontSize:18,fill:'#17251E'},numberFormatCode:fmt},chartFill:'#FFFFFF',plotAreaFill:'#FFFFFF'});}
function table(s,values,widths,y=180,height=340){let t=s.tables.add({rows:values.length,columns:values[0].length,left:65,top:y,width:1150,height,columnWidths:widths,values});t.borders.assign({style:'solid',fill:C.line,width:1});for(let r=0;r<values.length;r++)for(let c=0;c<values[0].length;c++){let cell=t.getCell(r,c);cell.fill=r===0?'#E5E5E5':'#FFFFFF';cell.text.style={fontFamily:'Arial',fontSize:23,color:'#222222',bold:r===0};}return t;}
let s=slide('Climate change and nutritional security','Environmental Science • End evaluation • November 2026','Open with the question: which crops put nutrition at risk when climate stress and dependence coincide? The study is a conditional screening framework, not a forecast of what every household will eat. Introduce the four team members.');
text(s,'ENVIRONMENTAL SCIENCE  /  END EVALUATION 2026',65,175,1080,35,18,C.muted,true);
text(s,'CLIMATE CHANGE',65,237,1040,60,35,C.green,true);
let coverTitle=text(s,'NUTRITION',60,290,1090,145,110,'#8F8F8F',true);coverTitle.text.style={fontFamily:'Arial Black',fontSize:110,color:'#8F8F8F',bold:true};
text(s,'Which crops are most vulnerable?',65,458,1100,60,33,'#D0D0D0');
text(s,'Nine crops, future climate and national nutrient security',65,525,1100,45,26,C.muted);
text(s,'Arpit Mahtele  /  Dev Patel  /  Navey Puri  /  Shreyash Lohare',65,587,1100,40,23,C.green);
ornament(s,'rings',1080,55,150,150);ornament(s,'dots',890,115,85,30);ornament(s,'vertical_dots',1190,300,32,100);ornament(s,'waves',1090,640,135,42);

s=slide('The question: which crop losses matter for nutrition?','Project question and final report, introduction','Explain that the same percentage crop loss has different nutritional consequences depending on dependence, imports and which nutrients the crop supplies. Our contribution connects climate stress with nutritional importance, then examines quantity, quality and diversity separately. Do not claim the index combination is a universally standard or validated method.');
lines(s,['Climate stress occurs where crops are grown.','Its nutritional consequence depends on what people rely on.','We connect exposure, crop response and national nutrient supply.'],65,180,1100,34,120);

s=slide('World overview: 20 countries and nine crops','Saved index_components.csv; Natural Earth 110m basemap; figures/presentation/PROVENANCE.md','The map colours the 20 selected countries by the number of crops evaluated, not risk. Coverage differs between crops, giving 59 crop-country pairs in total. Grey countries are outside the selected panels. Climate periods and the nutrition baseline are distinct. This selective panel does not represent all world agriculture.');
figure(s,'world_coverage',20,150,865,465);
text(s,'59 crop-country pairs',910,180,310,90,32,C.gold,true);
text(s,'9 crops in 3 groups',910,285,310,90,30);
text(s,'Climate model:\nMRI-ESM2-0\nSSP2-4.5',910,410,310,140,27,C.blue);
text(s,'Grey countries: outside the selected study panels',65,600,1150,30,22,C.muted);
text(s,'Climate: 1971-2000 / 2001-24 / 2041-60. Nutrient supply: 2021-23.',65,635,1150,50,24,C.muted);

s=slide('Framework: exposure, sensitivity and nutrient dependence','Final report, methods; updated from the four-crop mid-evaluation framework','Explain the three quantities before showing any crop ranking. Exposure asks how much heat or water stress occurs where and when a crop grows. Sensitivity describes the crop response per unit stress. Importance measures national dependence on that crop for five nutrients. Heat exposure pairs with heat response and water exposure with water response. The score prioritises crop-country combinations. A separate loss-accounting calculation translates yield scenarios into nutrient supply.');
table(s,[['Exposure E','Sensitivity S','Importance I'],['How much stress?','How strongly does the crop respond?','How much nutrition depends on it?'],['Monthly climate, crop area, season, irrigation','Published crop coefficients and declared proxies','National supply of five nutrients']],[380,380,390],180,300);
text(s,'We pair heat with heat response, and water with water response.',65,540,1120,65,30,C.gold,true);
text(s,'Nutrient-loss scenarios follow a separate accounting step.',65,620,1120,45,27);

s=slide('Heat exposure: temperature above the crop threshold','code/04_hazards.py; code/05_country_series.py; saved index_components.csv; Deryng et al. (2014)','H is the crop-area and flowering-window weighted mean exceedance, averaged across 2001-24. T_eff=(monthly mean temperature + monthly maximum temperature)/2. The flowering window spans 45-70% of the crop season. Crop-specific Tcrit enters before aggregation. Divide by the fixed reference maximum to obtain E. The bars show saved equal-country crop-panel means, not global averages. A monthly value below threshold does not rule out damaging daily extremes. A low bar is not proof that the crop is safe. Stars refer to rice/rapeseed heat assumptions.');
formula(s,'heat',145,90);
text(s,'T_eff = (T_mean + T_max) / 2, during flowering',65,248,1120,45,28);
figure(s,'heat_exposure',30,310,750,350);
lines(s,['Monthly exceedance above a crop-specific threshold','Area-weighted where the crop grows','Bars: saved 2001-24 crop-panel means'],820,320,390,25,110);

s=slide('Water exposure: crop water demand unmet by rainfall','FAO-56 and FAO-66; code/05_country_series.py; saved index_components.csv','P is growing-season precipitation. ETc is crop evapotranspiration, estimated from reference evapotranspiration and crop coefficients. j denotes a crop grid cell, R rainfed area and A total crop area. Positive deficits enter only on rainfed land. The model assumes irrigation fully meets water demand, and has no soil-water storage or water-supply constraints. H averages over years and E divides by its fixed reference maximum. Bars use the saved E_water, averaged over each crop country panel. Rice has low modelled exposure partly because of irrigation.');
formula(s,'water',133,120);
text(s,'P: growing-season rain     ETc: crop water requirement',65,250,1120,45,28);
figure(s,'water_exposure',30,310,750,350);
lines(s,['R / A: rainfed share of crop area','Rain meets demand: deficit is zero','Irrigation fully buffers deficit in this model'],820,320,390,25,105);

s=slide('Sensitivity: crop response per unit stress','code/06_sensitivity.py and config.py; Deryng et al. (2014); FAO-66; parameter evidence register','The MAIN index now uses literature-based coefficients only, with declared proxies or derived transfers where evidence is incomplete. The mid-evaluation blended empirical formula is superseded. s_h describes fractional yield response per degree above threshold. For Deryng wheat the linear damage slope is 1/(35-25)=0.10 per degree; raw crop values are normalised to the panel maximum. Ky describes fractional yield loss per fractional water deficit: 1.25 corresponds to 12.5% loss for a 10% deficit in the simplified response. Empirical regressions are cross-checks only. Rice and rapeseed heat slopes lack support on our metric; rice Ky is borrowed and other species/chamber/calendar transfers remain. Normalised S has no yield-percent unit.');
formula(s,'sensitivity',145,90);
text(s,'Example: wheat s_h = 1 / (35 − 25) = 0.10 per °C',65,240,1140,40,24,C.muted);
figure(s,'sensitivity_profile',30,295,805,365);
lines(s,['s_h: response per degree C above threshold','K_y = 1.25: 10% deficit gives 12.5% yield loss','Main index: literature-based coefficients','* Heat proxies for rice and rapeseed'],875,290,340,23,92);

s=slide('Importance: dependence on a crop for five nutrients','FAOSTAT FBS/SUA 2021-23 and USDA composition; saved index_components.csv','For each crop-country pair, compute its share of energy, protein, fat, zinc and iron in total national food supply. I is the equal-weight average of those five shares. N_c,k,n is the crop nutrient contribution and N_k,n the national total. Divide I by a fixed panel maximum for the score. Equal weights are a project choice, not a biological claim that requirements have identical units. Oils are allocated correctly and pulse subitems are not double counted with FBS parents. Graph values are unnormalised I times100, averaged over each crop own country panel. Supply includes imports and is not measured consumption.');
formula(s,'importance',133,125);
figure(s,'importance_profile',30,295,750,365);
lines(s,['Crop contribution / national total = nutrient share','Energy, protein, fat, zinc and iron','Equal mean of five supply shares, including imports'],820,310,390,25,112);

s=slide('The paired climate and nutrition vulnerability index','Final report index definition; code/08_index.py and code/15_future_index.py','c denotes crop and k country. The mean of the paired heat and water terms multiplies normalised nutritional importance. Pairing avoids a heat exposure multiplying a water sensitivity. Relative F4 is a prioritisation score, never a yield-loss percentage. Compute within each crop-country pair first, then aggregate by equal-country or production weights. Present uses 2001-24 climate. Historical and future scores use the SAME saved normalisation reference, so differences reflect hazards rather than a moving scale. Future scores may exceed the original normalised range. The formula choice and equal hazard weights are project design choices.');
formula(s,'index',170,120);
lines(s,['E_h × S_h: heat contribution     E_w × S_w: water contribution','Multiply by normalised five-nutrient dependence I','Aggregate pairs using country or production weights','Reference = panel maximum, held fixed across comparison periods'],65,335,1130,28,75);
text(s,'F4 ranks vulnerability. A score of 0.05 does not mean 5% yield loss.',65,640,1130,40,26,C.orange,true);

s=slide('From crop losses to nutrient supply','code/09_yield_diet.py; code/16_future_yield_nutrition.py; CO2 extension','The index score is not the yield loss input. Separate crop response and loss accounting give a non-negative fractional production loss ell. Under upper pass-through, f=ell times clipped self-sufficiency production/domestic availability. For non-positive domestic supply with positive production the saved accounting uses the documented special handling rather than a negative ratio. Export buffering supplies a lower bound. q is the supported fractional concentration change, applied once to remaining supply. Crops or nutrients without evidence stay unchanged by scenario convention. The future quantity component models losses only and excludes CO2 yield gains.');
formula(s,'pass_through',160,110);
lines(s,['ℓ: production loss from the response model, independent of F4','f: supply loss after accounting for domestic production and trade','q: supported change in nutrient concentration','SSR = production / domestic supply. Other foods stay included.'],65,325,1130,29,85);

s=slide('Crop overview: cereals have the highest group score','Saved index_crop.csv; F4, equal-country weighting; assumption-dependent full nine-crop model','Walk through the bars without reading every value. Wheat is the highest score under equal-country weighting. Full nine-crop positions use borrowed assumptions, especially for rice and rapeseed. These values are relative within this panel and weighting. Do not interpret the score 0.056 as a 5.6% yield loss.');
let rank=[...d.index_crop].sort((a,b)=>b.F4_hazard_paired_eq-a.F4_hazard_paired_eq);chart(s,rank.map(r=>r.crop==='bean'?'Common bean':r.crop),[{name:'F4',values:rank.map(r=>r.F4_hazard_paired_eq),fill:C.blue}],{fmt:'0.000',max:.07});
text(s,'All nine crops shown. Scores use equal-country means within each crop panel.',65,625,1130,40,24,C.muted);

s=slide('Future overview: cereals lead and pulses increase','Saved future_crop.csv; figures/presentation/crop_trajectories.png','Open blue circles are the historical 1971-2000 reference; filled coral circles are 2041-60. Lines connect the same crop. Compare both equal-country and production weights: wheat remains highest, common bean rises, and other crops shift less. Full-model results include rice and rapeseed unsupported heat parameters, explicitly marked with stars. The axis is linear F4, not percentage yield change. Present 2001-24 is not the reference in this figure. Cereals remain the highest group. Pulses rise fastest proportionally under equal-country weights; cereals rise fastest proportionally under production weights. Group results remain conditional.');
figure(s,'crop_trajectories',45,145,1190,455);
text(s,'Cereals lead. Pulses rise fastest proportionally with equal-country weights.',65,625,1150,45,25,C.gold,true);

s=slide('Water dominates today; heat drives the projected change','Saved index_components.csv; report contribution shares; figures/presentation/stress_components.png','Stacked bars decompose present F4 into matched heat and water terms, averaged within each crop panel. This is a decomposition of index scores, not measured production loss. Across the report aggregation water supplies 91% of current score, while heat supplies 72% of historical-to-future change. The denominators differ. The future heat claim is one-model and parameter dependent. Rapeseed projected heat response is especially uncertain.');
figure(s,'stress_components',35,175,880,450);
text(s,'91%',960,210,260,110,76,C.blue,true);text(s,'water in the\npresent index',960,325,260,90,25);
text(s,'72%',960,435,260,110,76,C.orange,true);text(s,'heat in the\nprojected change',960,550,270,85,25);

s=slide('Nutrition overview: crops support different nutrients','Saved index_components.csv, nutrient shares, 2021-23; own-panel equal-country means','This is the general nutritional result before focusing on India. The cells show mean crop shares of each nutrient in that crop own country panel. They are not world population-weighted averages and cannot be added across different panels. Cereals contribute strongly to energy and protein, and wheat also to iron and zinc. Soybean, groundnut and rapeseed have a greater fat role, including edible oils. Pulses contribute protein and micronutrients but their national shares vary. This nutritional dependence explains why the most heat-sensitive crop need not have the highest F4. National supply is distinct from intake or health.');
figure(s,'nutrient_profiles',125,145,1030,465);
text(s,'Cereals support several nutrients. Oilseeds have a stronger fat role.',65,630,1140,45,27,C.gold,true);

s=slide('Nutrition overview: quantity and nutrient quality','Saved co2_nutrient_results.csv; present-relative quantity, primary FACE concentration effects; 20 countries','Show the broader nutritional result before the India case. For each nutrient, these bars are medians of the 20 national percentage changes, with every country weighted equally. The quantity-only medians are close to zero because the present-relative loss-only calculation affects a subset of selected crop-country pairs and excludes gains. Combined protein, zinc and iron medians are more negative after applying supported concentration effects. Medians are descriptive summaries, not population-weighted world changes. Energy and fat have no estimated CO2 concentration effect; equal bars do not establish biological immunity. Experimental treatment is 546-586 ppm and is not scaled to the scenario 507 ppm, so the combined result is a partial-evidence stress test, not a calibrated 2050 forecast.');
const nutrientFields=['pct_kcal','pct_protein','pct_fat','pct_zinc','pct_iron'];
// Six decimal places preserve far more detail than the two-decimal chart labels
// while fitting Excel's chart-workbook precision. Source CSVs remain unchanged.
const median=a=>{const b=[...a].sort((x,y)=>x-y);return Number(((b[9]+b[10])/2).toFixed(6));};
const quantityRows=d.co2_nutrient_results.filter(r=>r.scenario==='A future yield loss only (present-relative 2001-24 -> 2041-60)');
const combinedRows=d.co2_nutrient_results.filter(r=>r.scenario==='C combined quantity x concentration (present-relative 2001-24 -> 2041-60; primary)');
if(quantityRows.length!==20||combinedRows.length!==20) throw new Error('Expected 20 country results for the overview');
text(s,'Median national supply change across 20 countries (%)',65,145,1130,40,25,C.muted);
chart(s,['Energy','Protein','Fat','Zinc','Iron'],[{name:'Climate quantity',values:nutrientFields.map(c=>median(quantityRows.map(r=>r[c]))),fill:C.blue},{name:'Quantity + CO₂ quality',values:nutrientFields.map(c=>median(combinedRows.map(r=>r[c]))),fill:C.orange}],{y:205,h:365,legend:true,fmt:'0.00',categoryLabels:'low'});
text(s,'Energy/fat: quantity effects only. CO₂-quality effects remain unestimated.',65,605,1140,42,25,C.gold,true);
text(s,'Present-relative quantity + experimental quality stress test',65,660,1140,34,23,C.muted);

s=slide('Adequacy: nutrient supply relative to requirements','Saved adequacy.csv and combined scenarios; alternative bioavailability requirements','The capped MAR equation cannot detect a nutrient decline while national mean supply remains above its reference requirement. Seven of 20 countries are below the main iron requirement; none under the alternative assumptions. Do not equate this with seven countries having individual deficiency, or with observed anaemia. Supply is not intake.');
formula(s,'adequacy',155,110);text(s,'N: nutrient supply     R: requirement     MAR: mean capped adequacy',65,275,1130,35,24,C.muted);table(s,[['Iron supply below reference','Countries'],['Main requirement assumptions','7 of 20'],['Alternative bioavailability assumptions','0 of 20']],[880,270],330,215);text(s,'National mean supply cannot estimate the number of deficient people.',65,580,1110,45,26,C.orange);

s=slide('Where wheat vulnerability is concentrated','Saved index_components.csv and future_components.csv; Natural Earth 110m basemap; figures/presentation/PROVENANCE.md','Two country-level maps, not local crop grids. Left: F4 under observed 2001-24 climate. Russia is highest among the six selected wheat countries, then USA and India. Right: absolute F4 change from 1971-2000 to 2041-60; every selected wheat country increases. Values are index scores, never yield percentages. The two colour bars represent different quantities and must not be compared as though they share units or a common scale. Dark-grey countries were not evaluated for wheat, not assigned zero risk. Wheat remains first under country and production weighting; the restricted screen still retains some assumptions.');
figure(s,'wheat_maps',45,155,1190,480);

s=slide('India: wheat production is concentrated in a few states','Ministry of Agriculture, Agricultural Statistics at a Glance 2024-25, Table 2.5(b), p54, 2023-24 columns; geoBoundaries IND ADM1 2011, CC BY 2.5 IN; docs/evidence/INDIA_STATE_MAP_SOURCES.md','These are official observed state statistics, providing geographical context for the national model. They are not state F4 or future-loss estimates. Uttar Pradesh, Madhya Pradesh and Punjab supply 66.78% of wheat. The six largest producers supply 91.55% and each has over 95% of wheat area irrigated. Himachal Pradesh has 26.39% irrigation but only 0.69% production share. This illustrates why water exposure and national production importance should be considered jointly. Irrigation coverage does not establish reliable water supply, groundwater sustainability or immunity to heat. No state nutrient dependence or state climate losses have been inferred. Grey states are outside this ten-state table, not zero. Boundary reference is 2011. The national nine-crop nutrient shares remain 58% energy, 55.30% protein, 55.82% iron and 64.48% zinc.');
figure(s,'india_wheat_states',25,135,1230,445);
text(s,'UP + Madhya Pradesh + Punjab supply 66.8% of national wheat.',65,600,1150,45,28,C.gold,true);
text(s,'Top six states: >95% irrigated. Himachal: 26.4%, but only 0.7% of wheat.',65,660,1150,38,24,C.muted);


s=slide('CO₂ can reduce quality even when quantity is protected','Myers et al., Nature (2014), doi:10.1038/nature13179; primary FACE evidence','Explain FACE experiments: wheat, rice, maize and soybean supply 12 primary crop-nutrient effects. Nine are significant; nonsignificant estimates remain labelled and sensitivity variants are available. The experiments use 546–586 ppm versus the scenario 507 ppm in 2050. There is no justified dose-response scaling, so these are experimental stress tests, not precise 2050 predictions. Oils and unknown crop effects are untouched.');
lines(s,['12 primary effects: wheat, rice, maize and soybean','Protein, zinc and iron; energy/fat effects not estimated','Experimental treatment: 546–586 ppm CO₂','A partial-evidence stress test, not a calibrated 2050 forecast'],65,170,1120,30,100);

s=slide('India: quality changes add to quantity losses','Saved ext_co2_india.tex; present-relative climate variant; primary CO₂ effects; upper pass-through','Foreground the present-relative comparison. In India protein supply changes are -0.78% quantity, -2.96% quality and -3.72% combined; zinc -0.81,-3.85,-4.61; iron -1.03,-2.24,-3.25. These are national supply changes. The composite mean of the three combined changes is -3.86%. Quality is an experimental step, not scenario-scaled; uncertainties and uncovered effects remain.');
chart(s,['Protein','Zinc','Iron'],[{name:'Climate quantity',values:[-.78,-.81,-1.03],fill:C.blue},{name:'CO₂ quality',values:[-2.96,-3.85,-2.24],fill:C.gold},{name:'Combined',values:[-3.72,-4.61,-3.25],fill:C.orange}],{legend:true,fmt:'0.00'});text(s,'Change in national nutrient supply (%)',65,135,1000,30,20,C.muted);

s=slide('Food-source diversity: measure how supply is distributed','Final report: whole-FBS nutrient-source Shannon entropy; no FBS/SUA double counting','p is each food item share of a given nutrient, not the share of people eating that food. H captures distribution across fixed FBS categories and exp(H) is the number of equally contributing sources that would give the same entropy. It is not household dietary diversity or functional nutrient diversity. Unmeasured substitution is not assumed.');
formula(s,'diversity',180,120);lines(s,['p: an FBS food item’s share of a nutrient','Effective sources describe evenness of national supply.','Read diversity together with total supply and adequacy.'],65,350,1110,31,85);

s=slide('A diversity score can rise while iron supply falls','Saved diversity_after_losses.csv; B simultaneous -10% and C loss-only future historical-reference, upper pass-through','The scatterplot shows national iron supply change on the x-axis and change in effective iron sources on the y-axis. Blue circles are a simultaneous loss of 10% in each modelled crop of that country; coral squares are the future loss-only historical-reference scenario. All points are from saved outputs, not fitted associations or forecasts of consumer behaviour. Points above zero can have more even sources while total supply falls. The separate right-side example is India wheat alone: a 10% production shock reduces iron by 2.95% and increases effective sources by 0.58. Do not confuse that single-crop example with the simultaneous-loss points.');
figure(s,'diversity_scatter',20,165,900,465);
text(s,'Separate example',950,195,270,45,24,C.muted,true);text(s,'India: wheat -10%',950,245,270,65,24);
text(s,'-2.95%',950,330,270,75,48,C.orange,true);text(s,'national iron supply',950,405,270,60,22);
text(s,'+0.58',950,475,270,75,48,C.green,true);text(s,'effective iron sources',950,550,270,65,22);

s=slide('Literature provides support and useful challenges','Existing 39-row assessment + targeted follow-up; see docs/evidence/LITERATURE_FOLLOWUP.md','The initial comparison includes 24 publications and 39 crop-study rows. New research adds partial geographical evidence for 10 previously unmatched pairs: six regional yield and four suitability. Nineteen future comparisons remain unverified under this expanded search; this is not a systematic absence claim. Studies and pairs are not interchangeable counts. Mention wheat India, Tanzania beans, Canadian lentil and South African maize. Differences may arise from CO2 yield fertilisation, adaptation, daily extremes, soils, geography and reference periods. Trade matters for availability outcomes rather than automatically for biological yield. The follow-up adds 10 partial matches and leaves 19 future comparisons unverified. Agreement with shared input papers is not independent validation.');
table(s,[['Consistent conclusions','Challenges to our model'],['Wheat risk in India','Canadian lentil: CO₂/adaptation gains'],['Bean risk in Tanzania','South African maize: regional losses'],['Stress affects nutrient supply','Italian rice: baseline-sensitive direction']],[570,580],170,320);text(s,'Disagreement can reflect CO2, adaptation, geography and reference periods',65,545,1130,60,28,C.orange,true);

s=slide('Where the evidence still limits the results','Parameter evidence register; CO₂ coverage matrix; final report limitations','The screen is selective: removing unsupported heat slopes does not make all remaining borrowed inputs fully supported. No supported rice or rapeseed heat yield slope; bean India/Myanmar species mismatch; pulse calendar gaps. Future uses one GCM/scenario. Quality treatment lacks all-crop dose response. These are limitations of a finished study, not reasons to fabricate complete coverage.');
lines(s,['Crop response: unsupported slopes and species/calendar transfers','Future climate: one model, one scenario; no daily-extreme analysis','CO₂ quality: partial crops and nutrients; no calibrated dose response','Food system: fixed trade behaviour and diets; no household forecast'],65,170,1130,29,100);

s=slide('Three conclusions to take away','Earth 616 • Questions','Finish in 30 seconds. One: wheat is the clearest priority in this conditional screening framework. Two: nutrient concentration changes add a risk that yield alone misses. Three: food-source diversity can rise while nutrition worsens. Restate that the future results are scenarios and stress tests, not calibrated diet forecasts. Invite questions.');
lines(s,['1   Wheat is the clearest model priority.','2   Food quality adds risk beyond crop quantity.','3   Higher diversity can coexist with lower nutrient supply.'],65,185,1130,35,120);

s=slide('Climate exposure and comparison periods','Final report: climate methods','Use if asked about exposure. Normalisation uses fixed baseline references across periods. T_eff is based on monthly data around flowering and misses short hot spells. Water shortfall uses precipitation relative to crop evapotranspiration and rainfed share, not a soil-water model. Future delta method is MRI-ESM2-0 SSP245. Separate historical-to-future from present-relative changes.',true);formula(s,'hazard',165,110);lines(s,['Historical comparison: 1971–2000 → 2041–2060','Present-relative comparison: 2001–2024 → 2041–2060','Monthly data, fixed crop geography, calendars and irrigation'],65,330,1110,29,85);

s=slide('India: historical and present-relative comparisons','Saved ext_co2_india.tex; primary set and upper pass-through','Both use the same modern food supply and experimental quality treatment. The historical-reference version includes climate change already present in modern observations. Present-relative combined losses are smaller. Neither predicts future diets. Bracketed effect envelopes in the report are not full model confidence intervals.',true);table(s,[['Combined quantity + quality','Protein','Zinc','Iron'],['Historical-reference (%)','−4.45','−5.44','−4.20'],['Present-relative (%)','−3.72','−4.61','−3.25']],[610,180,180,180],200,250);

s=slide('Why studies disagree on yield, supply and diets','Saved model design; Snyder et al. (2020), doi:10.1371/journal.pone.0237918','First align baseline, geography, outcome and scenario. Yield differences may reflect CO2, phenology, daily extremes, soil water and cultivar adaptation. Trade and market responses affect production, supply and economics; they do not directly explain different biological temperature responses. Our model has static trade accounting but no endogenous future prices or trade. These are plausible explanations, not quantified causal attribution.',true);
table(s,[['Compared outcome','Relevant differences'],['Yield per hectare','CO₂, heat, water, cultivar, season length'],['Total production','Yield + planted area and management'],['National food availability','Imports, exports, stocks and processing'],['Consumption and health','Prices, income, access and intake']],[390,760],170,355);text(s,'Document model differences; do not invent a cause for each discrepancy.',65,555,1130,50,26,C.orange);

s=slide('Selected references','Full bibliography and source locators are in the final report and evidence registers','References supporting biological response, crop projections and trade discussion. The Myers study provides inputs, so comparison is not independent validation. The new literature follow-up records access limitations, including abstract-only readings.',true);lines(s,['Myers et al. (2014), Nature — 10.1038/nature13179','Jägermeyr et al. (2021), Nature Food — 10.1038/s43016-021-00400-y','Ferreira et al. (2023), Int. J. Biometeorol. — 10.1007/s00484-022-02392-1','Borges et al. (2023), Scientific Reports — 10.1038/s41598-023-38910-3','Snyder et al. (2020), PLOS ONE — 10.1371/journal.pone.0237918'],65,170,1130,25,78);
await fs.mkdir(out,{recursive:true});
// The bundled PDF exporter has an unavailable font alias on Windows.
// export_slides_pdf.py assembles the visually checked 1920x1080 renderings.
if(!process.argv.includes('--finalize-only')) {
await (await PresentationFile.exportPptx(P)).save(path.join(tmp,'candidate.pptx'));
await fs.writeFile(path.join(tmp,'notes.json'),JSON.stringify(notes,null,2));
for(let i=0;i<P.slides.items.length;i++){
 const blob=await P.export({slide:P.slides.items[i],format:'png',scale:1.5});
 await fs.writeFile(path.join(tmp,`slide-${String(i+1).padStart(2,'0')}.png`),new Uint8Array(await blob.arrayBuffer()));
 console.log('Rendered',i+1);
}
}
const skill='C:/Users/user/.codex/plugins/cache/openai-primary-runtime/presentations/26.1112.11217/skills/presentations';
const {finalizePresentation}=await import(pathToFileURL(skill+'/container_tools/artifact_tool_utils.mjs').href);
// Finalize each revision to a new path, preserving previously exported decks.
let finalName='Earth_616_Professor_Presentation_Overlap_Fixed.pptx';
try {
 await fs.access(path.join(out,finalName));
 finalName=`Earth_616_Professor_Presentation_${new Date().toISOString().replace(/[:.]/g,'-')}.pptx`;
} catch(error) {if(error.code!=='ENOENT') throw error;}
await fs.rm(path.join(tmp,'validation.json'),{force:true});
await finalizePresentation({workspaceDir:root,candidatePath:path.join(tmp,'candidate.pptx'),finalPath:path.join(out,finalName),pythonExecutable:runtime+'/python/python.exe',integrityValidatorPath:skill+'/container_tools/inspect_presentation_package_integrity.py',layoutValidatorPath:skill+'/container_tools/inspect_presentation_layout_geometry.py',layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-heading-fit',...[4,16,23,28].flatMap(n=>['--require-native-table-slide',String(n)])],fontPolicy:{basis:'design',families:['Arial','Arial Black']},requiredNativeChartOwnerSlides:[11,15,20],requiredNativeTableOwnerSlides:[4,16,23,28],materializeLiteralChartWorkbooks:true,verifyArtifactToolImport:true,receiptPath:path.join(tmp,'validation.json')});
console.log('Final PPTX exported; main talk seconds:',timings.reduce((a,b)=>a+b,0));
await fs.writeFile(path.join(tmp,'deliverables.json'),JSON.stringify({powerpoint:path.join(out,finalName),pdf:path.join(root,'docs/final_slides.pdf')}));
const {spawnSync}=await import('node:child_process');
const pdfResult=spawnSync(process.env.CNVI_PY || 'python',[path.join(root,'code/export_slides_pdf.py')],{stdio:'inherit'});
if(pdfResult.status!==0) throw new Error('Slide PDF assembly failed');
