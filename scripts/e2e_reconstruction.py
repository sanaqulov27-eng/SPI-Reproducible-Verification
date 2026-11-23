"""End-to-end reconstruction of the World Bank SPI v4.0 from the indicator-level file.
Stages: (0) geospatial pre-rule -> (1) LOCF per economy -> (2) dimension means -> (3) pillars -> (4) overall.
Mirrors 02-SPI_index.Rmd lines 1307-1447 of the pinned commit. Compared at EVERY stage to SPI_index.csv."""
import pandas as pd, numpy as np, json, sys
P=sys.argv[1]; OUT=sys.argv[2]; TOL=1e-9
d=pd.read_csv(P+'SPI_data.csv'); o=pd.read_csv(P+'SPI_index.csv')
d=d.sort_values(['country','date']).reset_index(drop=True); o=o.sort_values(['country','date']).reset_index(drop=True)
assert (d[['country','date']].values==o[['country','date']].values).all()
spi=[c for c in d.columns if c.startswith('SPI.')]
f='SPI.D4.3.GEO.first.admin.level'; s='SPI.D4.3.GEO.second.admin.level'
x=d[['country','date']+spi].copy()
cond=x[f]<x[s]                                   # R: if_else(first<second, second, first); NA -> NA
x[f]=np.where(cond.isna(),np.nan,np.where(cond,x[s],x[f]))
x=x.drop(columns=[s])
ind=[c for c in x.columns if c.startswith('SPI.')]
L=x.groupby('country')[ind].ffill()               # na.locf(na.rm=FALSE) within economy, ordered by year
rm=lambda cols: L[cols].mean(axis=1,skipna=False) # rowMeans(na.rm=FALSE)
sw=lambda c: [k for k in ind if k.startswith(c)]
D=pd.DataFrame(index=L.index)
D['SPI.DIM1.5.INDEX']=rm(sw('SPI.D1.5'))
D['SPI.DIM2.1.INDEX']=rm(sw('SPI.D2.1'))
D['SPI.DIM2.2.INDEX']=L['SPI.D2.2.Openness.subscore']
D['SPI.DIM2.4.INDEX']=L['SPI.D2.4.NADA']
D['SPI.DIM3.1.INDEX']=rm(['SPI.D3.1.POV','SPI.D3.2.HNGR','SPI.D3.3.HLTH','SPI.D3.4.EDUC','SPI.D3.5.GEND','SPI.D3.6.WTRS'])
D['SPI.DIM3.2.INDEX']=rm(['SPI.D3.7.ENRG','SPI.D3.8.WORK','SPI.D3.9.INDY','SPI.D3.10.NEQL','SPI.D3.11.CITY','SPI.D3.12.CNSP'])
D['SPI.DIM3.3.INDEX']=rm(['SPI.D3.13.CLMT','SPI.D3.15.LAND'])
D['SPI.DIM3.4.INDEX']=rm(['SPI.D3.16.INST','SPI.D3.17.PTNS'])
D['SPI.DIM4.1.CEN.INDEX']=rm(['SPI.D4.1.1.POPU','SPI.D4.1.2.AGRI','SPI.D4.1.3.BIZZ'])
D['SPI.DIM4.1.SVY.INDEX']=rm(['SPI.D4.1.4.HOUS','SPI.D4.1.5.AGSVY','SPI.D4.1.6.LABR','SPI.D4.1.7.HLTH','SPI.D4.1.8.BZSVY'])
D['SPI.DIM4.2.INDEX']=rm(sw('SPI.D4.2'))
D['SPI.DIM4.3.INDEX']=rm(sw('SPI.D4.3'))
D['SPI.DIM5.1.INDEX']=rm(sw('SPI.D5.1')).fillna(-99)
D['SPI.DIM5.2.INDEX']=rm(sw('SPI.D5.2'))
D['SPI.DIM5.5.INDEX']=rm(sw('SPI.D5.5')).fillna(-99)
w=dict(p=1/5,d21=1/3,d22=1/3,d24=1/3,d3=1/16,c=1/4,sv=1/4,a=1/4,g=1/4,d51=0.0,d52=1.0,d55=0.0)
p2t=w['d21']+w['d22']+w['d24']
sdg=['SPI.D3.1.POV','SPI.D3.2.HNGR','SPI.D3.3.HLTH','SPI.D3.4.EDUC','SPI.D3.5.GEND','SPI.D3.6.WTRS','SPI.D3.7.ENRG','SPI.D3.8.WORK','SPI.D3.9.INDY','SPI.D3.10.NEQL','SPI.D3.11.CITY','SPI.D3.12.CNSP','SPI.D3.13.CLMT','SPI.D3.15.LAND','SPI.D3.16.INST','SPI.D3.17.PTNS']
p3t=sum([w['d3']]*16); p4t=w['c']+w['sv']+w['a']+w['g']; p5t=w['d51']+w['d52']+w['d55']; pt=5*w['p']
D['SPI.INDEX.PIL1']=D['SPI.DIM1.5.INDEX']
D['SPI.INDEX.PIL2']=(w['d21']/p2t)*D['SPI.DIM2.1.INDEX']+(w['d22']/p2t)*D['SPI.DIM2.2.INDEX']+(w['d24']/p2t)*D['SPI.DIM2.4.INDEX']
acc=0
for c in sdg: acc=acc+(w['d3']/p3t)*L[c]
D['SPI.INDEX.PIL3']=acc
D['SPI.INDEX.PIL4']=(w['c']/p4t)*D['SPI.DIM4.1.CEN.INDEX']+(w['sv']/p4t)*D['SPI.DIM4.1.SVY.INDEX']+(w['a']/p4t)*D['SPI.DIM4.2.INDEX']+(w['g']/p4t)*D['SPI.DIM4.3.INDEX']
D['SPI.INDEX.PIL5']=(w['d51']/p5t)*D['SPI.DIM5.1.INDEX']+(w['d52']/p5t)*D['SPI.DIM5.2.INDEX']+(w['d55']/p5t)*D['SPI.DIM5.5.INDEX']
D['SPI.INDEX']=sum((w['p']/pt)*D[f'SPI.INDEX.PIL{k}'] for k in range(1,6))
for c in [k for k in D.columns if k.startswith('SPI.INDEX')]: D[c]=100*D[c]
R=pd.concat([L,D],axis=1)
def cmp(a,b):
    both=np.isnan(a)&np.isnan(b); one=np.isnan(a)^np.isnan(b)
    diff=np.abs(a-b); ok=(diff<=TOL)|both
    n=int((~np.isnan(a)|~np.isnan(b)).sum())            # cells where at least one side is non-missing
    return dict(n_cells=len(a),n_both_missing=int(both.sum()),n_nonmissing=int((~both).sum()),n_match=int(ok.sum()-both.sum()),n_mismatch=int((~ok).sum()),n_na_mismatch=int(one.sum()),max_abs_diff=float(np.nanmax(diff)) if np.isfinite(diff).any() else 0.0)
