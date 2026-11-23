"""Quantify revisions of published SPI values between tagged releases v1.0-v4.0 (worldbank/SPI, 03_output_data/SPI_index.csv)."""
import pandas as pd, numpy as np, sys
V=['v1.0','v2.0','v3.0','v4.0']; IN=sys.argv[1]; OUT=sys.argv[2]; TOL=1e-6
D={v:pd.read_csv(f'{IN}SPI_index_{v}.csv').set_index(['iso3c','date']) for v in V}
F=['SPI.INDEX','SPI.INDEX.PIL1','SPI.INDEX.PIL2','SPI.INDEX.PIL3','SPI.INDEX.PIL4','SPI.INDEX.PIL5']
pairs=[('v1.0','v2.0'),('v2.0','v3.0'),('v3.0','v4.0'),('v1.0','v4.0'),('v2.0','v4.0')]
rows=[]
for a,b in pairs:
    for f in F:
        x=D[a][f]; y=D[b][f]; idx=x.dropna().index.intersection(y.dropna().index)
        dd=(y[idx]-x[idx]); ad=dd.abs(); rev=ad>TOL
        rows.append(dict(older=a,newer=b,field=f,n_common=len(idx),n_economies=len(set(i[0] for i in idx)),n_revised=int(rev.sum()),share_revised=rev.mean() if len(idx) else np.nan,
          mean_abs_all=ad.mean(),mean_abs_revised=ad[rev].mean() if rev.any() else 0,median_abs_revised=ad[rev].median() if rev.any() else 0,p90_abs_revised=ad[rev].quantile(.9) if rev.any() else 0,max_abs=ad.max(),mean_signed_revised=dd[rev].mean() if rev.any() else 0,n_up=int((dd>TOL).sum()),n_down=int((dd<-TOL).sum())))
S=pd.DataFrame(rows); S.to_csv(OUT+'vintage_revisions_summary.csv',index=False)
pd.set_option('display.width',250); pd.set_option('display.max_columns',30)
print(S[S.field=='SPI.INDEX'].round(3).to_string())
print(S[S.older.eq('v3.0')&S.newer.eq('v4.0')].round(3).to_string())
print(S[S.older.eq('v2.0')&S.newer.eq('v3.0')].round(3).to_string())
# persistence
x2,x3,x4=[D[v]['SPI.INDEX'] for v in ['v2.0','v3.0','v4.0']]
idx=x2.dropna().index.intersection(x3.dropna().index).intersection(x4.dropna().index)
r23=(x3[idx]-x2[idx]).abs()>TOL; r34=(x4[idx]-x3[idx]).abs()>TOL; back=((x4[idx]-x2[idx]).abs()<=TOL)&r23
print('common v2,v3,v4:',len(idx),'revised v2->v3:',int(r23.sum()),'of which revised again v3->v4:',int((r23&r34).sum()),'returned to v2 value:',int(back.sum()))
print('never revised across 3 releases:',int((~r23&~r34).sum()))
# long overall panel
L=pd.concat({v:D[v]['SPI.INDEX'] for v in V},axis=1); L=L.dropna(how='all').reset_index(); L.columns=['iso3c','year']+[f'SPI_overall_{v}' for v in V]
L.to_csv(OUT+'vintage_overall_panel.csv',index=False)
# indicator-level (post-LOCF indicator columns in SPI_index.csv): which indicators changed v3.0 -> v4.0
import re
ind=[c for c in D['v4.0'].columns if re.match(r'^SPI\.D\d',c)]
res=[]
for a,b in [('v2.0','v3.0'),('v3.0','v4.0')]:
    A=D[a]; B=D[b]; idx=A.index.intersection(B.index); cols=[c for c in ind if c in A.columns and c in B.columns]
    for c in cols:
        xa=A.loc[idx,c]; xb=B.loc[idx,c]; both=xa.notna()&xb.notna(); ch=((xa-xb).abs()>TOL)&both; newly=(xa.isna()&xb.notna()); lost=(xa.notna()&xb.isna())
        res.append(dict(older=a,newer=b,indicator=c,n_common=int(both.sum()),n_changed=int(ch.sum()),n_newly_available=int(newly.sum()),n_no_longer_available=int(lost.sum())))
R=pd.DataFrame(res); R.to_csv(OUT+'vintage_indicator_revisions.csv',index=False)
print(R[R.newer.eq('v4.0')].sort_values('n_changed',ascending=False).head(12).to_string())
print(R.groupby(['older','newer'])[['n_changed','n_newly_available','n_no_longer_available']].sum())
