"""Run every analysis of the SPI verification package and regenerate results/ and figures/.

Usage:
  python scripts/run_all.py                # offline: uses the hashed copies in raw_pinned/ and raw_vintages/
  python scripts/run_all.py --online       # downloads the same files from the pinned GitHub commit/tags, verifies SHA-256, then runs
  python scripts/run_all.py --out DIR      # write results to DIR instead of results/ (figures go to DIR/../figures_<name> if not default)
"""
import argparse, csv, hashlib, json, os, platform, subprocess, sys, datetime, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ap = argparse.ArgumentParser()
ap.add_argument('--online', action='store_true')
ap.add_argument('--out', default=os.path.join(ROOT, 'results'))
a = ap.parse_args()
OUT = os.path.abspath(a.out).rstrip('/') + '/'
FIG = (os.path.join(ROOT, 'figures') if os.path.abspath(a.out) == os.path.join(ROOT, 'results') else os.path.join(os.path.abspath(a.out), 'figures')).rstrip('/') + '/'
os.makedirs(OUT, exist_ok=True); os.makedirs(FIG, exist_ok=True)

def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''): h.update(b)
    return h.hexdigest()

rows = list(csv.DictReader(open(os.path.join(ROOT, 'source_hashes.csv'), encoding='utf-8-sig')))
base = ROOT
if a.online:
    base = os.path.join(ROOT, 'online_copy'); 
    for r in rows:
        dst = os.path.join(base, r['file']); os.makedirs(os.path.dirname(dst), exist_ok=True)
        urllib.request.urlretrieve(r['url'], dst)
bad = []
for r in rows:
    p = os.path.join(base, r['file'])
    ok = os.path.exists(p) and sha(p) == r['sha256']
    print(('OK  ' if ok else 'FAIL'), r['file'])
    if not ok: bad.append(r['file'])
if bad:
    sys.exit('Hash verification failed for: ' + ', '.join(bad) + '. Stopping.')

PD = os.path.join(base, 'raw_pinned') + '/'; VD = os.path.join(base, 'raw_vintages') + '/'
py = sys.executable; sc = os.path.join(ROOT, 'scripts')
def run(*args):
    print('>>', ' '.join(os.path.basename(x) if i == 1 else x for i, x in enumerate(args)))
    subprocess.run([py, *args], check=True, stdout=subprocess.DEVNULL)
run(os.path.join(sc, 'e2e_reconstruction.py'), PD, OUT)
run(os.path.join(sc, 'aggregation_check.py'), PD, OUT)
run(os.path.join(sc, 'descriptives_geo_rank.py'), PD, OUT)
run(os.path.join(sc, 'vintage_revisions.py'), VD, OUT)
run(os.path.join(sc, 'claims_register_postprocess.py'), os.path.join(ROOT, 'claims', 'claims_input_original.csv'), os.path.join(OUT, 'project_claims_audit.csv'))
# figures read results/ and raw_vintages/ under the package root; only run for the default output location
if os.path.abspath(a.out) == os.path.join(ROOT, 'results'):
    run(os.path.join(sc, 'make_figures.py'), ROOT, FIG)
    run(os.path.join(sc, 'build_xlsx.py'), ROOT)
json.dump({'run_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'python': platform.python_version(),
           'mode': 'online' if a.online else 'offline', 'pinned_commit': '2dd02f746cb4e2159281adc74d6865f948e90ce1',
           'all_input_hashes_verified': True, 'n_inputs': len(rows)}, open(os.path.join(OUT, 'run_manifest.json'), 'w'), indent=1)
print('Done. Results in', OUT)