rows=[]
stage={**{c:'1 indicator (after geospatial rule + LOCF)' for c in ind},**{c:'2 dimension' for c in D.columns if 'DIM' in c},**{c:'3 pillar' for c in D.columns if 'PIL' in c},'SPI.INDEX':'4 overall'}
for c in R.columns:
    r=cmp(R[c].values.astype(float),o[c].values.astype(float)); r.update(field=c,stage=stage[c]); rows.append(r)
S=pd.DataFrame(rows)[['stage','field','n_cells','n_nonmissing','n_match','n_mismatch','n_na_mismatch','max_abs_diff']]
S.to_csv(OUT+'e2e_field_summary.csv',index=False)
print(S.groupby('stage').agg(fields=('field','count'),nonmissing=('n_nonmissing','sum'),match=('n_match','sum'),mismatch=('n_mismatch','sum'),na_mis=('n_na_mismatch','sum'),maxdiff=('max_abs_diff','max')))
print(S[S.n_mismatch>0])
out=pd.concat([o[['country','iso3c','date']],R[[k for k in D.columns]].add_prefix('RECON_')],axis=1)
out.to_csv(OUT+'e2e_reconstruction_full_panel.csv',index=False)
# coverage
cov={}
for c in ['SPI.INDEX.PIL1','SPI.INDEX.PIL2','SPI.INDEX.PIL3','SPI.INDEX.PIL4','SPI.INDEX.PIL5','SPI.INDEX']:
    m=o[c].notna(); cov[c]=dict(n=int(m.sum()),economies=int(o.loc[m,'iso3c'].nunique()),first_year=int(o.loc[m,'date'].min()),last_year=int(o.loc[m,'date'].max()))
print(json.dumps(cov,indent=1))
json.dump(cov,open(OUT+'coverage.json','w'),indent=1)
