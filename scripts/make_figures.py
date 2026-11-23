import pandas as pd, numpy as np, matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt, sys
import os
BASE=sys.argv[1]; OUT=sys.argv[2]  # BASE = package root
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.spines.top':False,'axes.spines.right':False})
col={'Overall':'#0b5a8a','P1':'#7f7f7f','P2':'#e08a2c','P3':'#3a9a55','P4':'#b83a3a','P5':'#7b4fa3'}
v3=pd.read_csv(BASE+'/raw_vintages/SPI_index_v3.0.csv'); v4=pd.read_csv(BASE+'/raw_vintages/SPI_index_v4.0.csv')
f=['SPI.INDEX','SPI.INDEX.PIL1','SPI.INDEX.PIL2','SPI.INDEX.PIL3','SPI.INDEX.PIL4','SPI.INDEX.PIL5']; nm=['Overall','P1','P2','P3','P4','P5']
u4=v4[v4.iso3c=='UZB'].set_index('date'); u3=v3[v3.iso3c=='UZB'].set_index('date')
yrs=list(range(2016,2025))
fig,ax=plt.subplots(figsize=(7.2,4.3),dpi=300)
for c,n in zip(f,nm):
    lw=2.6 if n=='Overall' else 1.1
    ax.plot(yrs,u4.loc[yrs,c],'-o',color=col[n],lw=lw,ms=4.5 if n=='Overall' else 3,label=n,alpha=1 if n=='Overall' else .8)
    y3=[y for y in range(2016,2024) if abs(u3.loc[y,c]-u4.loc[y,c])>1e-6]
    ax.plot(y3,u3.loc[y3,c],'o',mfc='white',mec=col[n],ms=6.5 if n=='Overall' else 5,mew=1.1,ls='none')
ax.plot([],[],'o',mfc='white',mec='k',ls='none',label='v3.0 value\n(where revised in v4.0)')
ax.set_xlabel('Year'); ax.set_ylabel('Score (0-100)'); ax.set_ylim(0,100); ax.set_xticks(yrs); ax.grid(alpha=.25)
ax.set_title('Uzbekistan: overall SPI and pillar scores, 2016-2024 (release v4.0)',fontsize=10)
ax.legend(ncol=4,fontsize=7.5,loc='lower right',frameon=True)
fig.tight_layout(); fig.savefig(OUT+'Figure1.png'); fig.savefig(OUT+'Figure1.pdf'); plt.close(fig)
# Figure 2
E=pd.read_csv(BASE+'/results/e2e_field_summary.csv')
st=['1 indicator (after geospatial rule + LOCF)','2 dimension','3 pillar','4 overall']
lab={st[0]:'Indicators\n(52 fields)',st[1]:'Dimensions\n(15 fields)',st[2]:'Pillars\n(5 fields)',st[3]:'Overall\n(1 field)'}
fig,(a,b)=plt.subplots(1,2,figsize=(8.0,3.9),dpi=300,gridspec_kw={'width_ratios':[1.4,1]})
floor=1e-17; rng=np.random.default_rng(1)
for i,s in enumerate(st):
    d=E[E.stage==s]; y=d.max_abs_diff.replace(0,floor).values; x=i+rng.uniform(-.2,.2,len(y))
    ex=d.max_abs_diff.values==0
    a.scatter(x[~ex],y[~ex],s=14,color='#0b5a8a',alpha=.85,zorder=3)
    a.scatter(x[ex],y[ex],s=14,facecolor='white',edgecolor='#0b5a8a',alpha=.9,zorder=3)
a.set_yscale('log'); a.set_ylim(5e-18,1e-6); a.axhline(1e-9,color='#b83a3a',ls='--',lw=1); a.text(3.45,1.6e-9,'tolerance 1e-9',color='#b83a3a',ha='right',fontsize=7.5)
a.set_xticks(range(4)); a.set_xticklabels([lab[s] for s in st],fontsize=7.5); a.set_ylabel('Maximum absolute difference per field')
a.text(3.45,7e-18,'open circles: difference exactly 0',fontsize=7,ha='right')
a.set_title('a  Largest difference per field',loc='left',fontsize=9); a.grid(alpha=.25,axis='y')
g=E.groupby('stage').agg(n=('n_nonmissing','sum'),mm=('n_mismatch','sum')).loc[st]
b.bar(range(4),g.n,color='#3a9a55'); 
for i,(n,m) in enumerate(zip(g.n,g.mm)): b.text(i,n*1.15,f'{n:,}\n{m} mism.',ha='center',va='bottom',fontsize=7)
b.set_yscale('log'); b.set_ylim(1000,1.2e6); b.set_xticks(range(4)); b.set_xticklabels(['Indic.','Dim.','Pillars','Overall'],fontsize=7.5)
b.set_ylabel('Non-missing cells compared'); b.set_title('b  Cells compared per stage',loc='left',fontsize=9)
fig.tight_layout(); fig.savefig(OUT+'Figure2.png'); fig.savefig(OUT+'Figure2.pdf'); plt.close(fig)
# Figure 3
R=pd.read_csv(BASE+'/results/vintage_revisions_summary.csv')
fig,(a,b)=plt.subplots(1,2,figsize=(7.4,3.6),dpi=300)
pairs=[('v1.0','v2.0'),('v2.0','v3.0'),('v3.0','v4.0')]; w=.26
for j,(o_,n_) in enumerate(pairs):
    d=R[(R.older==o_)&(R.newer==n_)].set_index('field').loc[f]
    a.bar(np.arange(6)+(j-1)*w,d.share_revised*100,w,label=f'{o_} to {n_}',color=['#9ecae1','#4292c6','#08519c'][j])
a.set_xticks(range(6)); a.set_xticklabels(nm); a.set_ylabel('Country-years revised (%)'); a.legend(fontsize=7.5); a.grid(alpha=.25,axis='y'); a.set_title('a  Share of published values revised',loc='left',fontsize=9)
x3=v3.set_index(['iso3c','date'])['SPI.INDEX']; x4=v4.set_index(['iso3c','date'])['SPI.INDEX']
idx=x3.dropna().index.intersection(x4.dropna().index); dd=(x4[idx]-x3[idx])
b.hist(dd,bins=np.arange(-8.5,8.6,.5),color='#08519c'); b.set_yscale('log'); b.set_xlabel('Revision of overall score, v4.0 minus v3.0 (points)'); b.set_ylabel('Country-years'); b.grid(alpha=.25,axis='y')
b.set_title(f'b  Overall score, n = {len(idx):,}',loc='left',fontsize=9)
fig.tight_layout(); fig.savefig(OUT+'Figure3.png'); fig.savefig(OUT+'Figure3.pdf'); plt.close(fig)
print('ok',(dd.abs()>1e-6).sum(),len(dd))
