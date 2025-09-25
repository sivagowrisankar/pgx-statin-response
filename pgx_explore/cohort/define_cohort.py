# src/cohort/define_cohort.py
import argparse, json, os
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

def define_cohort_demo(paths_cfg, cohort_cfg):
    """
    Demo: fabricate a simple 'exposure' event and LDL labs so pipeline runs.
    Expect:
      data_demo/interim/clinical_demo.csv  (id, age, sex, bmi)
      data_demo/interim/labs_demo.csv      (id, date, ldl)
      data_demo/interim/meds_demo.csv      (id, date, drug, dose)
    """
    clinical = pd.read_csv(paths_cfg["demo_interim_dir"] + "/clinical_demo.csv")
    labs = pd.read_csv(paths_cfg["demo_interim_dir"] + "/labs_demo.csv")
    meds = pd.read_csv(paths_cfg["demo_interim_dir"] + "/meds_demo.csv")

    labs["date"] = to_dt(labs["date"])
    meds["date"] = to_dt(meds["date"])

    # choose first statin exposure per person
    statins = meds[meds["drug"].str.lower().str.contains("statin|atorvastatin|rosuvastatin|simvastatin")]
    first_rx = statins.sort_values(["id", "date"]).groupby("id", as_index=False).first()
    first_rx = first_rx.rename(columns={"date": "first_rx_date"})

    cohort = clinical.merge(first_rx[["id", "first_rx_date", "drug", "dose"]], on="id", how="inner")

    # keep adults and drop missing essentials
    cohort = cohort[(cohort["age"] >= cohort_cfg["min_age"]) & cohort["first_rx_date"].notna()]
    out_path = os.path.join(paths_cfg["outputs_dir"], "cohort")
    os.makedirs(out_path, exist_ok=True)
    cohort.to_csv(os.path.join(out_path, "cohort.csv"), index=False)
    print(f"[define_cohort] Wrote {len(cohort)} rows -> {out_path}/cohort.csv")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="config/cohort.yml")
    ap.add_argument("--paths", default="config/paths.yml")
    ap.add_argument("--mode", default="demo", choices=["demo","ukb"])
    args = ap.parse_args()
    paths_cfg = load_yaml_like(args.paths)
    cohort_cfg = load_yaml_like(args.config)
    if args.mode == "demo":
        define_cohort_demo(paths_cfg, cohort_cfg)
    else:
        raise NotImplementedError("UKB reader lives in src/io/ukb_rap_reader.py (RAP only).")

if __name__ == "__main__":
    main()
