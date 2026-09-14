# World Bank SPI v4.0 — Reproducible Verification Framework

A fully reproducible verification framework for the World Bank's Statistical Performance
Indicators (SPI). It (1) independently reconstructs the SPI aggregation formulas and
validates them against the **entire pinned v4.0 panel** — 1,613 country-year records with
a published overall score across **188 economies** (2016–2024), plus per-pillar coverage
back to 2004 — and (2) provides a **fully audited country-level case study for Uzbekistan**,
with a structured register of 251 individually checked numerical claims drawn from a
national policy report.

This repository accompanies a Scientific Data descriptor (manuscript in preparation).

## Two layers of validation

| Layer | Scope | What it proves |
|---|---|---|
| **Full-panel reconstruction** | All 188 economies with a published overall SPI score, 2016–2024 (1,613 records); per-pillar coverage 2004–2024 (217 economies) | The SPI's fixed-weight aggregation formulas, independently re-implemented in Python from the pinned R source, reproduce the official pillar and overall scores to floating-point precision. |
| **Full-panel LOCF replication** | 52 raw indicator fields × 4,557 country-year rows | The official missing-data rule (last-observation-carried-forward) is replicated indicator-by-indicator; 51/52 fields match exactly, and the one exception is disclosed as a known limitation rather than concealed. |
| **Uzbekistan claims audit** | 251 individually checked numerical claims from a national policy report | Every pillar/dimension score, historical figure, SDG value, international comparator, and scenario calculation cited in the report is checked against the pinned source and marked PASS/FAIL. |

## Contents

| File | Description |
|---|---|
| `verification_notebook.ipynb` | Executable Python (Jupyter/Colab) notebook implementing the full pipeline: retrieves the pinned SPI v4.0 source, reconstructs the aggregation formulas for the full panel, replicates LOCF, and audits the Uzbekistan claims register. Parameterised by ISO3 country code and pinned commit SHA. |
| `full_panel_reconstruction.csv` | Independently reconstructed P1–P5 and overall SPI for all 4,557 country-year records in the pinned release (217 economies, 2004–2024); overall-score columns are `NA` where no official overall score is published (see `full_panel_validation_summary.csv` for the 1,613-record subset used for overall-score validation). |
| `full_panel_validation_summary.csv` | Per-pillar and overall match-rate summary (n, match rate, maximum absolute difference). |
| `project_claims_audit.csv` | 251-row register of numerical claims from the Uzbekistan policy report; see the data dictionary in the manuscript (Table 1). |
| `uzbekistan_claims_register.xlsx` | The same Uzbekistan claims register with additional cross-reference sheets (pillar dynamics, SDG-level detail, international comparison, scenarios), for non-technical review. |
| `source_hashes.csv` | SHA-256 checksums, byte counts, and retrieval URLs for the pinned source files. |
| `audit_log.csv` | Log of methodological and schema checks (formula reconstruction, LOCF verification, R-source pattern matches). |
| `audit_manifest.json` | Machine-readable manifest recording the pinned release tag, commit SHA, and execution timestamp (UTC). |
| `AUDIT_SUMMARY.html` | Short human-readable audit summary. |
| `interactive_panel.html` | Self-contained interactive dashboard for the Uzbekistan case study (trend, pillar decomposition, SDG detail, international comparison, scenarios). |

## Data source

All figures derive from the World Bank's public SPI GitHub repository, release **v4.0**,
pinned at commit
[`2dd02f746cb4e2159281adc74d6865f948e90ce1`](https://github.com/worldbank/SPI/tree/2dd02f746cb4e2159281adc74d6865f948e90ce1).
Pinning to this exact commit (rather than the mutable `master` branch) ensures the figures
in this package remain reproducible even if the World Bank later revises historical rows
in a subsequent release.

- Source repository: https://github.com/worldbank/SPI
- Pinned data file: `03_output_data/SPI_index.csv`
- Pinned aggregation code: `02_programs/02-SPI_index.Rmd`

## How to reproduce

1. Open `verification_notebook.ipynb` in Google Colab or a local Jupyter environment
   (Python ≥3.10; requires `pandas`, `numpy`, `requests`).
2. Run all cells. The notebook downloads the pinned source files directly from GitHub
   at runtime — no manual data entry is required.
3. The notebook reproduces every value in this README and in the accompanying manuscript,
   including the full-panel reconstruction, the LOCF replication, and the Uzbekistan
   claims register, and writes an evidence pack with SHA-256-verified provenance.

## Applying the framework to another country

The claims-audit layer is parameterised by ISO3 country code (`COUNTRY_ISO` in the
notebook). To audit another country's policy report against the same pinned SPI release,
supply the report's numerical claims in the same format as `project_claims_audit.csv`
and re-run the comparison cells. The full-panel reconstruction already covers all 188
economies and does not need to be re-run per country.

## Citation

If you use this package, please cite it as below (see also `CITATION.cff`):

> Sanakulov, O. World Bank SPI v4.0 — Reproducible Verification Framework
> (Version v1.0.0) [Computer software]. Zenodo (2026).
> https://doi.org/[DOI to be assigned on first release]

and the underlying World Bank SPI data:

> World Bank. Statistical Performance Indicators (SPI), release v4.0.
> https://github.com/worldbank/SPI (commit `2dd02f746cb4e2159281adc74d6865f948e90ce1`).

## Version history note

This repository supersedes an earlier, Uzbekistan-only release of the same underlying
audit (`sanaqulov27-eng/Uzbekistan-SPI-verification`, DOIs
[10.5281/zenodo.22743529](https://doi.org/10.5281/zenodo.22743529) through
[10.5281/zenodo.22747762](https://doi.org/10.5281/zenodo.22747762)). That repository's
version history is preserved as-is and remains independently citable; this repository
is the current, actively maintained package and expands the scope from a single-country
case study to a full-panel (188-economy) independent reconstruction, with Uzbekistan
retained as the detailed, indicator-level audit example.

## License

Code and analysis in this repository: MIT License (see `LICENSE`).
Underlying World Bank SPI data is licensed under CC BY 4.0 by the World Bank.

## Author

Otaniyoz Sanakulov ([ORCID: 0009-0005-2274-112X](https://orcid.org/0009-0005-2274-112X)),
National Statistics Committee of the Republic of Uzbekistan.
Contact: sanaqulov27@gmail.com
