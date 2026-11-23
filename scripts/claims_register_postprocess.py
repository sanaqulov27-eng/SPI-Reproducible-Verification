import pandas as pd, numpy as np, re, sys
import sys
IN,OUTF=sys.argv[1],sys.argv[2]  # input claims csv, output claims csv
c=pd.read_csv(IN)
from decimal import Decimal, ROUND_HALF_UP
def hu(x,d):
    # round half up, after removing floating-point noise (rounding to 10 decimals first)
    return float(Decimal(str(round(float(x),10))).quantize(Decimal(1).scaleb(-int(d)),rounding=ROUND_HALF_UP))
c['Actual_at_report_precision']=[hu(a,d) for a,d in zip(c.Actual_raw_WB,c.Decimals)]
c['Difference_at_report_precision']=(c.Expected_in_report-c.Actual_at_report_precision).round(10)
c['Status']=np.where(c.Difference_at_report_precision.abs()<1e-9,'PASS','FAIL')
def typ(m):
    if re.search(r'Global rank',m): return 'Rank'
    if re.search(r'23→24',m): return 'Year-on-year change'
    if re.match(r'SDG \d+',m): return 'SDG goal score'
    if re.match(r'SPI\.D5\.2',m): return 'Indicator score'
    if re.match(r'(4\.\d|Dim \d)',m): return 'Dimension score'
    if '—' in m: return 'Comparator pillar/overall score'
    return 'Pillar / overall score (Uzbekistan)'
c['Claim_type']=c.Metric.map(typ)
def tie(row):
    d=int(row.Decimals); a=float(row.Actual_raw_WB)
    if d==0: return False
    f=round(a,10)*10**d; return abs((f-np.floor(f))-0.5)<1e-6
c['Rounding_tie']=c.apply(tie,axis=1)
c['Note']=c['Note'].astype('object')
c['Status_category']=np.where(c.Status=='PASS','PASS','FAIL')
c.loc[c.Rounding_tie,'Note']=c.loc[c.Rounding_tie,'Note'].fillna('')+'Exact value (88.15) lies on a rounding boundary: round half up gives the value stated in the report; rounding the stored floating-point number (88.1499...) would give 88.1.'
print(c.Claim_type.value_counts()); print(c[c.Rounding_tie][['Report_location','Metric','Year','Expected_in_report','Actual_raw_WB','Actual_at_report_precision','Decimals']])
print(c.groupby(['Report_location','Claim_type']).size())
c.to_csv(OUTF,index=False,encoding='utf-8-sig')
