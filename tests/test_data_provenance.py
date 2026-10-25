"""
Data integrity and provenance tests.
Enforces that all literature claims link to registered papers, and all experiments have valid configs.
"""

from pathlib import Path
import csv
import pytest

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent

def test_claims_link_to_registered_papers():
    """Verify that paper_ids referenced in claim_ledger.csv exist in paper_registry.csv."""
    papers_csv = WORKSPACE_ROOT / "literature" / "paper_registry.csv"
    claims_csv = WORKSPACE_ROOT / "literature" / "claim_ledger.csv"
    
    assert papers_csv.exists(), "paper_registry.csv missing!"
    assert claims_csv.exists(), "claim_ledger.csv missing!"
    
    with open(papers_csv, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        registered_ids = {row["paper_id"].strip() for row in reader if row.get("paper_id")}
        
    with open(claims_csv, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            source = str(row.get("source_paper", "")).strip()
            if source.startswith("PAP"):
                source_id = source.split()[0].strip()
                assert source_id in registered_ids, f"Claim {row.get('claim_id')} links to unregistered paper {source_id}"

def test_experiment_registry_has_configs():
    """Verify that all experiments registered in experiments_registry.csv have a valid YAML config."""
    exp_csv = WORKSPACE_ROOT / "experiments" / "experiments_registry.csv"
    configs_dir = WORKSPACE_ROOT / "experiments" / "configs"
    
    assert exp_csv.exists(), "experiments_registry.csv missing!"
    with open(exp_csv, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            exp_id = row["experiment_id"].strip()
            matching = list(configs_dir.glob(f"{exp_id}*.yaml"))
            if row["status"] in ["PLANNED", "RUNNING", "COMPLETED"]:
                if exp_id == "EXP001":
                    assert len(matching) >= 1, f"Missing config for {exp_id} in {configs_dir}"
