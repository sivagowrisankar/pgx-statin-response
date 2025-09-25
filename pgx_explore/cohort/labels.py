# src/cohort/labels.py
import argparse, os
import pandas as pd
from datetime import timedelta

def load_yaml_like(path):
    import yaml
    with open(path, "r") as f:
        return yaml.safe_load(f)

def to_dt(s):
    dt = pd.to_datetime(s, errors="coerce", utc=True)
    if hasattr(dt, 'dt') and getattr(dt.dt, 'tz', None) is not None:
        return dt.dt.tz_convert(None)
    elif getattr(dt, 'tz', None) is not None:
        return dt.tz_convert(None)
    return dt

def add_labels_demo(paths_cfg, cohort_cfg):
    cohort = pd.read_csv(paths_cfg["outputs_dir"] + "/cohort/cohort.csv")
    labs = pd.read_csv(paths_cfg["demo_interim_dir"] + "/labs_demo.csv")
    labs["date"] = to_dt(labs["date"])

    base_lo, base_hi = cohort_cfg["baseline_window_days"]
    foll_lo, foll_hi = cohort_cfg["followup_window_days"]

    # For each id, pick baseline LDL within window relative to first_rx_date, then follow-up LDL
    cohort["first_rx_date"] = to_dt(cohort["first_rx_date"])

    base_ldl = []
    follow_ldl = []
    for _, r in cohort.iterrows():
        pid = r["id"]
        rx = r["first_rx_date"]
        sub = labs[labs["id"] == pid]
        base = sub[(sub["date"] >= rx + pd.Timedelta(days=base_lo)) &
                   (sub["date"] <= rx + pd.Timedelta(days=base_hi))].sort_values("date")
        foll = sub[(sub["date"] >= rx + pd.Timedelta(days=foll_lo)) &
                   (sub["date"] <= rx + pd.Timedelta(days=foll_hi))].sort_values("date")
        base_ldl.append(base["ldl"].iloc[0] if len(base) else None)
        follow_ldl.append(foll["ldl"].iloc[0] if len(foll) else None)

    cohort["baseline_ldl"] = base_ldl
    cohort["followup_ldl"] = follow_ldl
    cohort = cohort.dropna(subset=["baseline_ldl", "followup_ldl"]).copy()
    cohort["pct_ldl_change"] = 100.0 * (cohort["followup_ldl"] - cohort["baseline_ldl"]) / cohort["baseline_ldl"]

    # Optional binary label: non-response <20% reduction vs response >40% reduction (demo thresholds)
    cohort["is_responder"] = (cohort["pct_ldl_change"] <= -40).astype(int)
    cohort["is_nonresponder"] = (cohort["pct_ldl_change"] >= -20).astype(int)

    out_dir = os.path.join(paths_cfg["outputs_dir"], "labels")
    os.makedirs(out_dir, exist_ok=True)
    cohort.to_csv(os.path.join(out_dir, "cohort_with_labels.csv"), index=False)
    print(f"[labels] Wrote {len(cohort)} rows with labels -> {out_dir}/cohort_with_labels.csv")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--label", default="pct_ldl_change")
    ap.add_argument("--config", default="config/cohort.yml")
    ap.add_argument("--paths", default="config/paths.yml")
    ap.add_argument("--mode", default="demo", choices=["demo","ukb"])
    args = ap.parse_args()

    paths_cfg = load_yaml_like(args.paths)
    cohort_cfg = load_yaml_like(args.config)
    if args.mode == "demo":
        add_labels_demo(paths_cfg, cohort_cfg)
    else:
        raise NotImplementedError("Implement UKB RAP variant in io/ukb_rap_reader.py.")

if __name__ == "__main__":
    main()
