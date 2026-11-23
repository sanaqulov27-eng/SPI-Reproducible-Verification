"""Build uzbekistan_claims_register.xlsx (static values) from results/*.csv. Usage: python build_xlsx.py PACKAGE_ROOT"""
import sys, pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter
R = sys.argv[1].rstrip('/') + '/'
c = pd.read_csv(R + 'results/project_claims_audit.csv')
rk = pd.read_csv(R + 'results/rank_2024_188.csv')
rv = pd.read_csv(R + 'results/vintage_revisions_summary.csv')
wb = Workbook(); ws = wb.active; ws.title = 'README'
info = [
 ('Claims register: Uzbekistan SPI v4.0', ''),
 ('Release', 'World Bank SPI v4.0, commit 2dd02f746cb4e2159281adc74d6865f948e90ce1'),
 ('Source file', '03_output_data/SPI_index.csv (SHA-256 in source_hashes.csv)'),
 ('Scope', 'Numerical statements in the Foreword and Tables 4-9 of one national report (unpublished, Uzbek) that map to a field of SPI_index.csv. Not every number in the report.'),
 ('Rule', 'Pinned value rounded (from its stored floating-point value) to the number of decimals used in the report and compared with the stated value.'),
 ('Status_category', 'PASS, FAIL, VINTAGE_DIFFERENCE or NOT_VERIFIABLE. In this register all 251 claims are PASS (1 flagged Rounding_tie).'),
 ('Ranks', 'Descending over the 188 economies with a non-missing 2024 overall score; ties share the lowest rank (see Rank_2024).'),
 ('Not a forecast', 'Nothing in this workbook is a forecast of future World Bank releases.'),
 ('Full documentation', 'See the Data Descriptor and README.md of the package.'),
]
for r in info: ws.append(r)
ws['A1'].font = Font(bold=True, size=13); ws.column_dimensions['A'].width = 22; ws.column_dimensions['B'].width = 110
for row in ws.iter_rows(min_row=2):
    row[0].font = Font(bold=True); row[1].alignment = Alignment(wrap_text=True, vertical='top')
def sheet(name, df):
    s = wb.create_sheet(name); s.append(list(df.columns))
    for r in df.itertuples(index=False): s.append([None if (isinstance(v, float) and pd.isna(v)) else (bool(v) if hasattr(v, 'dtype') and v.dtype == bool else v) for v in r])
    for i, col in enumerate(df.columns, 1):
        s.cell(1, i).font = Font(bold=True); s.cell(1, i).fill = PatternFill('solid', fgColor='DCE6F1')
        w = max([len(str(col))] + [len(str(v)) for v in df[col].head(300)]); s.column_dimensions[get_column_letter(i)].width = min(60, w + 2)
    s.freeze_panes = 'A2'
sheet('Claims_Register', c)
t = c.groupby(['Claim_type', 'Report_location']).agg(Claims=('Status', 'size'), PASS=('Status_category', lambda x: (x == 'PASS').sum()), Rounding_ties=('Rounding_tie', 'sum')).reset_index()
sheet('Summary_by_type', t)
sheet('Rank_2024', rk)
sheet('Revisions_summary', rv)
wb.save(R + 'uzbekistan_claims_register.xlsx'); print('xlsx written')
