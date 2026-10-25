import csv
from datetime import datetime

with open("data/catalogs/sentinel1_south_lhonak_catalog.csv", "r", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

by_path = {}
for r in rows:
    p = r["Path Number"]
    by_path.setdefault(p, []).append(r)

for p, items in by_path.items():
    direction = items[0]["Ascending or Descending?"]
    print(f"\n==========================================")
    print(f"Track {p} ({direction}) — Total: {len(items)} scenes")
    print(f"==========================================")
    
    # Sort chronologically
    sorted_items = sorted(items, key=lambda x: x["Acquisition Date"])
    print(f"Time span: {sorted_items[0]['Acquisition Date'][:10]} to {sorted_items[-1]['Acquisition Date'][:10]}")
    
    # Check 2023 pre-event acquisitions (prior to 04 Oct 2023)
    pre_2023 = [r for r in sorted_items if r["Acquisition Date"].startswith("2023")]
    print(f"\n2023 Pre-event scenes ({len(pre_2023)} total):")
    for s in pre_2023:
        dt = s["Acquisition Date"][:10]
        granule = s["Granule Name"]
        size_mb = float(s["Size (MB)"])
        print(f"  {dt} | Orbit: {s['Orbit']} | Size: {size_mb:.0f} MB | {granule}")
