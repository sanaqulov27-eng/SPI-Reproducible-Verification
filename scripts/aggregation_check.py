"""Aggregation-only consistency check: pillar and overall scores recomputed from the PUBLISHED dimension-level scores
(SPI.DIM*.INDEX) with the fixed weights of 02-SPI_index.Rmd. This is a consistency check of the published output file,
not an independent reconstruction (see e2e_reconstruction.py for the stage-wise reconstruction from indicators)."""
import pandas as pd, numpy as np, sys
P, OUT = sys.argv[1], sys.argv[2]; TOL = 1e-9
o = pd.read_csv(P + 'SPI_index.csv')
r = pd.DataFrame({'country': o.country, 'iso3c': o.iso3c, 'date': o.date})
r['P1'] = o['SPI.DIM1.5.INDEX'] * 100
r['P2'] = o[['SPI.DIM2.1.INDEX', 'SPI.DIM2.2.INDEX', 'SPI.DIM2.4.INDEX']].mean(axis=1, skipna=False) * 100
r['P3'] = (6 * o['SPI.DIM3.1.INDEX'] + 6 * o['SPI.DIM3.2.INDEX'] + 2 * o['SPI.DIM3.3.INDEX'] + 2 * o['SPI.DIM3.4.INDEX']) / 16 * 100
r['P4'] = o[['SPI.DIM4.1.CEN.INDEX', 'SPI.DIM4.1.SVY.INDEX', 'SPI.DIM4.2.INDEX', 'SPI.DIM4.3.INDEX']].mean(axis=1, skipna=False) * 100
r['P5'] = o['SPI.DIM5.2.INDEX'] * 100
r['Overall'] = r[['P1', 'P2', 'P3', 'P4', 'P5']].mean(axis=1, skipna=False)
rows = []
for k, c in zip(['P1', 'P2', 'P3', 'P4', 'P5', 'Overall'], ['SPI.INDEX.PIL1', 'SPI.INDEX.PIL2', 'SPI.INDEX.PIL3', 'SPI.INDEX.PIL4', 'SPI.INDEX.PIL5', 'SPI.INDEX']):
    a, b = r[k].values, o[c].values
    both = np.isnan(a) & np.isnan(b); d = np.abs(a - b); ok = (d <= TOL) | both
    r[k + '_official'] = b; r[k + '_diff'] = a - b
    rows.append(dict(field=c, n_nonmissing=int((~both).sum()), n_match=int((ok & ~both).sum()), n_mismatch=int((~ok).sum()),
                     economies=int(o.loc[~np.isnan(b), 'iso3c'].nunique()), max_abs_diff=float(np.nanmax(d))))
pd.DataFrame(rows).to_csv(OUT + 'aggregation_check_summary.csv', index=False)
r.to_csv(OUT + 'aggregation_check_published_dimensions.csv', index=False)
print(pd.DataFrame(rows).to_string())
