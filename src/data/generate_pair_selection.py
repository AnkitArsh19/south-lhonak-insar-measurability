import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
OUT_CSV = ROOT / "experiments" / "reports" / "sentinel1_pair_selection.csv"

pairs = [
    {
        "pair_id": "PAIR_01_DESC_PRE_EVENT",
        "track": "48",
        "direction": "DESCENDING",
        "ref_date": "2023-09-16",
        "sec_date": "2023-09-28",
        "temporal_baseline_days": 12,
        "ref_granule": "S1A_IW_SLC__1SDV_20230916T000326_20230916T000353_050345_060FB7_3B45",
        "sec_granule": "S1A_IW_SLC__1SDV_20230928T000326_20230928T000353_050520_0615B5_8E7B",
        "scientific_purpose": "Immediate pre-event window (5 days prior to breach). Tests whether sudden acceleration is visible right before collapse.",
        "expected_coherence": "Medium (late monsoon wet surface conditions)",
        "priority": "HIGH (Pilot #1)"
    },
    {
        "pair_id": "PAIR_02_ASC_PRE_EVENT",
        "track": "12",
        "direction": "ASCENDING",
        "ref_date": "2023-09-13",
        "sec_date": "2023-09-25",
        "temporal_baseline_days": 12,
        "ref_granule": "S1A_IW_SLC__1SDV_20230913T121407_20230913T121434_050309_060E91_5572",
        "sec_granule": "S1A_IW_SLC__1SDV_20230925T121408_20230925T121435_050484_061484_C0C9",
        "scientific_purpose": "Opposite viewing geometry (Ascending look ENE, 8 days prior to breach). Resolves geometric sensitivity ambiguity.",
        "expected_coherence": "Medium",
        "priority": "HIGH (Pilot #2)"
    },
    {
        "pair_id": "PAIR_03_DESC_DRY_BENCHMARK",
        "track": "48",
        "direction": "DESCENDING",
        "ref_date": "2023-05-07",
        "sec_date": "2023-05-19",
        "temporal_baseline_days": 12,
        "ref_granule": "S1A_IW_SLC__1SDV_20230507T000319_20230507T000346_048420_05D2FE_179A",
        "sec_granule": "S1A_IW_SLC__1SDV_20230519T000320_20230519T000347_048595_05D83E_878D",
        "scientific_purpose": "Pre-monsoon dry season benchmark. Highest expected coherence across moraine debris; determines if slope is measurable under ideal conditions.",
        "expected_coherence": "High (>0.50)",
        "priority": "HIGH (Pilot #3)"
    },
    {
        "pair_id": "PAIR_04_ASC_DRY_BENCHMARK",
        "track": "12",
        "direction": "ASCENDING",
        "ref_date": "2023-05-04",
        "sec_date": "2023-05-16",
        "temporal_baseline_days": 12,
        "ref_granule": "S1A_IW_SLC__1SDV_20230504T121400_20230504T121427_048384_05D1CD_4858",
        "sec_granule": "S1A_IW_SLC__1SDV_20230516T121401_20230516T121428_048559_05D73A_D465",
        "scientific_purpose": "Ascending pre-monsoon dry season benchmark. Tests geometric visibility and provides cross-heading comparison with Pair 03.",
        "expected_coherence": "High (>0.50)",
        "priority": "HIGH (Pilot #4)"
    },
    {
        "pair_id": "PAIR_05_DESC_POST_EVENT",
        "track": "48",
        "direction": "DESCENDING",
        "ref_date": "2023-09-28",
        "sec_date": "2023-10-10",
        "temporal_baseline_days": 12,
        "ref_granule": "S1A_IW_SLC__1SDV_20230928T000326_20230928T000353_050520_0615B5_8E7B",
        "sec_granule": "S1A_IW_SLC__1SDV_20231010T000326 (Post-event)",
        "scientific_purpose": "Co-event pair spanning the 3-4 October collapse. Validates that catastrophic moraine breach causes complete decorrelation / phase disruption over the scarp.",
        "expected_coherence": "Decorrelated over scarp, coherent on bedrock CTRL-01",
        "priority": "MEDIUM (Co-event Validation)"
    }
]

OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
with open(OUT_CSV, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=list(pairs[0].keys()))
    writer.writeheader()
    writer.writerows(pairs)

print(f"Saved pair selection to: {OUT_CSV}")
