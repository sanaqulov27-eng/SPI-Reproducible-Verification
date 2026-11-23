import pandas as pd, numpy as np, json, sys
P=sys.argv[1]; OUT=sys.argv[2]
d=pd.read_csv(P+'SPI_data.csv'); o=pd.read_csv(P+'SPI_index.csv')
d=d.sort_values(['country','date']).reset_index(drop=True); o=o.sort_values(['country','date']).reset_index(drop=True)
spi=[c for c in d.columns if c.startswith('SPI.')]
f='SPI.D4.3.GEO.first.admin.level'; s='SPI.D4.3.GEO.second.admin.level'
x=d[['country','iso3c','date']+spi].copy()
cond=x[f]<x[s]; x[f]=np.where(cond.isna(),np.nan,np.where(cond,x[s],x[f])); x=x.drop(columns=[s])
ind=[c for c in x.columns if c.startswith('SPI.')]
L=x.groupby('country')[ind].ffill()
raw_nonmiss=x[ind].notna(); fin_nonmiss=L.notna(); carried=fin_nonmiss&~raw_nonmiss
res={}
# 1 LOCF extent (exclude SPI.D3.NA artefact)
ind51=[c for c in ind if c!='SPI.D3.NA']
res['cells_final_nonmissing_52']=int(fin_nonmiss[ind].values.sum()); res['cells_carried_52']=int(carried[ind].values.sum())
res['cells_final_nonmissing_51']=int(fin_nonmiss[ind51].values.sum()); res['cells_carried_51']=int(carried[ind51].values.sum())
res['share_carried_51']=res['cells_carried_51']/res['cells_final_nonmissing_51']
# restricted to 2016-2024 (period of the overall index)
m=(x['date']>=2016).values
res['share_carried_51_2016_2024']=float(carried.loc[m,ind51].values.sum()/fin_nonmiss.loc[m,ind51].values.sum())
# by pillar group
grp={'P1':'SPI.D1','P2':'SPI.D2','P3':'SPI.D3','P4':'SPI.D4','P5':'SPI.D5'}
byp={}
for k,v in grp.items():
    cs=[c for c in ind51 if c.startswith(v+'.')]
    byp[k]=dict(indicators=len(cs),final=int(fin_nonmiss.loc[m,cs].values.sum()),carried=int(carried.loc[m,cs].values.sum()),share=float(carried.loc[m,cs].values.sum()/fin_nonmiss.loc[m,cs].values.sum()))
res['by_pillar_2016_2024']=byp
# idempotence of the 02-stage fill on the released indicator file
res['idempotence_cells_changed_by_ffill']=int((carried[ind].values).sum())
inter=0
for c in ind:
    inter+=int((x[c].isna() & x.groupby('country')[c].transform(lambda s:s.notna().cummax())).sum())
res['interior_gaps_in_released_indicator_file']=inter
# 2 missing-data reasons: rows without overall score
ov=o['SPI.INDEX'].notna().values
res['overall_records']=int(ov.sum())
no_ov=~ov
pill=['SPI.INDEX.PIL%d'%i for i in range(1,6)]
pm=o[pill].isna()
rows=o.loc[no_ov]
res['rows_without_overall']=int(no_ov.sum())
res['rows_without_overall_pre2016']=int((rows.date<2016).sum())
post=rows[rows.date>=2016]; res['rows_without_overall_2016plus']=int(len(post))
pmm=pm.loc[post.index]
# among 2016+ rows missing overall: which pillars are missing
sig=pmm.apply(lambda r:'+'.join([f'P{i+1}' for i,v in enumerate(r.values) if v]),axis=1)
res['missing_pillar_pattern_2016plus']=sig.value_counts().to_dict()
res['economies_never_overall']=int(o.groupby('iso3c')['SPI.INDEX'].apply(lambda s:s.notna().sum()==0).sum()); res['economies_total']=int(o.iso3c.nunique())
# economies lacking each pillar ever
res['economies_with_no_value_ever_by_pillar']={p:int(o.groupby('iso3c')[p].apply(lambda s:s.notna().sum()==0).sum()) for p in pill}
# structural start years of indicator groups (first year with any value in the raw file)
first={}
for k,v in grp.items():
    cs=[c for c in ind51 if c.startswith(v+'.')]
    first[k]=int(x.loc[x[cs].notna().any(axis=1),'date'].min())
