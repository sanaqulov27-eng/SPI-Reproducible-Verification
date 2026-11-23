# World Bank SPI v4.0: Reproducible Verification Framework (v1.1.0)

Verification layer for the World Bank Statistical Performance Indicators (SPI), release v4.0
(commit `2dd02f746cb4e2159281adc74d6865f948e90ce1`). Accompanies the Scientific Data Data Descriptor
*Reproducible verification of World Bank Statistical Performance Indicators: a stage-wise reconstruction of SPI v4.0*.

## What it does

1. **Stage-wise reconstruction.** From the indicator file `SPI_data.csv` it reconstructs the geospatial pre-rule,
   a forward-fill check, 15 dimension components, 5 pillars and the overall score, and compares every one of the
   73 output fields with `SPI_index.csv` (absolute tolerance 1e-9; NA vs NA counts as a match).
   Result: 240,900 cells compared, 0 mismatches. This is a consistency check of the published pipeline. It does not
   assess the quality of the underlying statistics, and the upstream R program that builds `SPI_data.csv`
   (`01-SPI_data_prep.Rmd`) is not re-executed.
2. **Revisions across releases** v1.0 to v4.0 (overall score, pillars, indicators).
3. **Geospatial rule, coverage and rank sensitivity** (165 cells; missing-value structure; ties and rounding).
4. **Claims register** (Uzbekistan, 251 numerical claims from an unpublished national report, with claim type and status category).

## Run

```
pip install -r requirements.txt          # Python 3.13
python scripts/run_all.py                # offline: hashed copies in raw_pinned/ and raw_vintages/
python scripts/run_all.py --online       # re-downloads the same files from the pinned commit/tags, verifies SHA-256
docker build -t spi-verify . && docker run --rm -v "$PWD/results:/pkg/results" spi-verify   # container (see note)
```

Every input is verified against `source_hashes.csv` before any analysis; the run stops on a mismatch.
`run_all.py` regenerates `results/`, `figures/` and `uzbekistan_claims_register.xlsx`. The results shipped in this
package are byte-identical to a fresh offline run.

Note: the Dockerfile was written but has not been built by the author of this package; if it fails, use the
`pip install` route, which was tested.

## Contents

| Path | Content |
|---|---|
| `raw_pinned/` | Unmodified World Bank files at the pinned commit, plus LICENSE (CC BY 4.0) |
| `raw_vintages/` | `SPI_index.csv` and `02-SPI_index.Rmd` of tags v1.0 to v4.0 |
| `source_hashes.csv` | URL, bytes, SHA-256 of every input |
| `results/e2e_reconstruction_full_panel.csv` | 4,557 country-years: reconstructed vs official dimensions, pillars, overall |
| `results/e2e_field_summary.csv` | Per-field matches, mismatches, max difference (73 fields) |
| `results/aggregation_check_*.csv` | Simpler check from published dimension columns |
| `results/geo_discrepancy_165_cells.csv` | Cells affected by the geospatial rule |
| `results/vintage_*.csv` | Release-to-release revisions |
| `results/rank_2024_188.csv` | 2024 ranks under three conventions |
| `results/coverage.json`, `descriptives.json` | Coverage counts, missing-value structure, rank statistics |
| `results/project_claims_audit.csv` | 251-claim register (Claim_type, Rounding_tie, Status_category) |
| `claims/claims_input_original.csv` | Register input before post-processing |
| `uzbekistan_claims_register.xlsx` | Register with summary sheets |
| `figures/` | Figures 1 to 3 of the paper |
| `scripts/` | All code; `verification_notebook.ipynb` walks through it |

## Licences

Code: MIT. Tables derived by the author: CC BY 4.0. World Bank files (`raw_pinned/`, `raw_vintages/`) are redistributed
unmodified under the World Bank's CC BY 4.0 licence (https://github.com/worldbank/SPI). The register contains only
numbers and labels extracted from the report, not report text.

## Limitations

Arithmetic and consistency only; not data quality. One economy and one report in the worked example.
Causes of revisions are not attributed. See the paper.