res['first_year_any_raw_value_by_pillar']=first
# share of pre-2016 rows with value, by pillar (final)
pre=o['date']<2016
res['pre2016_rows']=int(pre.sum()); res['pre2016_nonmissing_by_pillar']={p:int(o.loc[pre,p].notna().sum()) for p in pill}
res['SPI.D3.NA_unique_values']=sorted(set(np.round(d['SPI.D3.NA'].dropna().unique(),6).tolist()))
# 4 geo rule effect: cells, countries, years; propagation if plain LOCF were used
plain=d.groupby('country')[f].ffill().values
off=o[f].values
dif=~(np.isclose(plain,off,atol=1e-12,equal_nan=True))
res['geo_cells_affected']=int(dif.sum()); res['geo_economies_affected']=int(o.loc[dif,'iso3c'].nunique()); res['geo_years_range']=[int(o.loc[dif,'date'].min()),int(o.loc[dif,'date'].max())]
res['geo_by_year']=o.loc[dif,'date'].value_counts().sort_index().to_dict()
res['geo_rows_affected_2016plus']=int((dif&(o.date>=2016).values).sum())
# propagation: recompute DIM4.3, P4, overall with plain LOCF
dim43=plain.copy(); p4_off=o['SPI.INDEX.PIL4'].values; dim43_off=o['SPI.DIM4.3.INDEX'].values
dd=np.abs(dim43-dim43_off); dd=np.where(np.isnan(dd),0,dd)
res['geo_dim43_rows_changed']=int((dd>1e-9).sum())
# P4 change = (1/4)/(1)*dim43 diff*100 ; overall change = P4change/5
p4d=dd*0.25*100; ovd=p4d/5
res['geo_P4_abs_change_if_plain']=dict(rows=int((p4d>1e-9).sum()),max=float(p4d.max()),mean_over_changed=float(p4d[p4d>1e-9].mean()))
ovmask=(p4d>1e-9)&ov
res['geo_overall_abs_change_if_plain']=dict(rows_with_overall=int(ovmask.sum()),max=float(ovd[ovmask].max()) if ovmask.any() else 0,mean=float(ovd[ovmask].mean()) if ovmask.any() else 0)
# which of the 165 are 2nd-admin dominant
cells=o.loc[dif,['iso3c','date']].assign(official=off[dif],plain_locf=plain[dif])
cells.to_csv(OUT+'geo_discrepancy_165_cells.csv',index=False)
res['geo_top_economies']=o.loc[dif,'iso3c'].value_counts().head(10).to_dict()
# 5 ranking 2024
r=o[(o.date==2024)&o['SPI.INDEX'].notna()][['iso3c','country','SPI.INDEX']].copy()
r['rank_min']=r['SPI.INDEX'].rank(ascending=False,method='min').astype(int)
r['rank_dense']=r['SPI.INDEX'].rank(ascending=False,method='dense').astype(int)
r['r2']=r['SPI.INDEX'].round(2); r['rank_min_rounded2']=r['r2'].rank(ascending=False,method='min').astype(int)
r['r1']=r['SPI.INDEX'].round(1); r['rank_min_rounded1']=r['r1'].rank(ascending=False,method='min').astype(int)
res['rank_n']=len(r); res['rank_exact_ties']=int(r['SPI.INDEX'].duplicated(keep=False).sum()); res['rank_ties_rounded2']=int(r['r2'].duplicated(keep=False).sum()); res['rank_ties_rounded1']=int(r['r1'].duplicated(keep=False).sum())
uz=r[r.iso3c=='UZB'].iloc[0]; res['UZB_rank']=dict(score=float(uz['SPI.INDEX']),rank_min=int(uz.rank_min),rank_dense=int(uz.rank_dense),rank_min_rounded2=int(uz.rank_min_rounded2),rank_min_rounded1=int(uz.rank_min_rounded1))
res['rank_changes_when_rounded2']=int((r.rank_min!=r.rank_min_rounded2).sum()); res['rank_changes_when_rounded1']=int((r.rank_min!=r.rank_min_rounded1).sum())
res['rank_max_shift_rounded2']=int((r.rank_min-r.rank_min_rounded2).abs().max())
nbr=r.sort_values('SPI.INDEX',ascending=False).reset_index(drop=True); i=nbr.index[nbr.iso3c=='UZB'][0]
res['UZB_neighbours']=nbr.loc[max(0,i-2):i+2,['iso3c','SPI.INDEX','rank_min']].round(4).to_dict('records')
r.drop(columns=['r1','r2']).to_csv(OUT+'rank_2024_188.csv',index=False)
json.dump(res,open(OUT+'descriptives.json','w'),indent=1,default=str)
print(json.dumps(res,indent=1,default=str))
